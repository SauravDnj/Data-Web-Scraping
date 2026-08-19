"""T065 tests: worker recovery. Against SQLite + `fakeredis` (this
project's established real-substitute-system testing strategy),
building `RUNNING` jobs with a manually-aged `JobRun.heartbeat_at`
(via `JobRepository.touch_heartbeat()`, T062) to simulate a crashed
worker without needing a real clock or a real crash."""

from datetime import UTC, datetime, timedelta

import fakeredis
from app.db.models import Job as JobRow
from app.db.session import session_scope
from app.domain.job_errors import WORKER_CRASHED_ERROR_CODE
from app.domain.jobs import JobRun, JobRunStatus, JobStatus
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.repositories.configs import SqlAlchemyCollectionConfigRepository
from app.repositories.jobs import SqlAlchemyJobRepository
from app.repositories.projects import SqlAlchemyProjectRepository
from app.services.audit import AuditService
from app.services.configs import ConfigurationService
from app.services.jobs import JobService
from app.services.projects import ProjectService

from tests.unit.factories import make_user
from tests.unit.fakes import AlwaysValidValidator
from workers.jobs.heartbeat import STALE_THRESHOLD
from workers.jobs.recovery import recover_stale_job_runs
from workers.jobs.retry import RetryPolicy
from workers.queue import RedisJobQueue

NOW = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)


def _make_services(session):
    audit = AuditService(SqlAlchemyAuditLogRepository(session))
    projects = ProjectService(SqlAlchemyProjectRepository(session), audit)
    configs = ConfigurationService(
        SqlAlchemyCollectionConfigRepository(session),
        projects,
        AlwaysValidValidator(),
        audit,
    )
    jobs = JobService(SqlAlchemyJobRepository(session), projects, configs, audit)
    return audit, projects, configs, jobs


def _make_running_job_with_run(
    session, *, heartbeat_at: datetime, email: str = "owner@example.com"
):
    """A RUNNING job with one RUNNING JobRun whose heartbeat is frozen
    at `heartbeat_at` — standing in for "a worker claimed this job and
    then stopped sending heartbeats" without a real crash or a real
    clock."""
    user = make_user(session, email=email)
    audit, projects, configs, jobs = _make_services(session)
    project = projects.create_project(
        user_id=user.id, name="My Project", source_type="google_maps"
    )
    configs.create_version(
        project.id,
        requesting_user_id=user.id,
        provider="google_maps",
        config={"query": "coffee shops"},
    )
    job = jobs.create_job(project.id, requesting_user_id=user.id)  # QUEUED

    job_repo = SqlAlchemyJobRepository(session)
    job_repo.update_status(job.id, JobStatus.RUNNING)
    run = job_repo.create_run(
        JobRun(
            id=None,
            job_id=job.id,
            worker_id="worker-presumed-dead",
            status=JobRunStatus.RUNNING,
            attempt=1,
        )
    )
    job_repo.touch_heartbeat(run.id, heartbeat_at=heartbeat_at)

    return audit, project, jobs, job, run


def _repositories(session):
    return (
        SqlAlchemyJobRepository(session),
        SqlAlchemyProjectRepository(session),
        SqlAlchemyAuditLogRepository(session),
    )


def test_a_stale_run_is_recovered_the_job_marked_failed_and_requeued(
    session_factory,
):
    """T065's literal scenario: a simulated worker crash (item 7) is
    recovered after its heartbeat goes stale past STALE_THRESHOLD
    (item 9)."""
    stale_heartbeat = NOW - STALE_THRESHOLD - timedelta(seconds=1)
    with session_scope(session_factory) as session:
        audit, _project, jobs, job, run = _make_running_job_with_run(
            session, heartbeat_at=stale_heartbeat
        )
        job_repo, project_repo, audit_repo = _repositories(session)
        queue = RedisJobQueue(fakeredis.FakeRedis())

        outcomes = recover_stale_job_runs(
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            audit_service=audit,
            job_service=jobs,
            queue=queue,
            now=NOW,
        )

        assert len(outcomes) == 1
        outcome = outcomes[0]
        assert outcome.job_id == job.id
        assert outcome.run_id == run.id
        assert outcome.requeued_job_id is not None

        original = job_repo.get(job.id)
        assert original.status == JobStatus.FAILED
        assert original.error_code == WORKER_CRASHED_ERROR_CODE

        closed_runs = job_repo.list_runs_for_job(job.id)
        assert closed_runs[0].status == JobRunStatus.FAILED
        # SQLite drops tzinfo on read-back (T054's lesson) — compare
        # naive to naive.
        assert closed_runs[0].finished_at == NOW.replace(tzinfo=None)

        new_job = job_repo.get(outcome.requeued_job_id)
        assert new_job.status == JobStatus.QUEUED
        assert queue.dequeue(timeout_seconds=1) == new_job.id

        recovered_events = audit_repo.list_for_entity("job", job.id).items
        assert any(e.action == "job.recovered" for e in recovered_events)


def test_a_run_with_a_fresh_heartbeat_is_never_recovered(session_factory):
    """A healthy, still-beating worker must never be a false positive
    — same "never falsely flagged" guarantee T062 already proved for
    detection alone, now proved end to end through recovery."""
    fresh_heartbeat = NOW - timedelta(seconds=5)
    with session_scope(session_factory) as session:
        audit, _project, jobs, job, _run = _make_running_job_with_run(
            session, heartbeat_at=fresh_heartbeat
        )
        job_repo, project_repo, audit_repo = _repositories(session)
        queue = RedisJobQueue(fakeredis.FakeRedis())

        outcomes = recover_stale_job_runs(
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            audit_service=audit,
            job_service=jobs,
            queue=queue,
            now=NOW,
        )

        assert outcomes == []
        assert job_repo.get(job.id).status == JobStatus.RUNNING


def test_recovering_the_same_stale_run_twice_only_recovers_once(session_factory):
    """Item 6/8 — "ensure only one active execution owner exists" /
    duplicate delivery: two recovery sweeps racing (or one sweep
    running twice) over the same stale run must not requeue the job
    twice."""
    stale_heartbeat = NOW - STALE_THRESHOLD - timedelta(seconds=1)
    with session_scope(session_factory) as session:
        audit, _project, jobs, _job, _run = _make_running_job_with_run(
            session, heartbeat_at=stale_heartbeat
        )
        job_repo, project_repo, audit_repo = _repositories(session)
        queue = RedisJobQueue(fakeredis.FakeRedis())

        kwargs = {
            "job_repository": job_repo,
            "project_repository": project_repo,
            "audit_repository": audit_repo,
            "audit_service": audit,
            "job_service": jobs,
            "queue": queue,
            "now": NOW,
        }
        first = recover_stale_job_runs(**kwargs)
        second = recover_stale_job_runs(**kwargs)

        assert len(first) == 1
        assert second == []  # nothing left to recover — not recovered again

        # exactly one new job was ever queued for this lineage
        assert queue.dequeue(timeout_seconds=1) is not None
        assert queue.dequeue(timeout_seconds=0.1) is None


def test_a_job_already_finalized_before_recovery_reaches_it_is_left_alone(
    session_factory,
):
    """The other half of item 6's safety net: if the "dead" worker
    genuinely wasn't dead and finished the job normally right as the
    run was judged stale, recovery must not override that real
    outcome — it only closes the now-orphaned run administratively."""
    stale_heartbeat = NOW - STALE_THRESHOLD - timedelta(seconds=1)
    with session_scope(session_factory) as session:
        audit, _project, jobs, job, _run = _make_running_job_with_run(
            session, heartbeat_at=stale_heartbeat
        )
        job_repo, project_repo, audit_repo = _repositories(session)
        queue = RedisJobQueue(fakeredis.FakeRedis())

        # Simulate the worker finishing normally a moment before
        # recovery runs — a real successful completion, not a crash.
        job_repo.finalize_job(
            job.id, status=JobStatus.COMPLETED, finished_at=NOW - timedelta(seconds=1)
        )

        outcomes = recover_stale_job_runs(
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            audit_service=audit,
            job_service=jobs,
            queue=queue,
            now=NOW,
        )

        assert len(outcomes) == 1
        assert outcomes[0].requeued_job_id is None

        # the real outcome stands, untouched
        assert job_repo.get(job.id).status == JobStatus.COMPLETED
        # but the orphaned run was still closed out
        assert job_repo.list_runs_for_job(job.id)[0].status == JobRunStatus.FAILED


def test_a_lineage_that_already_hit_the_attempt_ceiling_is_marked_failed_not_requeued(
    session_factory,
):
    """Item 5 — exhausted jobs are marked failed, never retried
    indefinitely, reusing T063's own bounded-chain enforcement. Setup:
    an original job fails normally, gets retried once (T035/T063
    machinery, unrelated to recovery), and *that* retried attempt is
    the one that then crashes — its own chain length is already 1, so
    at `max_attempts=1` recovery must not retry it a second time."""
    stale_heartbeat = NOW - STALE_THRESHOLD - timedelta(seconds=1)
    policy = RetryPolicy(max_attempts=1)
    with session_scope(session_factory) as session:
        user = make_user(session)
        audit, projects, configs, jobs = _make_services(session)
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )
        configs.create_version(
            project.id,
            requesting_user_id=user.id,
            provider="google_maps",
            config={"query": "coffee shops"},
        )
        job_repo, project_repo, audit_repo = _repositories(session)
        queue = RedisJobQueue(fakeredis.FakeRedis())

        original = jobs.create_job(project.id, requesting_user_id=user.id)
        row = session.get(JobRow, original.id)
        row.status = JobStatus.FAILED
        row.error_code = "temporary"
        session.flush()
        retried = jobs.retry_job(original.id, requesting_user_id=user.id)

        job_repo.update_status(retried.id, JobStatus.RUNNING)
        run = job_repo.create_run(
            JobRun(
                id=None,
                job_id=retried.id,
                worker_id="worker-presumed-dead",
                status=JobRunStatus.RUNNING,
                attempt=1,
            )
        )
        job_repo.touch_heartbeat(run.id, heartbeat_at=stale_heartbeat)

        outcomes = recover_stale_job_runs(
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            audit_service=audit,
            job_service=jobs,
            queue=queue,
            now=NOW,
            retry_policy=policy,
        )

        assert len(outcomes) == 1
        assert outcomes[0].requeued_job_id is None
        assert job_repo.get(retried.id).status == JobStatus.FAILED
        assert queue.dequeue(timeout_seconds=0.1) is None
