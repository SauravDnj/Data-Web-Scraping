"""Database-independent domain object for schedules. The scheduler
service (T083) creates jobs from these — it does not execute providers
directly."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Schedule:
    id: int | None
    project_id: int
    cron_expression: str
    timezone: str = "UTC"
    enabled: bool = True
    next_run_at: datetime | None = None
    last_run_at: datetime | None = None
