"""Shared fixtures for model/session tests. See
tests/unit/test_db_session.py for why SQLite in-memory stands in for a
real temporary database in these tests."""

from collections.abc import Iterator

import pytest
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import build_engine


@pytest.fixture
def sqlite_engine() -> Iterator[object]:
    engine = build_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()
