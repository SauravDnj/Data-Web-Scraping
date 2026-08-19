"""Database-independent domain objects for jobs and job runs."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

_COUNTER_FIELDS = (
    "total_units",
    "successful_units",
    "failed_units",
    "skipped_units",
    "records_created",
    "records_updated",
    "records_rejected",
)


class JobStatus(StrEnum):
    """Canonical job states, resolved at T000 (see docs/16_MEMORY.md):
    draft -> queued -> running -> {completed, partially_completed,
    failed, cancelled, paused}, with paused re-entrant to running.
    Single source of truth — app.db.models.job.Job imports this."""

    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobRunStatus(StrEnum):
    """A single execution attempt's status — narrower than JobStatus
    since a run doesn't have draft/queued/paused states."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class JobCounters:
    total_units: int = 0
    successful_units: int = 0
    failed_units: int = 0
    skipped_units: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_rejected: int = 0

    def __post_init__(self) -> None:
        for name in _COUNTER_FIELDS:
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must not be negative.")


@dataclass(frozen=True)
class Job:
    id: int | None
    project_id: int
    config_id: int
    status: JobStatus = JobStatus.DRAFT
    counters: JobCounters = field(default_factory=JobCounters)
    requested_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class JobRun:
    id: int | None
    job_id: int
    worker_id: str
    status: JobRunStatus = JobRunStatus.RUNNING
    attempt: int = 1
    started_at: datetime | None = None
    finished_at: datetime | None = None
    heartbeat_at: datetime | None = None
    metrics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.attempt < 1:
            raise ValueError("attempt must be >= 1.")
