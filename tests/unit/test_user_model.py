"""T022 model tests: uniqueness, password hash storage, and email
normalization — against SQLite in-memory (same rationale as
tests/unit/test_db_session.py; a real migration-applied users table is
proven separately in tests/integration/test_migrations.py)."""

from collections.abc import Iterator

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password, normalize_email, verify_password
from app.db.base import Base
from app.db.models import User, UserStatus
from app.db.session import build_engine, build_session_factory, session_scope


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


def _make_user(email: str, plain_password: str = "correct horse battery staple") -> User:
    return User(
        email=normalize_email(email),
        name="Test User",
        password_hash=hash_password(plain_password),
        status=UserStatus.PENDING,
    )


def test_user_can_be_created_and_retrieved(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        session.add(_make_user("Person@Example.com"))

    with session_scope(factory) as session:
        user = session.query(User).filter_by(email="person@example.com").one()
        assert user.status == UserStatus.PENDING
        assert user.created_at is not None
        assert user.updated_at is not None


def test_duplicate_normalized_email_is_rejected(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        session.add(_make_user("dup@example.com"))

    with pytest.raises(IntegrityError):
        with session_scope(factory) as session:
            # Different casing/whitespace, but the same normalized email.
            session.add(_make_user("  Dup@Example.com  "))


def test_password_hash_is_never_plaintext():
    plain = "correct horse battery staple"
    hashed = hash_password(plain)

    assert hashed != plain
    assert plain not in hashed
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong password", hashed) is False


def test_normalize_email_lowercases_and_trims():
    assert normalize_email("  Person@Example.COM  ") == "person@example.com"
