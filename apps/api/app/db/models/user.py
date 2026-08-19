from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BigIntegerPK


class UserStatus:
    """Plain string values, matching the VARCHAR(32) status columns
    used throughout the schema (docs/04_DATABASE_DESIGN.md) — not a
    database-level ENUM."""

    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"

    ALL = frozenset({ACTIVE, DISABLED, PENDING})


def _utc_now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    """Minimum durable identity model for V1. No authentication
    service logic here (login, tokens, sessions) — that's T038; this
    only stores identity data, already-hashed."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigIntegerPK, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=UserStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now, onupdate=_utc_now
    )
