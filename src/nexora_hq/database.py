"""SQLite persistence for HQ-owned registry and activity records."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_VENTURES = (
    {
        "id": "ai-software-developer",
        "name": "AI Software Developer",
        "category": "SOFTWARE ENGINEERING",
        "description": "Autonomous software factory for planning, building, testing, and publishing applications.",
        "repository_url": "https://github.com/thakareatharv49-svg/AI-Software-Company",
    },
    {
        "id": "ai-open-source-contributor",
        "name": "AI Open Source Contributor",
        "category": "OPEN SOURCE",
        "description": "A separate venture focused on discovering open-source work and supporting contributions.",
        "repository_url": None,
    },
)

DEFAULT_ACTIVITY = (
    ("SYSTEM", "HQ foundation created", "Dashboard shell and venture boundaries established."),
    ("REGISTRY", "Venture registry initialized", "Two independent ventures listed for future monitoring."),
    ("ARCHITECTURE", "Integration boundary documented", "Future adapters are restricted to venture-level read-only status."),
)


class HQDatabase:
    """Small SQLite repository with short-lived connections per operation."""

    def __init__(self, path: str | Path):
        raw_path = str(path)
        self.path = raw_path if raw_path == ":memory:" else str(Path(raw_path).expanduser())
        if self.path != ":memory:":
            Path(self.path).resolve().parent.mkdir(parents=True, exist_ok=True)
        self._memory_connection: sqlite3.Connection | None = None

    def _connect(self) -> sqlite3.Connection:
        if self.path == ":memory:":
            if self._memory_connection is None:
                self._memory_connection = sqlite3.connect(self.path, check_same_thread=False)
                self._memory_connection.row_factory = sqlite3.Row
            return self._memory_connection
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        connection = self._connect()
        owns_connection = self.path != ":memory:"
        try:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS ventures (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    repository_url TEXT,
                    connection_state TEXT NOT NULL DEFAULT 'not_connected',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'hq',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            count = connection.execute("SELECT COUNT(*) FROM ventures").fetchone()[0]
            if count == 0:
                connection.executemany(
                    "INSERT INTO ventures (id, name, category, description, repository_url) VALUES (:id, :name, :category, :description, :repository_url)",
                    DEFAULT_VENTURES,
                )
            activity_count = connection.execute("SELECT COUNT(*) FROM activity").fetchone()[0]
            if activity_count == 0:
                connection.executemany(
                    "INSERT INTO activity (kind, title, detail, source) VALUES (?, ?, ?, 'hq')",
                    DEFAULT_ACTIVITY,
                )
            connection.commit()
        finally:
            if owns_connection:
                connection.close()

    def list_ventures(self) -> list[dict[str, Any]]:
        connection = self._connect()
        owns_connection = self.path != ":memory:"
        try:
            rows = connection.execute(
                "SELECT id, name, category, description, repository_url, connection_state, created_at, updated_at FROM ventures ORDER BY name"
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            if owns_connection:
                connection.close()

    def list_activity(self, limit: int = 50) -> list[dict[str, Any]]:
        connection = self._connect()
        owns_connection = self.path != ":memory:"
        try:
            rows = connection.execute(
                "SELECT id, kind, title, detail, source, created_at FROM activity ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            if owns_connection:
                connection.close()

    def ping(self) -> bool:
        connection = self._connect()
        owns_connection = self.path != ":memory:"
        try:
            connection.execute("SELECT 1").fetchone()
            return True
        except sqlite3.Error:
            return False
        finally:
            if owns_connection:
                connection.close()

    def close(self) -> None:
        if self._memory_connection is not None:
            self._memory_connection.close()
            self._memory_connection = None
