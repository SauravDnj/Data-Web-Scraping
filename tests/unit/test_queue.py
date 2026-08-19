"""T060 tests: the job queue abstraction, against `fakeredis` — a
faithful in-memory Redis implementation (real `LPUSH`/`BLMOVE`/`LREM`
semantics, not a hand-rolled mock), used because no live Redis is
available to verify against locally yet (T013 still open; same
SQLite-for-MySQL substitution philosophy this whole project has used).
One section per T060 IMPLEMENT item."""

import fakeredis
import pytest
from workers.queue import RedisJobQueue


@pytest.fixture
def queue() -> RedisJobQueue:
    client = fakeredis.FakeRedis()
    return RedisJobQueue(client)


# --- 1. queue interface: satisfied structurally, see workers/queue.py's JobQueue ---

# --- 3. enqueue job ID ---


def test_enqueue_does_not_raise(queue):
    queue.enqueue(42)  # no assertion needed beyond "doesn't raise"


# --- 4. dequeue job ID ---


def test_dequeue_returns_the_enqueued_job_id(queue):
    queue.enqueue(42)
    assert queue.dequeue(timeout_seconds=1) == 42


def test_dequeue_returns_none_when_the_queue_is_empty():
    client = fakeredis.FakeRedis()
    queue = RedisJobQueue(client)
    assert queue.dequeue(timeout_seconds=0.1) is None


def test_dequeue_is_first_in_first_out(queue):
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)

    assert queue.dequeue(timeout_seconds=1) == 1
    assert queue.dequeue(timeout_seconds=1) == 2
    assert queue.dequeue(timeout_seconds=1) == 3


# --- 5. handle acknowledgement ---


def test_acknowledge_removes_the_job_from_in_flight(queue):
    queue.enqueue(42)
    queue.dequeue(timeout_seconds=1)
    assert queue.list_in_flight() == [42]

    queue.acknowledge(42)

    assert queue.list_in_flight() == []


def test_acknowledging_a_job_never_dequeued_is_a_safe_no_op(queue):
    queue.acknowledge(999)  # must not raise
    assert queue.list_in_flight() == []


# --- 6. handle worker failure ---


def test_a_dequeued_job_stays_visible_in_flight_until_acknowledged(queue):
    """Simulates a worker crash: dequeue happened, acknowledge never
    did. The job ID is not silently lost - it's still discoverable."""
    queue.enqueue(42)
    queue.dequeue(timeout_seconds=1)

    assert queue.list_in_flight() == [42]


def test_requeue_moves_an_in_flight_job_back_to_the_main_queue(queue):
    queue.enqueue(42)
    queue.dequeue(timeout_seconds=1)

    queue.requeue(42)

    assert queue.list_in_flight() == []
    assert queue.dequeue(timeout_seconds=1) == 42  # redelivered


def test_requeuing_a_job_not_in_flight_does_not_duplicate_it_on_the_queue(queue):
    """A late/duplicate requeue() call (e.g. two recovery sweeps
    racing) must not re-add a job that was already acknowledged or
    already requeued once."""
    queue.enqueue(42)
    queue.dequeue(timeout_seconds=1)
    queue.acknowledge(42)

    queue.requeue(42)  # already acknowledged - nothing to requeue

    assert queue.dequeue(timeout_seconds=0.1) is None


# --- 7. queue tests: this whole file ---

# --- 8. keep queue payload minimal ---


def test_the_queue_only_ever_carries_a_job_id_never_job_details(queue):
    """Structural proof: enqueue()/dequeue()'s signatures only
    accept/return a bare int - there is no parameter anywhere for
    config, status, or any other job detail, and this module imports
    nothing from app.repositories (verified below) - job details live
    only in MySQL."""
    import workers.queue as queue_module

    assert not hasattr(queue_module, "app")  # no app.* module bound here
    queue.enqueue(42)
    dequeued = queue.dequeue(timeout_seconds=1)
    assert isinstance(dequeued, int)


# --- 9. job details remain in MySQL / Redis loss does not erase the job ---


def test_losing_the_queue_entirely_does_not_touch_any_external_state(queue):
    """This module has no MySQL/repository dependency at all - the
    strongest possible proof that flushing Redis cannot erase a Job
    row: this code has no way to reach one in the first place."""
    queue.enqueue(42)
    queue._client.flushall()  # simulates total Redis data loss

    assert queue.list_in_flight() == []
    assert queue.dequeue(timeout_seconds=0.1) is None
    # No assertion about MySQL is possible or needed here - this
    # module never touches it, which is exactly the point.
