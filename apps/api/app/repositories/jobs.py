from typing import Protocol

from sqlalchemy import select

from app.db.models import Job as JobRow
from app.db.models import JobRun as JobRunRow
from app.domain.job_state_machine import transition
from app.domain.jobs import Job, JobCounters, JobRun, JobRunStatus, JobStatus
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page, SqlAlchemyRepository


class JobRepository(Protocol):
    def get(self, job_id: int) -> Job | None: ...

    def create(self, job: Job) -> Job: ...

    def get_by_idempotency_key(self, idempotency_key: str) -> Job | None: ...

    def update_status(self, job_id: int, target: JobStatus) -> Job: ...

    def update_counters(self, job_id: int, counters: JobCounters) -> Job: ...

    def list_for_project(
        self,
        project_id: int,
        *,
        status: JobStatus | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Job]: ...

    def list_queued_or_running(
        self, *, limit: int = DEFAULT_PAGE_LIMIT, offset: int = 0
    ) -> Page[Job]: ...

    def create_run(self, run: JobRun) -> JobRun: ...

    def list_runs_for_job(self, job_id: int) -> list[JobRun]: ...


class SqlAlchemyJobRepository(SqlAlchemyRepository[JobRow, Job]):
    model = JobRow

    def _to_domain(self, row: JobRow) -> Job:
        return Job(
            id=row.id,
            project_id=row.project_id,
            config_id=row.config_id,
            status=JobStatus(row.status),
            counters=JobCounters(
                total_units=row.total_units,
                successful_units=row.successful_units,
                failed_units=row.failed_units,
                skipped_units=row.skipped_units,
                records_created=row.records_created,
                records_updated=row.records_updated,
                records_rejected=row.records_rejected,
            ),
            requested_at=row.requested_at,
            started_at=row.started_at,
            finished_at=row.finished_at,
            error_code=row.error_code,
            error_message=row.error_message,
            idempotency_key=row.idempotency_key,
        )

    def create(self, job: Job) -> Job:
        row = JobRow(
            project_id=job.project_id,
            config_id=job.config_id,
            status=job.status,
            total_units=job.counters.total_units,
            successful_units=job.counters.successful_units,
            failed_units=job.counters.failed_units,
            skipped_units=job.counters.skipped_units,
            records_created=job.counters.records_created,
            records_updated=job.counters.records_updated,
            records_rejected=job.counters.records_rejected,
            idempotency_key=job.idempotency_key,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def get_by_idempotency_key(self, idempotency_key: str) -> Job | None:
        row = self._session.scalar(
            select(JobRow).where(JobRow.idempotency_key == idempotency_key)
        )
        return self._to_domain(row) if row is not None else None

    def update_status(self, job_id: int, target: JobStatus) -> Job:
        """Goes through app.domain.job_state_machine.transition() —
        never assigns row.status directly (T031's "database/service
        code uses this state machine" requirement)."""
        row = self._session.get(JobRow, job_id)
        if row is None:
            raise LookupError(f"Job {job_id} does not exist.")
        row.status = transition(JobStatus(row.status), target)
        self._session.flush()
        return self._to_domain(row)

    def update_counters(self, job_id: int, counters: JobCounters) -> Job:
        """T055's write path — always called from within the same
        `session_scope()` transaction as the batch's own record
        writes (T054's `persist_batch()`), so the counters commit or
        roll back together with the records they describe. Never a
        separate, later transaction — that would risk the counters
        surviving a rollback of the records themselves, or vice versa,
        violating T055's "never claim success for uncommitted records"
        acceptance criterion."""
        row = self._session.get(JobRow, job_id)
        if row is None:
            raise LookupError(f"Job {job_id} does not exist.")
        row.total_units = counters.total_units
        row.successful_units = counters.successful_units
        row.failed_units = counters.failed_units
        row.skipped_units = counters.skipped_units
        row.records_created = counters.records_created
        row.records_updated = counters.records_updated
        row.records_rejected = counters.records_rejected
        self._session.flush()
        return self._to_domain(row)

    def list_for_project(
        self,
        project_id: int,
        *,
        status: JobStatus | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Job]:
        statement = select(JobRow).where(JobRow.project_id == project_id)
        if status is not None:
            statement = statement.where(JobRow.status == status)
        statement = statement.order_by(JobRow.requested_at.desc())
        return self._paginate(statement, limit=limit, offset=offset)

    def list_queued_or_running(
        self, *, limit: int = DEFAULT_PAGE_LIMIT, offset: int = 0
    ) -> Page[Job]:
        """Project-agnostic — matches ix_jobs_status_requested_at,
        the index added specifically for worker/scheduler polling."""
        statement = (
            select(JobRow)
            .where(JobRow.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]))
            .order_by(JobRow.requested_at.asc())
        )
        return self._paginate(statement, limit=limit, offset=offset)

    def _run_to_domain(self, row: JobRunRow) -> JobRun:
        return JobRun(
            id=row.id,
            job_id=row.job_id,
            worker_id=row.worker_id,
            status=JobRunStatus(row.status),
            attempt=row.attempt,
            started_at=row.started_at,
            finished_at=row.finished_at,
            heartbeat_at=row.heartbeat_at,
            metrics=row.metrics_json,
        )

    def create_run(self, run: JobRun) -> JobRun:
        row = JobRunRow(
            job_id=run.job_id,
            worker_id=run.worker_id,
            status=run.status,
            attempt=run.attempt,
            metrics_json=run.metrics,
        )
        self._session.add(row)
        self._session.flush()
        return self._run_to_domain(row)

    def list_runs_for_job(self, job_id: int) -> list[JobRun]:
        rows = self._session.scalars(
            select(JobRunRow)
            .where(JobRunRow.job_id == job_id)
            .order_by(JobRunRow.attempt.asc())
        ).all()
        return [self._run_to_domain(row) for row in rows]
