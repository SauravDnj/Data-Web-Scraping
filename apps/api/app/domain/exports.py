"""Database-independent domain object for exports."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ExportStatus(StrEnum):
    """Single source of truth — app.db.models.export.Export imports
    this rather than redefining it."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Export:
    """No job_id — an export is its own unit of work, not a side
    effect logged onto a job (docs/16_MEMORY.md, T026)."""

    id: int | None
    project_id: int
    requested_by: int
    format: str
    status: ExportStatus = ExportStatus.PENDING
    filters: dict[str, Any] = field(default_factory=dict)
    file_path: str | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
