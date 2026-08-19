from datetime import datetime
from typing import Protocol

from sqlalchemy import select

from app.db.models import Schedule as ScheduleRow
from app.domain.schedules import Schedule
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page, SqlAlchemyRepository


class ScheduleRepository(Protocol):
    def get(self, schedule_id: int) -> Schedule | None: ...

    def create(self, schedule: Schedule) -> Schedule: ...

    def set_enabled(self, schedule_id: int, enabled: bool) -> Schedule: ...

    def list_due(
        self,
        now: datetime,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Schedule]: ...


class SqlAlchemyScheduleRepository(SqlAlchemyRepository[ScheduleRow, Schedule]):
    model = ScheduleRow

    def _to_domain(self, row: ScheduleRow) -> Schedule:
        return Schedule(
            id=row.id,
            project_id=row.project_id,
            cron_expression=row.cron_expression,
            timezone=row.timezone,
            enabled=row.enabled,
            next_run_at=row.next_run_at,
            last_run_at=row.last_run_at,
        )

    def create(self, schedule: Schedule) -> Schedule:
        row = ScheduleRow(
            project_id=schedule.project_id,
            cron_expression=schedule.cron_expression,
            timezone=schedule.timezone,
            enabled=schedule.enabled,
            next_run_at=schedule.next_run_at,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def set_enabled(self, schedule_id: int, enabled: bool) -> Schedule:
        row = self._session.get(ScheduleRow, schedule_id)
        if row is None:
            raise LookupError(f"Schedule {schedule_id} does not exist.")
        row.enabled = enabled
        self._session.flush()
        return self._to_domain(row)

    def list_due(
        self,
        now: datetime,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Schedule]:
        """Matches ix_schedules_enabled_next_run_at exactly."""
        statement = (
            select(ScheduleRow)
            .where(ScheduleRow.enabled.is_(True), ScheduleRow.next_run_at <= now)
            .order_by(ScheduleRow.next_run_at.asc())
        )
        return self._paginate(statement, limit=limit, offset=offset)
