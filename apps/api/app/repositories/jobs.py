from datetime import datetime, timedelta
from typing import Protocol, cast

from sqlalchemy import CursorResult, func, select, update

from app.db.models import Job as JobRow
from app.db.models import JobRun as JobRunRow
from app.db.models import Project as ProjectRow
from app.domain.job_state_machine import transition
from app.domain.jobs import Job, JobCounters, JobRun, JobRunStatus, JobStatus
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page, SqlAlchemyRepository


class JobRepository(Protocol):
    def get(self, job_id: int) -> Job | None: ...

    def create(self, job: Job) -> Job: ...

    def get_by_idempotency_key(self, idempotency_key: str) -> Job | None: ...

    def update_status(self, job_id: int, target: JobStatus) -> Job: ...

    def update_counters(self, job_id: int, counters: JobCounters) -> Job: ...

    def claim_queued_job(self, job_id: int, *, started_at: datetime) -> Job | None: ...

    def request_cancellation(
        self, job_id: int, *, requested_at: datetime
    ) -> Job | None: ...

    def is_cancellation_requested(self, job_id: int) -> bool: ...

    def finalize_job(
        self,
        job_id: int,
        *,
        status: JobStatus,
        finished_at: datetime,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> Job: ...

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

    def list_for_user(
        self,
        user_id: int,
        *,
        status: JobStatus | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Job]: ...

    def count_by_status_for_user(self, user_id: int) -> dict[JobStatus, int]: ...

    def create_run(self, run: JobRun) -> JobRun: ...

    def list_runs_for_job(self, job_id: int) -> list[JobRun]: ...

    def finish_run(
        self, run_id: int, *, status: JobRunStatus, finished_at: datetime
    ) -> JobRun: ...

    def touch_heartbeat(self, run_id: int, *, heartbeat_at: datetime) -> JobRun: ...

    def list_stale_running_runs(
        self, *, now: datetime, stale_threshold: timedelta
    ) -> list[JobRun]: ...

    def close_stale_run(
        self, run_id: int, *, stale_before: datetime, finished_at: datetime
    ) -> JobRun | None: ...


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
            cancel_requested=row.cancel_requested,
            cancel_requested_at=row.cancel_requested_at,
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

    def claim_queued_job(self, job_id: int, *, started_at: datetime) -> Job | None:
        """T061 item 2 — the real conditional `UPDATE ... WHERE
        status='queued'` docs/09_JOB_QUEUE_WORKER_DEEP.md describes,
        not the ORM get-then-mutate pattern `update_status()` uses.
        That pattern has no protection against a race — two workers
        could both read `status=queued` before either writes. Here,
        the `WHERE` clause hardcodes exactly the one transition this
        method performs (`QUEUED` → `RUNNING`, itself a legal T031
        transition), so it's exactly as safe as going through
        `transition()` for this specific case, while also being
        atomic under real concurrent access — something a Python-side
        state-machine check alone cannot provide. Returns `None` (not
        an error) if another worker already claimed it, or the job
        was never actually queued — the caller must treat that as
        "not mine, skip it"."""
        result = cast(
            CursorResult,
            self._session.execute(
                update(JobRow)
                .where(JobRow.id == job_id, JobRow.status == JobStatus.QUEUED)
                .values(status=JobStatus.RUNNING, started_at=started_at)
            ),
        )
        self._session.flush()
        if result.rowcount == 0:
            return None
        return self.get(job_id)

    def request_cancellation(
        self, job_id: int, *, requested_at: datetime
    ) -> Job | None:
        """T064 item 2 — records a cancellation request without
        touching `status`. Same atomic-conditional-`UPDATE` shape as
        `claim_queued_job()`, and for the same reason: only a job a
        worker is actively executing (`RUNNING`) needs a *request* the
        worker can observe and act on at its own safe boundary
        (`workers/jobs/execute_collection.py`). `JobService.cancel_job()`
        cancels DRAFT/QUEUED/PAUSED jobs immediately instead, via
        `update_status()`, since no worker owns those right now.
        Returns `None` if the job is no longer `RUNNING` by the time
        this executes (it may have just finished) — the caller must
        re-check the job's current status rather than assume the
        request landed."""
        result = cast(
            CursorResult,
            self._session.execute(
                update(JobRow)
                .where(JobRow.id == job_id, JobRow.status == JobStatus.RUNNING)
                .values(cancel_requested=True, cancel_requested_at=requested_at)
            ),
        )
        self._session.flush()
        if result.rowcount == 0:
            return None
        return self.get(job_id)

    def is_cancellation_requested(self, job_id: int) -> bool:
        """A cheap, frequent read — called once per collected item in
        the worker's main loop (T064 item 3), so it stays a single
        boolean column fetch rather than the fuller `get()`."""
        row = self._session.get(JobRow, job_id)
        if row is None:
            raise LookupError(f"Job {job_id} does not exist.")
        return bool(row.cancel_requested)

    def finalize_job(
        self,
        job_id: int,
        *,
        status: JobStatus,
        finished_at: datetime,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> Job:
        """T061 items 14-15 combined — finalize status (through the
        T031 state machine, same as `update_status()`) and record any
        error, atomically, in the same write. Two separate calls here
        would risk a status showing FAILED with no error detail yet
        (or vice versa) if something failed between them."""
        row = self._session.get(JobRow, job_id)
        if row is None:
            raise LookupError(f"Job {job_id} does not exist.")
        row.status = transition(JobStatus(row.status), status)
        row.finished_at = finished_at
        row.error_code = error_code
        row.error_message = error_message
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

    def list_for_user(
        self,
        user_id: int,
        *,
        status: JobStatus | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Job]:
        """T071 — cross-project, matching `GET /jobs`
        (docs/05_API_DESIGN.md). A `Job` has no `user_id` of its own,
        so this joins through `projects` the same way authorization
        already does everywhere else (`ProjectService._require_owner`)
        — filtering by that join IS the authorization boundary here,
        no separate ownership check needed the way single-job lookups
        require one."""
        statement = (
            select(JobRow)
            .join(ProjectRow, ProjectRow.id == JobRow.project_id)
            .where(ProjectRow.user_id == user_id)
        )
        if status is not None:
            statement = statement.where(JobRow.status == status)
        statement = statement.order_by(JobRow.requested_at.desc())
        return self._paginate(statement, limit=limit, offset=offset)

    def count_by_status_for_user(self, user_id: int) -> dict[JobStatus, int]:
        """T071 — the real `GROUP BY` behind `JobService.
        summarize_for_user()`'s dashboard cards. A real SQL aggregate,
        not a client-side sum of a paginated list (T071's own DO NOT
        rule) — every job counts here regardless of how many exist."""
        rows = self._session.execute(
            select(JobRow.status, func.count())
            .join(ProjectRow, ProjectRow.id == JobRow.project_id)
            .where(ProjectRow.user_id == user_id)
            .group_by(JobRow.status)
        ).all()
        return {JobStatus(status): count for status, count in rows}

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

    def finish_run(
        self, run_id: int, *, status: JobRunStatus, finished_at: datetime
    ) -> JobRun:
        """T061 item 16 ("stop heartbeat") — a bookend, not a
        continuous poll (that's T062's job): marks this run's last-
        known-alive moment as `finished_at` one final time, alongside
        its terminal status."""
        row = self._session.get(JobRunRow, run_id)
        if row is None:
            raise LookupError(f"JobRun {run_id} does not exist.")
        row.status = status
        row.finished_at = finished_at
        row.heartbeat_at = finished_at
        self._session.flush()
        return self._run_to_domain(row)

    def touch_heartbeat(self, run_id: int, *, heartbeat_at: datetime) -> JobRun:
        """T062 item 1 — the periodic liveness write during execution
        (as opposed to `finish_run()`'s one-time closing touch). A
        single-column update, deliberately not going through
        `finalize_job()`'s heavier machinery — this is meant to be
        called often and cheaply."""
        row = self._session.get(JobRunRow, run_id)
        if row is None:
            raise LookupError(f"JobRun {run_id} does not exist.")
        row.heartbeat_at = heartbeat_at
        self._session.flush()
        return self._run_to_domain(row)

    def list_stale_running_runs(
        self, *, now: datetime, stale_threshold: timedelta
    ) -> list[JobRun]:
        """T062 items 3-5 — every `RUNNING` run whose last heartbeat is
        older than `stale_threshold` relative to `now` (both supplied
        by the caller, never read internally — same injected-time
        discipline as every other timestamp comparison in this
        codebase, T038's `as_naive_utc` lesson included). A run with a
        recent heartbeat is structurally excluded by the `WHERE`
        clause itself — a healthy worker is never a false positive
        here, not by a separate check bolted on afterward."""
        cutoff = now - stale_threshold
        rows = self._session.scalars(
            select(JobRunRow).where(
                JobRunRow.status == JobRunStatus.RUNNING,
                JobRunRow.heartbeat_at < cutoff,
            )
        ).all()
        return [self._run_to_domain(row) for row in rows]

    def close_stale_run(
        self, run_id: int, *, stale_before: datetime, finished_at: datetime
    ) -> JobRun | None:
        """T065 item 6 ("ensure only one active execution owner
        exists") — the atomic conditional `UPDATE` a recovery process
        uses to close a run `list_stale_running_runs()` found, same
        shape and same reason as `claim_queued_job()`/
        `request_cancellation()`: the `WHERE status='running' AND
        heartbeat_at < stale_before` clause re-verifies staleness at
        the moment of the write, not just at listing time, so a run
        whose worker wrote a fresh heartbeat in between (a false
        positive, still alive, just briefly slow) is left untouched —
        and if two recovery passes race for the same genuinely-stale
        run, only one of them can win this `UPDATE`. Returns `None` in
        either case; the caller must treat that as "not mine, someone
        else is handling it (or it wasn't actually stale)."""
        result = cast(
            CursorResult,
            self._session.execute(
                update(JobRunRow)
                .where(
                    JobRunRow.id == run_id,
                    JobRunRow.status == JobRunStatus.RUNNING,
                    JobRunRow.heartbeat_at < stale_before,
                )
                .values(
                    status=JobRunStatus.FAILED,
                    finished_at=finished_at,
                    heartbeat_at=finished_at,
                )
            ),
        )
        self._session.flush()
        if result.rowcount == 0:
            return None
        row = self._session.get(JobRunRow, run_id)
        assert row is not None
        return self._run_to_domain(row)
