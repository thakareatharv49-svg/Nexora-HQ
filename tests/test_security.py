from fastapi.testclient import TestClient

from src.nexora_hq.app import create_app


def test_production_disables_interactive_api_docs(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXORA_ENV", "production")
    client = TestClient(create_app(tmp_path / "production.sqlite3"))
    with client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404
