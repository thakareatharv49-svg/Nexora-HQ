import asyncio
from datetime import UTC, datetime, timedelta

import httpx

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


def test_unconfigured_adapter_is_explicit_and_does_not_make_a_request():
    result = asyncio.run(ReadOnlyDeveloperAdapter(None, None).read_status())

    assert result.integration_state == "not_configured"
    assert result.status == "unknown"
    assert result.active_missions is None
    assert result.last_success_at is None
    assert result.source is None


def test_adapter_normalizes_explicit_status_and_sends_service_token():
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/api/hq/status"
        assert request.headers["authorization"] == "Bearer test-service-token"
        return httpx.Response(200, json=valid_payload())

    result = asyncio.run(make_adapter(handler).read_status())

    assert result.integration_state == "connected"
    assert result.status == "operational"
    assert result.active_missions == 1
    assert result.queued_missions == 3
    assert result.completed_missions == 12
    assert result.blocked_missions == 0
    assert result.last_success_at == result.checked_at
    assert result.source == "http://developer.test"
    assert "test-service-token" not in result.model_dump_json()


def test_http_success_without_valid_explicit_status_is_not_treated_as_healthy():
    def handler(_request):
        return httpx.Response(200, json={"service": "ai-software-developer"})

    result = asyncio.run(make_adapter(handler).read_status())

    assert result.integration_state == "error"
    assert result.status == "unknown"
    assert result.active_missions is None


def test_non_200_response_is_an_error_without_leaking_upstream_body():
    def handler(_request):
        return httpx.Response(503, text="private upstream diagnostic")

    result = asyncio.run(make_adapter(handler).read_status())

    assert result.integration_state == "error"
    assert result.status == "unknown"
    assert "private upstream diagnostic" not in result.model_dump_json()


def test_failed_check_after_old_success_reports_stale_data():
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
    result = asyncio.run(adapter.read_status())

    assert result.integration_state == "stale"
    assert result.last_success_at is not None
    assert "stale" in result.message.lower()



def test_old_source_snapshot_is_marked_stale_even_when_endpoint_responds():
    old_timestamp = (datetime.now(UTC) - timedelta(minutes=10)).isoformat()

    def handler(_request):
        return httpx.Response(200, json=valid_payload(updated_at=old_timestamp))

    result = asyncio.run(make_adapter(handler).read_status())

    assert result.integration_state == "stale"
    assert result.status == "operational"
    assert result.active_missions == 1
    assert result.source_updated_at is not None
    assert "snapshot is stale" in result.message.lower()
