from fastapi.testclient import TestClient

from src.nexora_hq.app import create_app
from src.nexora_hq.auth import hash_password
from src.nexora_hq.database import HQDatabase


def make_authenticated_client(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXORA_ENV", "test")
    monkeypatch.setenv(
        "NEXORA_ADMIN_PASSWORD_HASH", hash_password("correct-test-password")
    )
    monkeypatch.setenv("NEXORA_SESSION_SECRET", "test-session-secret-" + "x" * 40)
    return TestClient(create_app(tmp_path / "authenticated.sqlite3"))


def test_login_failures_lock_and_expire(tmp_path):
    database = HQDatabase(tmp_path / "login-attempts.sqlite3")
    database.initialize()

    assert database.record_login_failure(
        "client-key", now=100, failure_limit=3, window_seconds=60, lockout_seconds=30
    ) == 0
    assert database.record_login_failure(
        "client-key", now=101, failure_limit=3, window_seconds=60, lockout_seconds=30
    ) == 0
    assert database.record_login_failure(
        "client-key", now=102, failure_limit=3, window_seconds=60, lockout_seconds=30
    ) == 30
    assert database.login_lockout_seconds("client-key", now=110) == 22
    assert database.record_login_failure(
        "client-key", now=132, failure_limit=3, window_seconds=60, lockout_seconds=30
    ) == 0
    assert database.login_lockout_seconds("client-key", now=132) == 0
    database.close()


def test_login_endpoint_returns_429_after_five_bad_passwords(tmp_path, monkeypatch):
    with make_authenticated_client(tmp_path, monkeypatch) as client:
        for _ in range(4):
            response = client.post(
                "/api/auth/login", json={"password": "wrong-test-password"}
            )
            assert response.status_code == 401

        blocked = client.post(
            "/api/auth/login", json={"password": "wrong-test-password"}
        )
        assert blocked.status_code == 429
        assert int(blocked.headers["retry-after"]) > 0
        assert client.post(
            "/api/auth/login", json={"password": "correct-test-password"}
        ).status_code == 429
        assert client.get("/api/ventures").status_code == 401


def test_successful_login_clears_prior_failures(tmp_path, monkeypatch):
    with make_authenticated_client(tmp_path, monkeypatch) as client:
        for _ in range(4):
            assert client.post(
                "/api/auth/login", json={"password": "wrong-test-password"}
            ).status_code == 401

        successful = client.post(
            "/api/auth/login", json={"password": "correct-test-password"}
        )
        assert successful.status_code == 200
        assert successful.json()["authenticated"] is True
        assert "httponly" in successful.headers["set-cookie"].lower()

        next_failure = client.post(
            "/api/auth/login", json={"password": "wrong-test-password"}
        )
        assert next_failure.status_code == 401
