from fastapi.testclient import TestClient

from src.nexora_hq.app import create_app


def test_update_venture_changes_metadata_and_records_activity(tmp_path):
    with TestClient(create_app(tmp_path / "registry.sqlite3")) as client:
        created = client.post("/api/ventures", json={"name": "Research Studio", "category": "Research", "description": "Explores new product ideas for Nexora.", "repository_url": "https://github.com/example/research-studio"})
        venture_id = created.json()["id"]
        updated = client.patch(f"/api/ventures/{venture_id}", json={"description": "Tracks reviewed product research for Nexora.", "repository_url": None})
        activity = client.get("/api/activity?limit=10")

    assert created.status_code == 201
    assert updated.status_code == 200
    assert updated.json()["description"] == "Tracks reviewed product research for Nexora."
    assert updated.json()["repository_url"] is None
    assert updated.json()["connection_state"] == "not_connected"
    assert any(item["title"] == "Venture updated: Research Studio" for item in activity.json()["items"])


def test_update_venture_rejects_duplicate_names_and_missing_ids(tmp_path):
    with TestClient(create_app(tmp_path / "registry.sqlite3")) as client:
        first = client.post("/api/ventures", json={"name": "Research Studio", "category": "Research", "description": "Explores new product ideas for Nexora."})
        second = client.post("/api/ventures", json={"name": "Product Lab", "category": "Research", "description": "Explores new product ideas for Nexora."})
        duplicate = client.patch("/api/ventures/" + second.json()["id"], json={"name": "research studio"})
        missing = client.patch("/api/ventures/not-found", json={"name": "New Venture"})

    assert first.status_code == 201
    assert second.status_code == 201
    assert duplicate.status_code == 409
    assert missing.status_code == 404
