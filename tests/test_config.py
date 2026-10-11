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



def test_venture_adapter_requires_url_and_service_token_together():
    with pytest.raises(ValueError, match="must be configured together"):
        Settings.from_env({"NEXORA_AI_SOFTWARE_DEVELOPER_URL": "http://127.0.0.1:8011"})


def test_venture_adapter_rejects_credentials_in_url():
    with pytest.raises(ValueError, match="base HTTP"):
        Settings.from_env({
            "NEXORA_AI_SOFTWARE_DEVELOPER_URL": "https://user:pass@example.test",
            "NEXORA_AI_SOFTWARE_DEVELOPER_TOKEN": "service-token",
        })


def test_production_venture_adapter_requires_https():
    with pytest.raises(ValueError, match="must use HTTPS"):
        Settings.from_env({
            "NEXORA_ENV": "production",
            "NEXORA_ADMIN_PASSWORD_HASH": "scrypt$placeholder",
            "NEXORA_SESSION_SECRET": "s" * 40,
            "NEXORA_AI_SOFTWARE_DEVELOPER_URL": "http://developer.internal",
            "NEXORA_AI_SOFTWARE_DEVELOPER_TOKEN": "service-token",
        })


def test_valid_venture_adapter_configuration_is_normalized():
    settings = Settings.from_env({
        "NEXORA_AI_SOFTWARE_DEVELOPER_URL": "http://127.0.0.1:8011/",
        "NEXORA_AI_SOFTWARE_DEVELOPER_TOKEN": "service-token",
    })
    assert settings.ai_software_developer_url == "http://127.0.0.1:8011"
    assert settings.ai_software_developer_token == "service-token"
