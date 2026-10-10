from fastapi.testclient import TestClient

from src.nexora_hq.app import create_app
from src.nexora_hq.auth import hash_password


def test_production_disables_interactive_api_docs(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXORA_ENV", "production")
    monkeypatch.setenv("NEXORA_ADMIN_PASSWORD_HASH", hash_password("production-test-password"))
    monkeypatch.setenv("NEXORA_SESSION_SECRET", "test-secret-that-is-long-enough-for-session-signing")
    client = TestClient(create_app(tmp_path / "production.sqlite3"))
    with client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404
