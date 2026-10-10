from fastapi.testclient import TestClient

from src.nexora_hq.app import create_app


def make_client(tmp_path):
    application = create_app(tmp_path / "test.sqlite3")
    return TestClient(application)


def test_health_endpoint_marks_integrations_unconfigured(tmp_path):
    with make_client(tmp_path) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "nexora-hq",
        "database": "ready",
        "venture_integrations": "not_configured",
    }
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_venture_registry_is_persisted_and_explicitly_disconnected(tmp_path):
    database_path = tmp_path / "registry.sqlite3"
    first = TestClient(create_app(database_path))
    with first:
        response = first.get("/api/ventures")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert {item["name"] for item in payload["items"]} == {
        "AI Software Developer",
        "AI Open Source Contributor",
    }
    assert all(item["connection_state"] == "not_connected" for item in payload["items"])

    second = TestClient(create_app(database_path))
    with second:
        again = second.get("/api/ventures")
    assert again.status_code == 200
    assert again.json()["count"] == 2


def test_activity_limit_is_validated(tmp_path):
    with make_client(tmp_path) as client:
        response = client.get("/api/activity?limit=2")
        invalid = client.get("/api/activity?limit=0")
    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert len(response.json()["items"]) == 2
    assert invalid.status_code == 422


def test_dashboard_is_served_by_backend_when_static_assets_exist(tmp_path):
    with make_client(tmp_path) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "Nexora HQ" in response.text

def test_health_reports_degraded_when_database_is_unavailable(tmp_path):
    def unavailable():
        return False

    with make_client(tmp_path) as client:
        client.app.state.database.ping = unavailable
        response = client.get("/api/health")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["database"] == "unavailable"
