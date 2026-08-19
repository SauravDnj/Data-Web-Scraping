from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BigIntegerPK
from app.domain.exports import ExportStatus

__all__ = ["Export", "ExportStatus"]


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Export(Base):
    """Tracked independently of the job that produced the underlying
    records — an export is its own unit of work with its own
    lifecycle, not a side effect logged onto a job."""

    __tablename__ = "exports"
    __table_args__ = (
        Index("ix_exports_project_id_created_at", "project_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigIntegerPK, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        BigIntegerPK, ForeignKey("projects.id"), nullable=False
    )
    requested_by: Mapped[int] = mapped_column(
        BigIntegerPK, ForeignKey("users.id"), nullable=False
    )
    format: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=ExportStatus.PENDING
    )
    filters_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
