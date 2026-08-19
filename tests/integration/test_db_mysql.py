"""Real MySQL verification of T020, using the actual configured
DATABASE_URL. Skips cleanly if MySQL/app_user (T012) isn't set up yet
— once it is, this starts running for real with no code change,
doubling as a regression check for T012 itself."""

import os

import pytest
from app.db.session import build_engine, build_session_factory, session_scope
from sqlalchemy import text
from sqlalchemy.exc import OperationalError


def _mysql_reachable(database_url: str) -> bool:
    try:
        engine = build_engine(database_url, pool_pre_ping=False)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except OperationalError:
        return False


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://app_user:test@localhost:3306/google_data_platform",
)

pytestmark = pytest.mark.skipif(
    not _mysql_reachable(DATABASE_URL),
    reason="MySQL/app_user not reachable yet (T012 not complete) — "
    "see docs/16_MEMORY.md",
)


def test_session_can_acquire_and_close_against_real_mysql():
    engine = build_engine(DATABASE_URL)
    factory = build_session_factory(engine)

    with session_scope(factory) as session:
        result = session.execute(text("SELECT 1")).scalar_one()

    assert result == 1
    engine.dispose()
