"""T021 migration smoke test: alembic upgrade head / downgrade base
against a genuinely empty, temporary database (SQLite — there's no
real schema yet to make the dialect matter; T022+ add MySQL-specific
tables, and tests/integration/test_db_mysql.py-style real-MySQL
verification should extend here once T012 is done)."""

import sqlite3
from pathlib import Path

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
