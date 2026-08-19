"""T021 migration smoke test: alembic upgrade head / downgrade base
against a genuinely empty, temporary database (SQLite — there's no
real schema yet to make the dialect matter; T022+ add MySQL-specific
tables, and tests/integration/test_db_mysql.py-style real-MySQL
verification should extend here once T012 is done)."""

import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

REPO_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = REPO_ROOT / "apps" / "api" / "alembic.ini"


def _version_table_rows(db_path: Path) -> list[tuple[str]]:
    connection = sqlite3.connect(db_path)
    try:
        return connection.execute("SELECT version_num FROM alembic_version").fetchall()
    finally:
        connection.close()


def test_alembic_upgrade_and_downgrade_from_empty_database(tmp_path):
    db_path = tmp_path / "alembic_smoke.db"
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(config, "head")

    assert db_path.exists()
    assert len(_version_table_rows(db_path)) == 1

    command.downgrade(config, "base")

    assert _version_table_rows(db_path) == []


def _table_names(db_path: Path) -> set[str]:
    connection = sqlite3.connect(db_path)
    try:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    finally:
        connection.close()
    return {row[0] for row in rows}


def test_users_table_is_created_and_removed_by_migration(tmp_path):
    """T022: the migration itself (not just the model against
    create_all) creates a real users table with the unique email
    constraint, and downgrade removes it cleanly."""
    db_path = tmp_path / "users_migration_smoke.db"
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(config, "head")
    assert "users" in _table_names(db_path)

    insert_sql = (
        "INSERT INTO users (email, password_hash, status, created_at, updated_at) "
        "VALUES (?, ?, 'pending', '2026-01-01', '2026-01-01')"
    )
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(insert_sql, ("a@example.com", "hash"))
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(insert_sql, ("a@example.com", "hash2"))
    finally:
        connection.close()

    command.downgrade(config, "base")
    assert "users" not in _table_names(db_path)


def test_project_and_config_tables_are_created_and_removed_by_migration(tmp_path):
    """T023: the migration creates projects/collection_configs with
    real foreign keys and the (project_id, version) unique constraint
    — constraint-level behavior itself is covered thoroughly by the
    ORM tests in tests/unit/test_project_and_config_models.py; this
    just proves the migration DDL produces both tables."""
    db_path = tmp_path / "projects_migration_smoke.db"
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(config, "head")
    assert {"projects", "collection_configs"} <= _table_names(db_path)

    command.downgrade(config, "base")
    assert {"projects", "collection_configs"}.isdisjoint(_table_names(db_path))


def test_job_tables_are_created_and_removed_by_migration(tmp_path):
    """T024: same pattern as T022/T023 — proves the migration DDL,
    constraint-level behavior is covered in tests/unit/test_job_models.py."""
    db_path = tmp_path / "jobs_migration_smoke.db"
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(config, "head")
    assert {"jobs", "job_runs"} <= _table_names(db_path)

    command.downgrade(config, "base")
    assert {"jobs", "job_runs"}.isdisjoint(_table_names(db_path))


def test_record_tables_are_created_and_removed_by_migration(tmp_path):
    """T025: same pattern as T022-T024."""
    db_path = tmp_path / "records_migration_smoke.db"
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(config, "head")
    assert {"records", "record_provenance"} <= _table_names(db_path)

    command.downgrade(config, "base")
    assert {"records", "record_provenance"}.isdisjoint(_table_names(db_path))


def test_operations_tables_are_created_and_removed_by_migration(tmp_path):
    """T026: same pattern as T022-T025."""
    db_path = tmp_path / "operations_migration_smoke.db"
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(config, "head")
    assert {"exports", "schedules", "audit_logs"} <= _table_names(db_path)

    command.downgrade(config, "base")
    assert {"exports", "schedules", "audit_logs"}.isdisjoint(_table_names(db_path))


def _column_names(db_path: Path, table: str) -> set[str]:
    connection = sqlite3.connect(db_path)
    try:
        rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    finally:
        connection.close()
    return {row[1] for row in rows}


def test_idempotency_key_column_migration_round_trips_on_sqlite(tmp_path):
    """T035: this ALTER-TABLE migration originally failed on SQLite
    (constraint changes need Alembic's batch mode there) — this is a
    permanent regression test for that, not just a table-existence
    check like the CREATE TABLE migrations above. Upgrades all the way
    to head, downgrades one step, re-upgrades, then all the way back
    to base — proving the column and its unique constraint survive a
    full up/down/up/down cycle cleanly."""
    db_path = tmp_path / "idempotency_key_migration.db"
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(config, "head")
    assert "idempotency_key" in _column_names(db_path, "jobs")

    command.downgrade(config, "-1")
    assert "idempotency_key" not in _column_names(db_path, "jobs")

    command.upgrade(config, "head")
    assert "idempotency_key" in _column_names(db_path, "jobs")

    command.downgrade(config, "base")
