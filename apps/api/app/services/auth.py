"""Authentication: login, logout, and current-session verification.

V1 strategy (T038 item 1, "select one simple documented strategy"):
password login + opaque, random, server-side session tokens. Stored
hashed with SHA-256 for lookup — not bcrypt: bcrypt's deliberate
slowness defends low-entropy human-chosen passwords against brute
force; a session token is already a high-entropy random 32-byte value,
where a fast hash is correct (SHA-256 is a standard library primitive
used only for lookup here, not an invented encryption scheme).

Self-registration is NOT implemented (T038 item 2, "only if required
by V1") — no requirement for public signup exists anywhere in the
docs; users are provisioned by some other mechanism, out of scope
here. No HTTP, no SQLAlchemy — the API layer (app.api.v1.auth) is a
thin wrapper around this."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from app.core.security import verify_password
from app.domain.auth import AuthSession, IssuedSession, as_naive_utc
from app.domain.users import User, UserStatus
from app.repositories.sessions import SessionRepository
from app.repositories.users import UserRepository
from app.services.errors import PermissionDeniedError

SESSION_LIFETIME = timedelta(hours=12)
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

# Same message for "no such user" and "wrong password" — never leak
# which one it was (would let an attacker enumerate valid emails).
_INVALID_CREDENTIALS_MESSAGE = "Invalid email or password."


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, users: UserRepository, sessions: SessionRepository) -> None:
        self._users = users
        self._sessions = sessions

    def login(self, email: str, plain_password: str) -> IssuedSession:
        user = self._users.get_by_email(email)
        if user is None:
            raise PermissionDeniedError(_INVALID_CREDENTIALS_MESSAGE)

        if user.status == UserStatus.DISABLED:
            raise PermissionDeniedError("This account is disabled.")

        if user.locked_until is not None and as_naive_utc(
            user.locked_until
        ) > as_naive_utc(datetime.now(UTC)):
            raise PermissionDeniedError(
                "Too many failed login attempts. Try again later."
            )

        if not verify_password(plain_password, user.password_hash):
            self._record_failed_attempt(user)
            raise PermissionDeniedError(_INVALID_CREDENTIALS_MESSAGE)

        assert user.id is not None
        self._users.reset_failed_logins(user.id)
        return self._issue_session(user.id)

    def logout(self, token: str) -> None:
        """Idempotent — logging out an already-invalid token is not an
        error."""
        session = self._get_active_session(token)
        if session is None:
            return
        assert session.id is not None
        self._sessions.revoke(session.id, revoked_at=datetime.now(UTC))

    def get_current_user(self, token: str) -> User | None:
        """Never raises — returns None for any missing/expired/revoked
        token. The API layer (app.api.dependencies) decides how to
        turn that into a 401."""
        session = self._get_active_session(token)
        if session is None:
            return None
        return self._users.get(session.user_id)

    def _get_active_session(self, token: str) -> AuthSession | None:
        session = self._sessions.get_by_token_hash(_hash_token(token))
        if session is None or not session.is_active:
            return None
        return session

    def _record_failed_attempt(self, user: User) -> None:
        assert user.id is not None
        next_attempt_count = user.failed_login_attempts + 1
        locked_until = (
            datetime.now(UTC) + LOCKOUT_DURATION
            if next_attempt_count >= MAX_FAILED_LOGIN_ATTEMPTS
            else None
        )
        self._users.record_failed_login(user.id, locked_until=locked_until)

    def _issue_session(self, user_id: int) -> IssuedSession:
        token = secrets.token_urlsafe(32)
        session = self._sessions.create(
            AuthSession(
                id=None,
                user_id=user_id,
                token_hash=_hash_token(token),
                expires_at=datetime.now(UTC) + SESSION_LIFETIME,
            )
        )
        return IssuedSession(session=session, token=token)
