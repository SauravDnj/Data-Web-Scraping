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

    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            "INSERT INTO users (email, password_hash, status, created_at, updated_at) "
            "VALUES ('a@example.com', 'hash', 'pending', '2026-01-01', '2026-01-01')"
        )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO users (email, password_hash, status, created_at, updated_at) "
                "VALUES ('a@example.com', 'hash2', 'pending', '2026-01-01', '2026-01-01')"
            )
    finally:
        connection.close()

    command.downgrade(config, "base")
    assert "users" not in _table_names(db_path)
