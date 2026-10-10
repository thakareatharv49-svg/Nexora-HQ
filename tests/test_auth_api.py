from fastapi.testclient import TestClient

from src.nexora_hq.app import create_app
from src.nexora_hq.auth import hash_password


def test_admin_login_protects_registry_and_activity(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXORA_ENV", "production")
    monkeypatch.setenv("NEXORA_ADMIN_PASSWORD_HASH", hash_password("correct password"))
    monkeypatch.setenv("NEXORA_SESSION_SECRET", "test-secret-that-is-long-enough-for-session-signing")
    client = TestClient(create_app(tmp_path / "auth.sqlite3"), base_url="https://testserver")

    with client:
        status = client.get("/api/auth/status")
        assert status.json() == {"auth_required": True, "authenticated": False}
        assert client.get("/api/ventures").status_code == 401
        assert client.get("/api/activity").status_code == 401
        assert client.post("/api/auth/login", json={"password": "incorrect"}).status_code == 401

        login = client.post("/api/auth/login", json={"password": "correct password"})
        assert login.status_code == 200
        assert login.headers["cache-control"] == "no-store"
        assert login.json() == {"auth_required": True, "authenticated": True}
        set_cookie = login.headers["set-cookie"].lower()
        assert "httponly" in set_cookie
        assert "secure" in set_cookie
        assert "samesite=strict" in set_cookie
        assert client.get("/api/ventures").status_code == 200
        activity = client.get("/api/activity")
        assert activity.status_code == 200
        assert any(item["title"] == "Administrator signed in" for item in activity.json()["items"])

        logout = client.post("/api/auth/logout")
        assert logout.status_code == 200
        assert client.get("/api/ventures").status_code == 401

        assert client.post("/api/auth/login", json={"password": "correct password"}).status_code == 200
        audit = client.get("/api/activity").json()["items"]
        titles = [item["title"] for item in audit]
        assert "Administrator signed out" in titles
        assert "Administrator signed in" in titles
