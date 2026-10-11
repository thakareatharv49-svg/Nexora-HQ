"""Validated environment configuration for Nexora HQ."""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Settings:
    environment: str
    database_path: str
    admin_password_hash: str | None
    session_secret: str | None
    ai_software_developer_url: str | None
    ai_software_developer_token: str | None

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        values = os.environ if environ is None else environ
        environment = values.get("NEXORA_ENV", "development").strip().lower()
        if environment not in {"development", "test", "production"}:
            raise ValueError("NEXORA_ENV must be development, test, or production")

        database_path = values.get("NEXORA_DB_PATH", "data/nexora-hq.sqlite3").strip()
        if not database_path:
            raise ValueError("NEXORA_DB_PATH must not be empty")
        if environment == "production" and database_path == ":memory:":
            raise ValueError("Production must use persistent database storage")

        admin_password_hash = values.get("NEXORA_ADMIN_PASSWORD_HASH", "").strip() or None
        session_secret = values.get("NEXORA_SESSION_SECRET", "").strip() or None
        if bool(admin_password_hash) != bool(session_secret):
            raise ValueError("NEXORA_ADMIN_PASSWORD_HASH and NEXORA_SESSION_SECRET must be configured together")
        if environment == "production" and not admin_password_hash:
            raise ValueError("Production requires admin password hash and session secret")
        if admin_password_hash and not admin_password_hash.startswith("scrypt$"):
            raise ValueError("NEXORA_ADMIN_PASSWORD_HASH must be a scrypt password hash")
        if session_secret and len(session_secret) < 32:
            raise ValueError("NEXORA_SESSION_SECRET must contain at least 32 characters")

        developer_url = values.get("NEXORA_AI_SOFTWARE_DEVELOPER_URL", "").strip().rstrip("/") or None
        developer_token = values.get("NEXORA_AI_SOFTWARE_DEVELOPER_TOKEN", "").strip() or None
        if bool(developer_url) != bool(developer_token):
            raise ValueError(
                "NEXORA_AI_SOFTWARE_DEVELOPER_URL and NEXORA_AI_SOFTWARE_DEVELOPER_TOKEN must be configured together"
            )
        if developer_url:
            parsed = urlsplit(developer_url)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or parsed.username
                or parsed.password
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("NEXORA_AI_SOFTWARE_DEVELOPER_URL must be a base HTTP(S) URL without credentials or query")
            if environment == "production" and parsed.scheme != "https":
                raise ValueError("Production venture integrations must use HTTPS")

        return cls(
            environment=environment,
            database_path=database_path,
            admin_password_hash=admin_password_hash,
            session_secret=session_secret,
            ai_software_developer_url=developer_url,
            ai_software_developer_token=developer_token,
        )
