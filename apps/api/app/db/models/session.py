from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BigIntegerPK


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Session(Base):
    """An opaque server-side session (T038). The raw token is never
    stored — only a SHA-256 hash of it (app.services.auth), so a
    database read alone can never yield a usable credential. Logout/
    revocation just sets revoked_at; expired-or-revoked sessions are
    rejected the same way at lookup time."""

    __tablename__ = "sessions"
    __table_args__ = (Index("ix_sessions_user_id", "user_id"),)

    id: Mapped[int] = mapped_column(BigIntegerPK, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigIntegerPK, ForeignKey("users.id"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
