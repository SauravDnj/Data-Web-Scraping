"""Database-independent domain object for schedules. The scheduler
service (T083) creates jobs from these — it does not execute providers
directly."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Schedule:
    """`next_run_at` is required, not optional — the schema has it
    NOT NULL (docs/04_DATABASE_DESIGN.md) with no server-side default,
    and the repository forwards it as-is at creation time."""

    id: int | None
    project_id: int
    cron_expression: str
    next_run_at: datetime
    timezone: str = "UTC"
    enabled: bool = True
    last_run_at: datetime | None = None
