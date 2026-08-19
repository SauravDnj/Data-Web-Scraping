from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BigIntegerPK
from app.domain.users import UserStatus

__all__ = ["User", "UserStatus"]


def _utc_now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    """Minimum durable identity model for V1. Authentication service
    logic (login, tokens, sessions) lives in app.services.auth (T038),
    not here — this only stores identity data and lockout state."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigIntegerPK, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=UserStatus.PENDING
    )
    # T038: basic account-lockout rate/abuse control.
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now, onupdate=_utc_now
    )
