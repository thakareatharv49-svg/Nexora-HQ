"""Validated environment configuration for Nexora HQ."""
from __future__ import annotations

import os
from dataclasses import dataclass
from collections.abc import Mapping


@dataclass(frozen=True)
class Settings:
    environment: str
    database_path: str

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
        return cls(environment=environment, database_path=database_path)
