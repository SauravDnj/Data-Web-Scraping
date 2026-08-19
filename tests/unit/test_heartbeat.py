"""T062 tests: worker heartbeat — against SQLite via the real
`JobRepository` (T032), same rationale as
`tests/unit/test_pipeline_deduplicate.py`. Every timestamp is supplied
explicitly by the test (item 6, "tests with controlled time") — no
real sleeps, no `datetime.now()` calls anywhere in this file."""

from datetime import UTC, datetime, timedelta

from tests.unit.factories import make_config, make_job, make_project, make_user
from workers.jobs.heartbeat import HeartbeatUpdater, find_stale_job_runs

from app.db.session import session_scope
from app.domain.jobs import JobRun, JobRunStatus, JobStatus
from app.repositories.jobs import SqlAlchemyJobRepository

T0 = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)
INTERVAL = timedelta(seconds=30)
THRESHOLD = timedelta(minutes=5)


def _make_run(session, *, email: str = "owner@example.com"):
    user = make_user(session, email=email)
    project = make_project(session, user.id)
    config = make_config(session, project.id, config_json={"query": "coffee"})
    job = make_job(session, project.id, config.id)
    job_repository = SqlAlchemyJobRepository(session)
    job_repository.update_status(job.id, JobStatus.QUEUED)
    job_repository.update_status(job.id, JobStatus.RUNNING)
    run = job_repository.create_run(
        JobRun(
            id=None, job_id=job.id, worker_id="worker-1", status=JobRunStatus.RUNNING
        )
    )
    return job_repository, run


# --- 1/2. update heartbeat during execution / heartbeat interval ---


def test_maybe_beat_does_not_write_before_the_interval_elapses(session_factory):
    with session_scope(session_factory) as session:
        job_repository, run = _make_run(session)
        heartbeat = HeartbeatUpdater(
            job_repository, run.id, started_at=T0, interval=INTERVAL
        )

        wrote = heartbeat.maybe_beat(T0 + timedelta(seconds=5))

        assert wrote is False


def test_maybe_beat_writes_once_the_interval_has_elapsed(session_factory):
    with session_scope(session_factory) as session:
        job_repository, run = _make_run(session)
        heartbeat = HeartbeatUpdater(
            job_repository, run.id, started_at=T0, interval=INTERVAL
        )

        later = T0 + INTERVAL
        wrote = heartbeat.maybe_beat(later)

        assert wrote is True
        runs = job_repository.list_runs_for_job(run.job_id)
        assert runs[0].heartbeat_at == later.replace(tzinfo=None)


def test_maybe_beat_is_gated_again_after_a_real_write(session_factory):
    with session_scope(session_factory) as session:
        job_repository, run = _make_run(session)
        heartbeat = HeartbeatUpdater(
            job_repository, run.id, started_at=T0, interval=INTERVAL
        )

        first = T0 + INTERVAL
        assert heartbeat.maybe_beat(first) is True

        soon_after = first + timedelta(seconds=5)
        assert heartbeat.maybe_beat(soon_after) is False


def test_repeated_calls_within_the_interval_are_cheap_no_ops(session_factory):
    """Simulates calling maybe_beat() once per collected item — most
    calls should be no-ops, not a write per item."""
    with session_scope(session_factory) as session:
        job_repository, run = _make_run(session)
        heartbeat = HeartbeatUpdater(
            job_repository, run.id, started_at=T0, interval=INTERVAL
        )

        results = [
            heartbeat.maybe_beat(T0 + timedelta(seconds=i)) for i in range(1, 10)
        ]

        assert all(result is False for result in results)


# --- 7. heartbeat failures are logged and handled ---


def test_a_heartbeat_write_failure_is_caught_and_returns_false():
    class _FailingRepository:
        def touch_heartbeat(self, run_id, *, heartbeat_at):
            raise RuntimeError("database unavailable")

    heartbeat = HeartbeatUpdater(_FailingRepository(), run_id=1, started_at=T0)

    wrote = heartbeat.maybe_beat(T0 + INTERVAL)

    assert wrote is False  # never raises out of maybe_beat()


# --- 3/4. stale threshold / detect stale job runs ---


def test_a_run_with_an_old_heartbeat_is_detected_as_stale(session_factory):
    with session_scope(session_factory) as session:
        job_repository, run = _make_run(session)
        stale_at = T0 - THRESHOLD - timedelta(minutes=1)
        job_repository.touch_heartbeat(run.id, heartbeat_at=stale_at)

        stale_runs = find_stale_job_runs(
            job_repository, now=T0, stale_threshold=THRESHOLD
        )

        assert [stale_run.id for stale_run in stale_runs] == [run.id]


# --- 5. prevent healthy workers from being marked stale ---


def test_a_run_with_a_recent_heartbeat_is_never_marked_stale(session_factory):
    with session_scope(session_factory) as session:
        job_repository, run = _make_run(session)
        recent = T0 - timedelta(seconds=10)
        job_repository.touch_heartbeat(run.id, heartbeat_at=recent)

        stale_runs = find_stale_job_runs(
            job_repository, now=T0, stale_threshold=THRESHOLD
        )

        assert stale_runs == []


def test_a_finished_run_with_an_old_heartbeat_is_never_marked_stale(session_factory):
    """Only RUNNING runs are candidates - a COMPLETED/FAILED run's
    heartbeat naturally stops advancing and must not be mistaken for
    an abandoned one."""
    with session_scope(session_factory) as session:
        job_repository, run = _make_run(session)
        stale_at = T0 - THRESHOLD - timedelta(minutes=1)
        job_repository.finish_run(
            run.id, status=JobRunStatus.COMPLETED, finished_at=stale_at
        )

        stale_runs = find_stale_job_runs(
            job_repository, now=T0, stale_threshold=THRESHOLD
        )

        assert stale_runs == []


def test_a_healthy_run_survives_alongside_a_stale_one(session_factory):
    """The acceptance criterion, directly: a stopped worker's run
    becomes detectable as stale, without incorrectly flagging a
    healthy one running at the same time."""
    with session_scope(session_factory) as session:
        job_repository, stale_run = _make_run(session)
        job_repository.touch_heartbeat(
            stale_run.id, heartbeat_at=T0 - THRESHOLD - timedelta(minutes=1)
        )

        _job_repository2, healthy_run = _make_run(session, email="other@example.com")
        job_repository.touch_heartbeat(
            healthy_run.id, heartbeat_at=T0 - timedelta(seconds=10)
        )

        stale_runs = find_stale_job_runs(
            job_repository, now=T0, stale_threshold=THRESHOLD
        )

        assert [stale_run_.id for stale_run_ in stale_runs] == [stale_run.id]
