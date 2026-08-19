"""T031 tests: the full legal transition matrix, representative
illegal transitions, and the literal acceptance criteria — pure
Python, no database."""

import pytest
from app.domain.job_state_machine import (
    TERMINAL_STATUSES,
    InvalidJobTransition,
    is_legal_transition,
    transition,
)
from app.domain.jobs import JobStatus

ALLOWED_TRANSITIONS = [
    (JobStatus.DRAFT, JobStatus.QUEUED),
    (JobStatus.DRAFT, JobStatus.CANCELLED),
    (JobStatus.QUEUED, JobStatus.RUNNING),
    (JobStatus.QUEUED, JobStatus.CANCELLED),
    (JobStatus.RUNNING, JobStatus.PAUSED),
    (JobStatus.RUNNING, JobStatus.COMPLETED),
    (JobStatus.RUNNING, JobStatus.PARTIALLY_COMPLETED),
    (JobStatus.RUNNING, JobStatus.FAILED),
    (JobStatus.RUNNING, JobStatus.CANCELLED),
    (JobStatus.PAUSED, JobStatus.RUNNING),
    (JobStatus.PAUSED, JobStatus.CANCELLED),
]

REPRESENTATIVE_ILLEGAL_TRANSITIONS = [
    (JobStatus.DRAFT, JobStatus.RUNNING),  # must queue first
    (JobStatus.QUEUED, JobStatus.PAUSED),  # only a running job can pause
    (JobStatus.QUEUED, JobStatus.COMPLETED),
    (JobStatus.PAUSED, JobStatus.COMPLETED),  # must resume to running first
    (JobStatus.PAUSED, JobStatus.FAILED),
    (JobStatus.COMPLETED, JobStatus.RUNNING),
    (JobStatus.COMPLETED, JobStatus.QUEUED),
    (JobStatus.FAILED, JobStatus.COMPLETED),
    (JobStatus.FAILED, JobStatus.RUNNING),
    (JobStatus.CANCELLED, JobStatus.RUNNING),
    (JobStatus.CANCELLED, JobStatus.QUEUED),
    (JobStatus.PARTIALLY_COMPLETED, JobStatus.RUNNING),
]


@pytest.mark.parametrize("current,target", ALLOWED_TRANSITIONS)
def test_every_allowed_transition_succeeds(current, target):
    assert is_legal_transition(current, target)
    assert transition(current, target) == target


@pytest.mark.parametrize("current,target", REPRESENTATIVE_ILLEGAL_TRANSITIONS)
def test_representative_illegal_transitions_are_rejected(current, target):
    assert not is_legal_transition(current, target)
    with pytest.raises(InvalidJobTransition):
        transition(current, target)


def test_completed_cannot_become_running():
    with pytest.raises(InvalidJobTransition):
        transition(JobStatus.COMPLETED, JobStatus.RUNNING)


def test_failed_cannot_silently_become_completed():
    with pytest.raises(InvalidJobTransition):
        transition(JobStatus.FAILED, JobStatus.COMPLETED)


def test_pause_and_resume_are_explicit_and_symmetric():
    assert transition(JobStatus.RUNNING, JobStatus.PAUSED) == JobStatus.PAUSED
    assert transition(JobStatus.PAUSED, JobStatus.RUNNING) == JobStatus.RUNNING


def test_every_terminal_status_has_no_legal_transitions():
    for status in TERMINAL_STATUSES:
        for target in JobStatus:
            assert not is_legal_transition(status, target)


def test_terminal_statuses_are_exactly_the_four_outcome_states():
    assert {
        JobStatus.COMPLETED,
        JobStatus.PARTIALLY_COMPLETED,
        JobStatus.FAILED,
        JobStatus.CANCELLED,
    } == TERMINAL_STATUSES


def test_invalid_transition_error_identifies_current_and_target():
    with pytest.raises(InvalidJobTransition) as excinfo:
        transition(JobStatus.COMPLETED, JobStatus.RUNNING)

    assert excinfo.value.current == JobStatus.COMPLETED
    assert excinfo.value.target == JobStatus.RUNNING
    assert "completed" in str(excinfo.value)
    assert "running" in str(excinfo.value)


def test_every_status_pair_is_a_defined_decision():
    """Every (current, target) pair over all JobStatus members must be
    handled — no KeyError, no silently-unhandled status. A status
    missing from the transition table would be a real correctness bug,
    not just an untested one."""
    for current in JobStatus:
        for target in JobStatus:
            assert isinstance(is_legal_transition(current, target), bool)


def test_no_status_transitions_to_itself():
    """Re-entering the same status isn't a 'transition' — callers that
    want idempotent no-ops should check equality before calling
    transition(), not rely on it accepting a same-status no-op."""
    for status in JobStatus:
        assert not is_legal_transition(status, status)
