import sqlite3

import pytest

from src.nexora_hq.database import HQDatabase
from src.nexora_hq.maintenance import backup_database, restore_database


def _make_database(path, title):
    database = HQDatabase(path)
    database.initialize()
    database.record_activity("TEST", title, "Maintenance test record")
    database.close()


def _activity_titles(path):
    with sqlite3.connect(path) as connection:
        return [
            row[0]
            for row in connection.execute("SELECT title FROM activity ORDER BY id")
        ]


def test_backup_is_restorable_and_preserves_records(tmp_path):
    source = tmp_path / "hq.sqlite3"
    backup = tmp_path / "backups" / "hq-backup.sqlite3"
    _make_database(source, "Before backup")

    assert backup_database(source, backup) == backup.resolve()
    assert _activity_titles(backup) == _activity_titles(source)
    with sqlite3.connect(backup) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_restore_refuses_to_overwrite_without_explicit_permission(tmp_path):
    backup = tmp_path / "backup.sqlite3"
    destination = tmp_path / "destination.sqlite3"
    _make_database(backup, "Backup state")
    _make_database(destination, "Existing state")

    with pytest.raises(FileExistsError):
        restore_database(backup, destination)

    assert "Existing state" in _activity_titles(destination)
    assert "Backup state" not in _activity_titles(destination)


def test_restore_overwrite_keeps_rollback_copy(tmp_path):
    backup = tmp_path / "backup.sqlite3"
    destination = tmp_path / "destination.sqlite3"
    _make_database(backup, "Backup state")
    _make_database(destination, "Existing state")

    restore_database(backup, destination, overwrite=True)

    assert "Backup state" in _activity_titles(destination)
    assert "Existing state" not in _activity_titles(destination)
    rollback_files = list(tmp_path.glob("destination.sqlite3.pre-restore-*.sqlite3"))
    assert len(rollback_files) == 1
    assert "Existing state" in _activity_titles(rollback_files[0])


def test_backup_rejects_same_source_and_destination(tmp_path):
    source = tmp_path / "hq.sqlite3"
    _make_database(source, "Keep me")

    with pytest.raises(ValueError, match="different files"):
        backup_database(source, source)

    assert "Keep me" in _activity_titles(source)


def test_restore_rejects_invalid_backup_without_touching_destination(tmp_path):
    backup = tmp_path / "invalid.sqlite3"
    destination = tmp_path / "destination.sqlite3"
    backup.write_text("not a sqlite database", encoding="utf-8")
    _make_database(destination, "Keep me")

    with pytest.raises(ValueError, match="SQLite database"):
        restore_database(backup, destination, overwrite=True)

    assert "Keep me" in _activity_titles(destination)
