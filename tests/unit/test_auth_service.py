"""T038 tests: login success/failure/lockout/expired-session, logout
revocation — against SQLite in-memory (see tests/unit/test_db_session.py)."""

from datetime import UTC, datetime, timedelta

import pytest
from app.db.models import User as UserRow
from app.db.session import session_scope
from app.domain.auth import AuthSession
from app.repositories.sessions import SqlAlchemySessionRepository
from app.repositories.users import SqlAlchemyUserRepository
from app.services.auth import (
    MAX_FAILED_LOGIN_ATTEMPTS,
    AuthService,
    _hash_token,
)
from app.services.errors import PermissionDeniedError

from tests.unit.factories import make_user

VALID_PASSWORD = "correct horse battery staple"


def _make_auth(session) -> AuthService:
    return AuthService(
        SqlAlchemyUserRepository(session), SqlAlchemySessionRepository(session)
    )


def test_login_succeeds_with_correct_credentials(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session, email="owner@example.com")
        auth = _make_auth(session)

        issued = auth.login("owner@example.com", VALID_PASSWORD)

        assert issued.token
        assert issued.session.user_id == user.id
        assert issued.session.is_active


def test_login_fails_with_wrong_password(session_factory):
    with session_scope(session_factory) as session:
        make_user(session, email="owner@example.com")
        auth = _make_auth(session)

        with pytest.raises(PermissionDeniedError, match="Invalid email or password"):
            auth.login("owner@example.com", "wrong password")


def test_login_fails_for_unknown_email_with_the_same_message(session_factory):
    """No information leak about whether the email exists."""
    with session_scope(session_factory) as session:
        auth = _make_auth(session)

        with pytest.raises(PermissionDeniedError, match="Invalid email or password"):
            auth.login("nobody@example.com", "whatever")


def test_repeated_failures_lock_the_account(session_factory):
    with session_scope(session_factory) as session:
        make_user(session, email="owner@example.com")
        auth = _make_auth(session)

        for _ in range(MAX_FAILED_LOGIN_ATTEMPTS):
            with pytest.raises(PermissionDeniedError):
                auth.login("owner@example.com", "wrong password")

        # Even the CORRECT password is now rejected — account is locked.
        with pytest.raises(PermissionDeniedError, match="Too many failed"):
            auth.login("owner@example.com", VALID_PASSWORD)


def test_successful_login_resets_failed_attempt_counter(session_factory):
    with session_scope(session_factory) as session:
        make_user(session, email="owner@example.com")
        auth = _make_auth(session)

        for _ in range(MAX_FAILED_LOGIN_ATTEMPTS - 1):
            with pytest.raises(PermissionDeniedError):
                auth.login("owner@example.com", "wrong password")

        # One more failure would have locked it — but this succeeds
        # and should reset the counter instead.
        auth.login("owner@example.com", VALID_PASSWORD)

        for _ in range(MAX_FAILED_LOGIN_ATTEMPTS - 1):
            with pytest.raises(PermissionDeniedError):
                auth.login("owner@example.com", "wrong password")

        # Still not locked — the earlier reset means we're not at the
        # threshold yet.
        issued = auth.login("owner@example.com", VALID_PASSWORD)
        assert issued.token


def test_expired_session_is_rejected(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session, email="owner@example.com")
        auth = _make_auth(session)
        sessions = SqlAlchemySessionRepository(session)

        raw_token = "a-known-raw-token-for-this-test"
        sessions.create(
            AuthSession(
                id=None,
                user_id=user.id,
                token_hash=_hash_token(raw_token),
                expires_at=datetime.now(UTC) - timedelta(minutes=1),
            )
        )

        # A real, resolvable token — but its session already expired.
        assert auth.get_current_user(raw_token) is None


def test_logout_revokes_the_session(session_factory):
    with session_scope(session_factory) as session:
        make_user(session, email="owner@example.com")
        auth = _make_auth(session)
        issued = auth.login("owner@example.com", VALID_PASSWORD)

        assert auth.get_current_user(issued.token) is not None
        auth.logout(issued.token)
        assert auth.get_current_user(issued.token) is None


def test_logout_is_idempotent_for_an_already_invalid_token(session_factory):
    with session_scope(session_factory) as session:
        auth = _make_auth(session)
        auth.logout("this-token-was-never-issued")  # must not raise


def test_get_current_user_returns_none_for_an_unknown_token(session_factory):
    with session_scope(session_factory) as session:
        auth = _make_auth(session)
        assert auth.get_current_user("not-a-real-token") is None


def test_disabled_account_cannot_log_in(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session, email="owner@example.com")
        row = session.get(UserRow, user.id)
        row.status = "disabled"
        session.flush()

        auth = _make_auth(session)
        with pytest.raises(PermissionDeniedError, match="disabled"):
            auth.login("owner@example.com", VALID_PASSWORD)
