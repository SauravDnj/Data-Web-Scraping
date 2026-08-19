"""Database-independent domain objects for authentication (T038)."""

from dataclasses import dataclass
from datetime import UTC, datetime


def as_naive_utc(value: datetime) -> datetime:
    """Every DATETIME column in this schema (MySQL and SQLite alike —
    this is not a SQLite quirk) drops timezone-awareness on read-back;
    a value fresh from `session.create()` before any re-query may
    still be the original aware Python object, while the same field
    read back via a later SELECT is naive. Comparing "now" against a
    stored timestamp must normalize both sides the same way regardless
    of which case applies, or the comparison can raise
    `TypeError: can't compare offset-naive and offset-aware datetimes`
    depending on incidental ORM identity-map behavior — found via a
    real test failure at T038, not by inspection."""
    return value.replace(tzinfo=None) if value.tzinfo is not None else value


@dataclass(frozen=True)
class AuthSession:
    """Never holds the raw token — only its hash. The raw token exists
    only transiently, at issuance, as the separate `token` field on
    IssuedSession below."""

    id: int | None
    user_id: int
    token_hash: str
    expires_at: datetime
    created_at: datetime | None = None
    revoked_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        if self.revoked_at is not None:
            return False
        return as_naive_utc(datetime.now(UTC)) < as_naive_utc(self.expires_at)


@dataclass(frozen=True)
class IssuedSession:
    """Returned once, at login — the only time the raw token is ever
    available. Never logged, never persisted raw."""

    session: AuthSession
    token: str
