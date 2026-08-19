"""SQLAlchemy plumbing tests using SQLite in-memory — proves the
engine/session/Base/naming-convention wiring itself is correct,
independent of which database dialect is behind it. MySQL-specific
verification lives in tests/integration/test_db_mysql.py."""

from collections.abc import Iterator

import pytest
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import build_engine, build_session_factory, session_scope


class _Widget(Base):
    """Throwaway model used only to prove schema creation works — not
    a real domain model."""

    __tablename__ = "test_widgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


@pytest.fixture
def sqlite_engine() -> Iterator[object]:
    # StaticPool + check_same_thread=False keeps the same in-memory
    # database alive across connections within this test.
    engine = build_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_temporary_schema_can_be_created_and_used(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        session.add(_Widget(name="alpha"))

    with session_scope(factory) as session:
        widget = session.query(_Widget).filter_by(name="alpha").one()
        assert widget.id is not None


def test_session_rolls_back_on_error(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with pytest.raises(RuntimeError):
        with session_scope(factory) as session:
            session.add(_Widget(name="beta"))
            session.flush()  # write is visible within the transaction...
            raise RuntimeError("simulated failure after a write")

    with session_scope(factory) as session:
        # ...but never committed, because session_scope rolled back.
        assert session.query(_Widget).filter_by(name="beta").count() == 0


def test_naming_convention_applies_to_primary_key_constraint():
    constraint = _Widget.__table__.primary_key
    assert constraint.name == "pk_test_widgets"
