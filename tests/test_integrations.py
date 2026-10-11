from datetime import UTC, datetime, timedelta

import httpx
import pytest

from src.nexora_hq.integrations import ReadOnlyDeveloperAdapter


def make_adapter(handler):
    def client_factory(**kwargs):
        return httpx.AsyncClient(transport=httpx.MockTransport(handler), **kwargs)

    return ReadOnlyDeveloperAdapter(
        "http://developer.test",
        "test-service-token",
        client_factory=client_factory,
    )


def valid_payload(**overrides):
    payload = {
        "service": "ai-software-developer",
        "status": "operational",
        "active_missions": 1,
        "queued_missions": 3,
        "completed_missions": 12,
        "blocked_missions": 0,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_unconfigured_adapter_is_explicit_and_does_not_make_a_request():
    result = await ReadOnlyDeveloperAdapter(None, None).read_status()

    assert result.integration_state == "not_configured"
    assert result.status == "unknown"
    assert result.active_missions is None
    assert result.last_success_at is None
    assert result.source is None


@pytest.mark.asyncio
async def test_adapter_normalizes_explicit_status_and_sends_service_token():
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/api/hq/status"
        assert request.headers["authorization"] == "Bearer test-service-token"
        return httpx.Response(200, json=valid_payload())

    result = await make_adapter(handler).read_status()

    assert result.integration_state == "connected"
    assert result.status == "operational"
    assert result.active_missions == 1
    assert result.queued_missions == 3
    assert result.completed_missions == 12
    assert result.blocked_missions == 0
    assert result.last_success_at == result.checked_at
    assert result.source == "http://developer.test"
    assert "test-service-token" not in result.model_dump_json()


@pytest.mark.asyncio
async def test_http_success_without_valid_explicit_status_is_not_treated_as_healthy():
    def handler(_request):
        return httpx.Response(200, json={"service": "ai-software-developer"})

    result = await make_adapter(handler).read_status()

    assert result.integration_state == "error"
    assert result.status == "unknown"
    assert result.active_missions is None


@pytest.mark.asyncio
async def test_non_200_response_is_an_error_without_leaking_upstream_body():
    def handler(_request):
        return httpx.Response(503, text="private upstream diagnostic")

    result = await make_adapter(handler).read_status()

    assert result.integration_state == "error"
    assert result.status == "unknown"
    assert "private upstream diagnostic" not in result.model_dump_json()


@pytest.mark.asyncio
async def test_failed_check_after_old_success_reports_stale_data():
    def handler(_request):
        return httpx.Response(200, json=valid_payload())

    adapter = make_adapter(handler)
    adapter._last_success_at = datetime.now(UTC) - timedelta(minutes=10)

    def failing_factory(**kwargs):
        return httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda _request: httpx.Response(503, text="upstream unavailable")
            ),
            **kwargs,
        )

    adapter.client_factory = failing_factory
    result = await adapter.read_status()

    assert result.integration_state == "stale"
    assert result.last_success_at is not None
    assert "stale" in result.message.lower()
