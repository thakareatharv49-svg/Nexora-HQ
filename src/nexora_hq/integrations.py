"""Read-only adapters for external Nexora ventures."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

import httpx


VentureStatus = Literal["operational", "degraded", "down", "unknown"]
IntegrationState = Literal["not_configured", "connected", "stale", "error"]


class DeveloperStatusPayload(BaseModel):
    """Narrow, explicit contract expected from the AI Software Developer."""

    model_config = ConfigDict(extra="ignore", strict=True)

    service: Literal["ai-software-developer"]
    status: VentureStatus
    active_missions: int = Field(ge=0)
    queued_missions: int = Field(ge=0)
    completed_missions: int = Field(ge=0)
    blocked_missions: int = Field(ge=0)
    updated_at: datetime

    @field_validator("updated_at")
    @classmethod
    def require_timezone_aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("updated_at must include a timezone")
        return value


class VentureIntegration(BaseModel):
    venture_id: str = "ai-software-developer"
    display_name: str = "AI Software Developer"
    status: VentureStatus = "unknown"
    integration_state: IntegrationState
    checked_at: datetime
    last_success_at: datetime | None = None
    source_updated_at: datetime | None = None
    source: str | None = None
    message: str
    active_missions: int | None = None
    queued_missions: int | None = None
    completed_missions: int | None = None
    blocked_missions: int | None = None


class ReadOnlyDeveloperAdapter:
    """Query a configured, dedicated status endpoint without mutating the venture."""

    def __init__(
        self,
        base_url: str | None,
        token: str | None,
        *,
        timeout_seconds: float = 2.0,
        stale_after_seconds: int = 120,
        client_factory=httpx.AsyncClient,
    ) -> None:
        self.base_url = (base_url or "").strip().rstrip("/") or None
        self.token = (token or "").strip() or None
        self.timeout_seconds = timeout_seconds
        self.stale_after_seconds = stale_after_seconds
        self.client_factory = client_factory
        self._last_success_at: datetime | None = None
        self._last_source_updated_at: datetime | None = None

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    def _source(self) -> str | None:
        if not self.base_url:
            return None
        parsed = urlsplit(self.base_url)
        return f"{parsed.scheme}://{parsed.netloc}"

    async def read_status(self) -> VentureIntegration:
        now = self._now()
        if not self.base_url or not self.token:
            return VentureIntegration(
                integration_state="not_configured",
                checked_at=now,
                source=None,
                message="Read-only venture status adapter is not configured.",
            )

        parsed = urlsplit(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
            return VentureIntegration(
                integration_state="error",
                checked_at=now,
                source=None,
                message="Configured venture URL is invalid.",
            )

        try:
            async with self.client_factory(
                timeout=self.timeout_seconds,
                follow_redirects=False,
                headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"},
            ) as client:
                response = await client.get(f"{self.base_url}/api/hq/status")
            if response.status_code != 200:
                raise ValueError("status endpoint did not return HTTP 200")
            payload = DeveloperStatusPayload.model_validate_json(response.content)
        except (httpx.HTTPError, ValueError, ValidationError, TypeError):
            last_success = self._last_success_at
            stale = last_success is not None and (
                now - last_success
            ).total_seconds() > self.stale_after_seconds
            return VentureIntegration(
                integration_state="stale" if stale else "error",
                checked_at=now,
                last_success_at=last_success,
                source_updated_at=self._last_source_updated_at,
                source=self._source(),
                message=(
                    "Venture status is stale; the last successful check is too old."
                    if stale
                    else "Could not verify venture status from its dedicated status endpoint."
                ),
            )

        self._last_success_at = now
        self._last_source_updated_at = payload.updated_at
        source_age = (now - payload.updated_at).total_seconds()
        source_is_stale = source_age > self.stale_after_seconds or source_age < -60
        return VentureIntegration(
            status=payload.status,
            integration_state="stale" if source_is_stale else "connected",
            checked_at=now,
            last_success_at=now,
            source_updated_at=payload.updated_at,
            source=self._source(),
            message=(
                "The endpoint responded, but its status snapshot is stale."
                if source_is_stale
                else "Read-only venture status received from the configured endpoint."
            ),
            active_missions=payload.active_missions,
            queued_missions=payload.queued_missions,
            completed_missions=payload.completed_missions,
            blocked_missions=payload.blocked_missions,
        )
