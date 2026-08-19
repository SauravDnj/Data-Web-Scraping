"""The single place that decides whether a job status transition is
legal. Database/service code (T032+) must call transition() rather
than assigning Job.status directly — that's what keeps invalid
transitions (e.g. completed -> running) impossible by construction
instead of merely undocumented."""

from app.domain.jobs import JobStatus

_ALLOWED_TRANSITIONS: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.DRAFT: frozenset({JobStatus.QUEUED, JobStatus.CANCELLED}),
    JobStatus.QUEUED: frozenset({JobStatus.RUNNING, JobStatus.CANCELLED}),
    JobStatus.RUNNING: frozenset(
        {
            JobStatus.PAUSED,
            JobStatus.COMPLETED,
            JobStatus.PARTIALLY_COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.PAUSED: frozenset({JobStatus.RUNNING, JobStatus.CANCELLED}),
    # Terminal — no legal transition leaves any of these. A job that
    # needs to run again is a new Job row, not a resurrected old one.
    JobStatus.COMPLETED: frozenset(),
    JobStatus.PARTIALLY_COMPLETED: frozenset(),
    JobStatus.FAILED: frozenset(),
    JobStatus.CANCELLED: frozenset(),
}

TERMINAL_STATUSES: frozenset[JobStatus] = frozenset(
    status for status, targets in _ALLOWED_TRANSITIONS.items() if not targets
)


class InvalidJobTransition(Exception):
    """Typed domain error — callers should catch this specifically,
    not a bare Exception, to convert it into an API error (T039+) or a
    worker-level failure classification (T044)."""

    def __init__(self, current: JobStatus, target: JobStatus) -> None:
        self.current = current
        self.target = target
        super().__init__(
            f"Cannot transition job from '{current.value}' to '{target.value}'."
        )


def is_legal_transition(current: JobStatus, target: JobStatus) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


def transition(current: JobStatus, target: JobStatus) -> JobStatus:
    """Returns `target` if the transition is legal, otherwise raises
    InvalidJobTransition. Does not mutate anything — this stays
    independent of SQLAlchemy/HTTP like the rest of app.domain;
    callers are responsible for persisting the returned value."""
    if not is_legal_transition(current, target):
        raise InvalidJobTransition(current, target)
    return target
