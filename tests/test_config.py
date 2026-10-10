import pytest

from src.nexora_hq.config import Settings


def test_defaults_are_safe_for_local_development():
    settings = Settings.from_env({})
    assert settings.environment == "development"
    assert settings.database_path == "data/nexora-hq.sqlite3"


def test_invalid_environment_is_rejected():
    with pytest.raises(ValueError, match="NEXORA_ENV"):
        Settings.from_env({"NEXORA_ENV": "production-ish"})


def test_empty_database_path_is_rejected():
    with pytest.raises(ValueError, match="NEXORA_DB_PATH"):
        Settings.from_env({"NEXORA_DB_PATH": "  "})


def test_production_cannot_use_in_memory_database():
    with pytest.raises(ValueError, match="persistent database"):
        Settings.from_env({"NEXORA_ENV": "production", "NEXORA_DB_PATH": ":memory:"})

def test_production_requires_admin_password_hash_and_session_secret():
    with pytest.raises(ValueError, match="Production requires admin password hash"):
        Settings.from_env({"NEXORA_ENV": "production"})
