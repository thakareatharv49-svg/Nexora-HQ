from fastapi.testclient import TestClient

from src.nexora_hq.app import create_app


def test_create_venture_persists_record_and_activity(tmp_path):
    with TestClient(create_app(tmp_path / "registry.sqlite3")) as client:
        response = client.post(
            "/api/ventures",
            json={
                "name": "Research Studio",
                "category": "Research",
                "description": "Explores new product ideas for Nexora.",
                "repository_url": "https://github.com/example/research-studio",
            },
        )
        registry = client.get("/api/ventures")
        activity = client.get("/api/activity?limit=10")

    assert response.status_code == 201
    created = response.json()
    assert created["id"]
    assert created["name"] == "Research Studio"
    assert created["connection_state"] == "not_connected"
    assert created["repository_url"] == "https://github.com/example/research-studio"
    assert registry.status_code == 200
    assert registry.json()["count"] == 3
    assert any(item["id"] == created["id"] for item in registry.json()["items"])
    assert any(
        item["title"] == "Venture registered: Research Studio"
        for item in activity.json()["items"]
    )


def test_create_venture_rejects_duplicate_names_case_insensitively(tmp_path):
    with TestClient(create_app(tmp_path / "registry.sqlite3")) as client:
        payload = {
            "name": "Research Studio",
            "category": "Research",
            "description": "Explores new product ideas for Nexora.",
        }
        first = client.post("/api/ventures", json=payload)
        duplicate = client.post(
            "/api/ventures", json={**payload, "name": "research studio"}
        )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "A venture with this name already exists"


def test_create_venture_validates_fields_and_repository_scheme(tmp_path):
    with TestClient(create_app(tmp_path / "registry.sqlite3")) as client:
        short_description = client.post(
            "/api/ventures",
            json={
                "name": "Test Venture",
                "category": "Research",
                "description": "Short",
            },
        )
        unsafe_repository = client.post(
            "/api/ventures",
            json={
                "name": "Safe Venture",
                "category": "Research",
                "description": "A sufficiently detailed venture description.",
                "repository_url": "javascript:alert(1)",
            },
        )

    assert short_description.status_code == 422
    assert unsafe_repository.status_code == 422
