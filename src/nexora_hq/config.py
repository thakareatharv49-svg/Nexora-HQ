"""Validated environment configuration for Nexora HQ."""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str
    database_path: str
    admin_password_hash: str | None
    session_secret: str | None

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        values = os.environ if environ is None else environ
        environment = values.get("NEXORA_ENV", "development").strip().lower()
        if environment not in {"development", "test", "production"}:
            raise ValueError("NEXORA_ENV must be development, test, or production")

        database_path = values.get("NEXORA_DB_PATH", "data/nexora-hq.sqlite3").strip()
        if not database_path:
            raise ValueError("NEXORA_DB_PATH must not be empty")
        if environment == "production" and database_path == ":memory:":
            raise ValueError("Production must use persistent database storage")

        admin_password_hash = values.get("NEXORA_ADMIN_PASSWORD_HASH", "").strip() or None
        session_secret = values.get("NEXORA_SESSION_SECRET", "").strip() or None
        if bool(admin_password_hash) != bool(session_secret):
            raise ValueError("NEXORA_ADMIN_PASSWORD_HASH and NEXORA_SESSION_SECRET must be configured together")
        if environment == "production" and not admin_password_hash:
            raise ValueError("Production requires admin password hash and session secret")
        if admin_password_hash and not admin_password_hash.startswith("scrypt$"):
            raise ValueError("NEXORA_ADMIN_PASSWORD_HASH must be a scrypt password hash")
        if session_secret and len(session_secret) < 32:
            raise ValueError("NEXORA_SESSION_SECRET must contain at least 32 characters")
        return cls(
            environment=environment,
            database_path=database_path,
            admin_password_hash=admin_password_hash,
            session_secret=session_secret,
        )
