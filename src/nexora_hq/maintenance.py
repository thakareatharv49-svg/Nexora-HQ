"""Offline-safe backup and restore helpers for the HQ SQLite database.

These utilities are deliberately separate from HTTP routes: database maintenance
must be an explicit operator action, never an unauthenticated web operation.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote


def _open_readonly(path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(path.resolve().as_posix(), safe='/')}?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def _validate_hq_database(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Database file does not exist: {path}")
    connection = _open_readonly(path)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError("Database integrity check failed")
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        if not {"ventures", "activity"}.issubset(tables):
            raise ValueError("File is not a valid Nexora HQ database")
    except sqlite3.DatabaseError as exc:
        raise ValueError("File is not a readable SQLite database") from exc
    finally:
        connection.close()


def _write_consistent_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(handle)
    temporary = Path(temporary_name)
    source_connection = None
    destination_connection = None
    try:
        source_connection = sqlite3.connect(source, timeout=5)
        destination_connection = sqlite3.connect(temporary, timeout=5)
        source_connection.backup(destination_connection)
        destination_connection.close()
        destination_connection = None
        source_connection.close()
        source_connection = None
        _validate_hq_database(temporary)
        os.replace(temporary, destination)
    finally:
        if destination_connection is not None:
            destination_connection.close()
        if source_connection is not None:
            source_connection.close()
        temporary.unlink(missing_ok=True)


def backup_database(source: str | Path, destination: str | Path) -> Path:
    """Create a consistent, integrity-checked backup and atomically publish it."""
    source_path = Path(source).expanduser().resolve()
    destination_path = Path(destination).expanduser().resolve()
    if source_path == destination_path:
        raise ValueError("Backup source and destination must be different files")
    _validate_hq_database(source_path)
    _write_consistent_copy(source_path, destination_path)
    return destination_path


def restore_database(
    backup: str | Path,
    destination: str | Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Restore a validated backup; preserve a rollback copy when replacing a DB.

    Stop the running HQ service before restoring. If a destination already
    exists, overwrite must be explicit and a timestamped pre-restore copy is
    created first.
    """
    backup_path = Path(backup).expanduser().resolve()
    destination_path = Path(destination).expanduser().resolve()
    if backup_path == destination_path:
        raise ValueError("Restore source and destination must be different files")
    _validate_hq_database(backup_path)
    if destination_path.exists() and not overwrite:
        raise FileExistsError(
            "Restore destination already exists; pass overwrite=True to preserve a rollback copy and replace it"
        )

    rollback_path: Path | None = None
    if destination_path.exists():
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        rollback_path = destination_path.with_name(
            f"{destination_path.name}.pre-restore-{timestamp}.sqlite3"
        )
        if rollback_path.exists():
            raise FileExistsError("Refusing to overwrite an existing rollback backup")
        backup_database(destination_path, rollback_path)

    try:
        _write_consistent_copy(backup_path, destination_path)
    except Exception:
        if rollback_path is not None and rollback_path.exists():
            _write_consistent_copy(rollback_path, destination_path)
        raise
    return destination_path
