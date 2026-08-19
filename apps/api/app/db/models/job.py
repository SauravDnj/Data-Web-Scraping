from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BigIntegerPK
from app.domain.jobs import JobRunStatus, JobStatus

__all__ = ["Job", "JobRun", "JobStatus", "JobRunStatus"]


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        Index(
            "ix_jobs_project_id_status_requested_at",
            "project_id",
            "status",
            "requested_at",
        ),
        # Separate from the project-scoped index above: worker/scheduler
        # polling for queued or running jobs is project-agnostic, so it
        # needs status as the leading column. Final index tuning against
        # real query plans is T027's job once live MySQL is available.
        Index("ix_jobs_status_requested_at", "status", "requested_at"),
    )

    id: Mapped[int] = mapped_column(BigIntegerPK, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        BigIntegerPK, ForeignKey("projects.id"), nullable=False
    )
    config_id: Mapped[int] = mapped_column(
        BigIntegerPK, ForeignKey("collection_configs.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=JobStatus.DRAFT
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class JobRun(Base):
    """One row per execution attempt. worker_id/attempt/heartbeat_at
    support T062 (heartbeat) and T065 (recovery) — a stale heartbeat is
    how a crashed worker's run gets detected later."""

    __tablename__ = "job_runs"
    __table_args__ = (Index("ix_job_runs_job_id_status", "job_id", "status"),)

    id: Mapped[int] = mapped_column(BigIntegerPK, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        BigIntegerPK, ForeignKey("jobs.id"), nullable=False
    )
    worker_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=JobRunStatus.RUNNING
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now, nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    heartbeat_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now, nullable=False
    )
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
