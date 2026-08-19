"""Job control-plane operations: creation, cancel, pause/resume,
retry. No provider calls here — that belongs to the worker
(T060/T061). No HTTP, no SQLAlchemy — depends on repository Protocols
(T032), the T031 state machine, and other services (T033/T034),
reused rather than duplicated."""

from app.domain.audit_actions import AuditAction
from app.domain.job_errors import is_retryable
from app.domain.jobs import Job, JobStatus
from app.repositories.jobs import JobRepository
from app.services.audit import AuditService
from app.services.configs import ConfigurationService
from app.services.errors import InvalidStateError, NotFoundError
from app.services.projects import ProjectService


class JobService:
    def __init__(
        self,
        jobs: JobRepository,
        projects: ProjectService,
        configs: ConfigurationService,
        audit: AuditService,
    ) -> None:
        self._jobs = jobs
        self._projects = projects
        self._configs = configs
        self._audit = audit

    def create_job(
        self,
        project_id: int,
        *,
        requesting_user_id: int,
        idempotency_key: str | None = None,
    ) -> Job:
        """Transactional: the idempotency check, config lookup,
        insert, and QUEUED transition all happen against the same
        session — the caller's session_scope() (T020) is what commits
        them together or rolls them all back together. A duplicate
        request with the same idempotency_key returns the existing
        job rather than creating a new one; the column's DB-level
        UNIQUE constraint (T035 migration) is the actual correctness
        guarantee under concurrent requests, this check is the common
        (non-racing) case's fast path."""
        if idempotency_key is not None:
            existing = self._jobs.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                return existing

        # Authorization + "archived project cannot start new jobs" (T033).
        self._projects.ensure_can_start_job(
            project_id, requesting_user_id=requesting_user_id
        )

        active_config = self._configs.get_active(
            project_id, requesting_user_id=requesting_user_id
        )
        if active_config is None:
            raise InvalidStateError(
                f"Project {project_id} has no active configuration."
            )
        assert active_config.id is not None

        job = Job(
            id=None,
            project_id=project_id,
            config_id=active_config.id,
            idempotency_key=idempotency_key,
        )
        created = self._jobs.create(job)
        assert created.id is not None
        queued = self._jobs.update_status(created.id, JobStatus.QUEUED)

        self._audit.record_event(
            actor_user_id=requesting_user_id,
            action=AuditAction.JOB_CREATED,
            entity_type="job",
            entity_id=queued.id,
            details={"project_id": project_id},
        )
        return queued

    def get_job(self, job_id: int, *, requesting_user_id: int) -> Job:
        return self._require_owned_job(job_id, requesting_user_id)

    def cancel_job(self, job_id: int, *, requesting_user_id: int) -> Job:
        self._require_owned_job(job_id, requesting_user_id)
        cancelled = self._jobs.update_status(job_id, JobStatus.CANCELLED)
        self._audit.record_event(
            actor_user_id=requesting_user_id,
            action=AuditAction.JOB_CANCELLED,
            entity_type="job",
            entity_id=job_id,
        )
        return cancelled

    def pause_job(self, job_id: int, *, requesting_user_id: int) -> Job:
        """Only legal from RUNNING — enforced by the T031 state
        machine inside JobRepository.update_status(), not re-checked
        here."""
        self._require_owned_job(job_id, requesting_user_id)
        paused = self._jobs.update_status(job_id, JobStatus.PAUSED)
        self._audit.record_event(
            actor_user_id=requesting_user_id,
            action=AuditAction.JOB_PAUSED,
            entity_type="job",
            entity_id=job_id,
        )
        return paused

    def resume_job(self, job_id: int, *, requesting_user_id: int) -> Job:
        self._require_owned_job(job_id, requesting_user_id)
        resumed = self._jobs.update_status(job_id, JobStatus.RUNNING)
        self._audit.record_event(
            actor_user_id=requesting_user_id,
            action=AuditAction.JOB_RESUMED,
            entity_type="job",
            entity_id=job_id,
        )
        return resumed

    def retry_job(self, job_id: int, *, requesting_user_id: int) -> Job:
        """FAILED is terminal for a Job row (T031) — a retry creates a
        NEW job referencing the same project/config rather than
        resurrecting the old one, and only when the original failure's
        error class is retryable (app.domain.job_errors, reconciled
        with app.domain.provider_contracts.ProviderErrorCategory at
        T044)."""
        original = self._require_owned_job(job_id, requesting_user_id)
        if original.status != JobStatus.FAILED:
            raise InvalidStateError(
                f"Job {job_id} is {original.status.value}, not failed — only a "
                "failed job can be retried."
            )
        if not is_retryable(original.error_code):
            raise InvalidStateError(
                f"Job {job_id}'s failure ({original.error_code}) is not retryable."
            )

        new_job = Job(
            id=None, project_id=original.project_id, config_id=original.config_id
        )
        created = self._jobs.create(new_job)
        assert created.id is not None
        queued = self._jobs.update_status(created.id, JobStatus.QUEUED)

        self._audit.record_event(
            actor_user_id=requesting_user_id,
            action=AuditAction.JOB_RETRIED,
            entity_type="job",
            entity_id=queued.id,
            details={
                "original_job_id": job_id,
                "original_error_code": original.error_code,
            },
        )
        return queued

    def _require_owned_job(self, job_id: int, requesting_user_id: int) -> Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise NotFoundError("Job", job_id)
        # A job has no user_id of its own — authorization goes through
        # its project's ownership (reuses ProjectService, not duplicated).
        self._projects.get_project(
            job.project_id, requesting_user_id=requesting_user_id
        )
        return job
