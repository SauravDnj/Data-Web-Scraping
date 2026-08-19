from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BigIntegerPK


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Schedule(Base):
    """The scheduler service (T083) creates jobs from these — it does
    not execute providers directly. `enabled` gates whether the
    scheduler considers this schedule at all; a disabled schedule
    keeps `next_run_at` frozen rather than recalculating it."""

    __tablename__ = "schedules"
    __table_args__ = (
        Index("ix_schedules_enabled_next_run_at", "enabled", "next_run_at"),
    )

    id: Mapped[int] = mapped_column(BigIntegerPK, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        BigIntegerPK, ForeignKey("projects.id"), nullable=False
    )
    cron_expression: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    next_run_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
