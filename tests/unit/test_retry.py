"""T063 tests: bounded, classified retry. Pure-function tests
(should_retry/compute_backoff_delay) need no DB; count_retry_chain_
length()/retry_failed_job() run against SQLite via the real
repositories/services (T032/T035/T037), same rationale as
tests/unit/test_job_service.py — plus a fakeredis-backed
RedisJobQueue (T060) for the queue-side assertions."""

from datetime import timedelta

import fakeredis
import pytest
from tests.unit.factories import make_user
from tests.unit.fakes import AlwaysValidValidator
from workers.jobs.retry import (
    DEFAULT_RETRY_POLICY,
    RetryPolicy,
    compute_backoff_delay,
    count_retry_chain_length,
    retry_failed_job,
    should_retry,
)
from workers.queue import RedisJobQueue

from app.db.models import Job as JobRow
from app.db.session import session_scope
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.repositories.configs import SqlAlchemyCollectionConfigRepository
from app.repositories.jobs import SqlAlchemyJobRepository
from app.repositories.projects import SqlAlchemyProjectRepository
from app.services.audit import AuditService
from app.services.configs import ConfigurationService
from app.services.jobs import JobService
from app.services.projects import ProjectService

# --- 1/4. maximum attempts + classify before retry ---


def test_a_non_retryable_error_is_never_retried_regardless_of_attempt():
    assert should_retry(retryable=False, attempt=0) is False


def test_a_retryable_error_within_the_limit_is_retried():
    policy = RetryPolicy(max_attempts=3)
    assert should_retry(retryable=True, attempt=0, policy=policy) is True
    assert should_retry(retryable=True, attempt=2, policy=policy) is True


def test_a_retryable_error_at_the_limit_is_not_retried():
    policy = RetryPolicy(max_attempts=3)
    assert should_retry(retryable=True, attempt=3, policy=policy) is False


def test_a_retryable_error_past_the_limit_is_not_retried():
    """Never retry indefinitely — the explicit T063 DO NOT rule."""
    policy = RetryPolicy(max_attempts=3)
    assert should_retry(retryable=True, attempt=10, policy=policy) is False


# --- 2/3. exponential backoff + jitter ---


def test_the_first_attempts_delay_is_the_base_delay_with_no_jitter():
    policy = RetryPolicy(base_delay=timedelta(seconds=5), backoff_multiplier=4.0)
    delay = compute_backoff_delay(1, policy, random_fraction=0.0)
    assert delay == timedelta(seconds=5)


def test_delay_grows_exponentially_with_attempt_number():
    policy = RetryPolicy(base_delay=timedelta(seconds=5), backoff_multiplier=4.0)
    first = compute_backoff_delay(1, policy, random_fraction=0.0)
    second = compute_backoff_delay(2, policy, random_fraction=0.0)
    third = compute_backoff_delay(3, policy, random_fraction=0.0)

    assert first == timedelta(seconds=5)
    assert second == timedelta(seconds=20)
    assert third == timedelta(seconds=80)


def test_positive_jitter_increases_the_delay():
    policy = RetryPolicy(
        base_delay=timedelta(seconds=10), backoff_multiplier=1.0, jitter_fraction=0.2
    )
    delay = compute_backoff_delay(1, policy, random_fraction=1.0)
    assert delay == timedelta(seconds=12)  # 10 + 10*0.2*1.0


def test_negative_jitter_decreases_the_delay():
    policy = RetryPolicy(
        base_delay=timedelta(seconds=10), backoff_multiplier=1.0, jitter_fraction=0.2
    )
    delay = compute_backoff_delay(1, policy, random_fraction=-1.0)
    assert delay == timedelta(seconds=8)  # 10 - 10*0.2*1.0


def test_the_delay_is_never_negative():
    policy = RetryPolicy(
        base_delay=timedelta(seconds=1), backoff_multiplier=1.0, jitter_fraction=5.0
    )
    delay = compute_backoff_delay(1, policy, random_fraction=-1.0)
    assert delay >= timedelta(seconds=0)


def test_random_jitter_stays_within_the_documented_range_across_many_draws():
    policy = DEFAULT_RETRY_POLICY
    base = policy.base_delay.total_seconds()
    lower = timedelta(seconds=base * (1 - policy.jitter_fraction))
    upper = timedelta(seconds=base * (1 + policy.jitter_fraction))
    for _ in range(50):
        delay = compute_backoff_delay(1, policy)
        assert lower <= delay <= upper


# --- helpers for the DB-touching tests below ---


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
    return projects, configs, jobs


def _fail_job(session, job_id: int, error_code: str) -> None:
    """Test-only arrangement, matching test_job_service.py's own
    `_fail_job` — JobService has no "mark failed" command itself
    (that's worker-level, T061), so this reaches into the row
    directly."""
    row = session.get(JobRow, job_id)
    row.status = "failed"
    row.error_code = error_code
    session.flush()


def _make_failed_job(session, *, error_code: str, email: str = "owner@example.com"):
    user = make_user(session, email=email)
    projects, configs, jobs = _make_services(session)
    project = projects.create_project(
        user_id=user.id, name="My Project", source_type="google_maps"
    )
    configs.create_version(
        project.id,
        requesting_user_id=user.id,
        provider="google_maps",
        config={"query": "coffee shops"},
    )
    job = jobs.create_job(project.id, requesting_user_id=user.id)
    _fail_job(session, job.id, error_code)
    return jobs, job


def _repositories(session):
    return (
        SqlAlchemyJobRepository(session),
        SqlAlchemyProjectRepository(session),
        SqlAlchemyAuditLogRepository(session),
    )


# --- 5. persist attempt count (chain length via the audit trail) ---


def test_a_never_retried_job_has_a_chain_length_of_zero(session_factory):
    with session_scope(session_factory) as session:
        _jobs, job = _make_failed_job(session, error_code="temporary")
        _job_repo, _project_repo, audit_repo = _repositories(session)

        assert count_retry_chain_length(audit_repo, job.id) == 0


def test_chain_length_grows_by_one_per_retry(session_factory):
    with session_scope(session_factory) as session:
        jobs, job = _make_failed_job(session, error_code="temporary")
        job_repo, project_repo, audit_repo = _repositories(session)
        project = project_repo.get(job.project_id)

        first_retry = jobs.retry_job(job.id, requesting_user_id=project.user_id)
        assert count_retry_chain_length(audit_repo, first_retry.id) == 1

        _fail_job(session, first_retry.id, "temporary")
        second_retry = jobs.retry_job(
            first_retry.id, requesting_user_id=project.user_id
        )
        assert count_retry_chain_length(audit_repo, second_retry.id) == 2


# --- 6/7. requeue retryable jobs / mark permanent failures ---


def test_a_retryable_failure_is_requeued(session_factory):
    with session_scope(session_factory) as session:
        _jobs, job = _make_failed_job(session, error_code="temporary")
        job_repo, project_repo, audit_repo = _repositories(session)
        _projects, _configs, job_service = _make_services(session)
        queue = RedisJobQueue(fakeredis.FakeRedis())

        new_job = retry_failed_job(
            job.id,
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            job_service=job_service,
            queue=queue,
        )

        assert new_job is not None
        assert new_job.id != job.id
        assert queue.dequeue(timeout_seconds=1) == new_job.id


def test_a_permanent_failure_is_never_retried(session_factory):
    with session_scope(session_factory) as session:
        _jobs, job = _make_failed_job(session, error_code="authentication")
        job_repo, project_repo, audit_repo = _repositories(session)
        _projects, _configs, job_service = _make_services(session)
        queue = RedisJobQueue(fakeredis.FakeRedis())

        result = retry_failed_job(
            job.id,
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            job_service=job_service,
            queue=queue,
        )

        assert result is None
        assert queue.dequeue(timeout_seconds=0.1) is None


def test_a_lineage_that_hit_the_attempt_ceiling_is_no_longer_retried(session_factory):
    """DO NOT list: never retry indefinitely — enforced end to end,
    not just at the pure should_retry() level."""
    with session_scope(session_factory) as session:
        jobs, job = _make_failed_job(session, error_code="temporary")
        job_repo, project_repo, audit_repo = _repositories(session)
        _projects, _configs, job_service = _make_services(session)
        queue = RedisJobQueue(fakeredis.FakeRedis())
        policy = RetryPolicy(max_attempts=2)

        # max_attempts=2 allows chain lengths 0 and 1 to retry (the
        # original, then its first retry) — the third attempt, whose
        # chain length is 2, is where the ceiling actually bites.
        first = retry_failed_job(
            job.id,
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            job_service=job_service,
            queue=queue,
            policy=policy,
        )
        assert first is not None  # chain length 0 < 2
        _fail_job(session, first.id, "temporary")

        second = retry_failed_job(
            first.id,
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            job_service=job_service,
            queue=queue,
            policy=policy,
        )
        assert second is not None  # chain length 1 < 2
        _fail_job(session, second.id, "temporary")

        third = retry_failed_job(
            second.id,
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            job_service=job_service,
            queue=queue,
            policy=policy,
        )

        assert third is None  # chain length 2, at the ceiling


# --- 9. test every error class ---


@pytest.mark.parametrize(
    "error_code,expected_retried",
    [
        ("authentication", False),
        ("quota", False),
        ("invalid_request", False),
        ("permanent", False),
        ("unknown", False),
        ("rate", True),
        ("temporary", True),
    ],
)
def test_every_provider_error_category_matches_its_documented_retry_default(
    session_factory, error_code, expected_retried
):
    with session_scope(session_factory) as session:
        _jobs, job = _make_failed_job(session, error_code=error_code)
        job_repo, project_repo, audit_repo = _repositories(session)
        _projects, _configs, job_service = _make_services(session)
        queue = RedisJobQueue(fakeredis.FakeRedis())

        result = retry_failed_job(
            job.id,
            job_repository=job_repo,
            project_repository=project_repo,
            audit_repository=audit_repo,
            job_service=job_service,
            queue=queue,
        )

        assert (result is not None) == expected_retried
