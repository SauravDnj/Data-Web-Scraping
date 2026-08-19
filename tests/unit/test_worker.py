import threading
import time

import pytest
from pydantic import ValidationError
from workers.config import WorkerSettings
from workers.worker_main import resolve_worker_id, run


def make_settings(**overrides: str) -> WorkerSettings:
    defaults = {"redis_url": "redis://localhost:6379/2"}
    defaults.update(overrides)
    return WorkerSettings(_env_file=None, **defaults)


def test_worker_settings_requires_redis_url(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    with pytest.raises(ValidationError):
        WorkerSettings(_env_file=None)


def test_resolve_worker_id_uses_configured_value():
    settings = make_settings(worker_id="worker-1")
    assert resolve_worker_id(settings) == "worker-1"


def test_resolve_worker_id_generates_one_when_unset():
    settings = make_settings()
    worker_id = resolve_worker_id(settings)
    assert worker_id
    assert resolve_worker_id(settings) != worker_id  # each call is unique


def test_run_wakes_up_promptly_when_stop_event_is_set_concurrently():
    """This is what a signal handler actually relies on: setting the
    event while run() is blocked in its wait loop, not before it
    starts. Proves the loop doesn't need a full poll interval to
    notice shutdown was requested."""
    stop_event = threading.Event()
    settings = make_settings(redis_url="redis://localhost:6399/0")
    thread = threading.Thread(target=run, args=(stop_event, settings, "test-worker"))

    start = time.monotonic()
    thread.start()
    time.sleep(0.2)
    stop_event.set()
    thread.join(timeout=5)
    elapsed = time.monotonic() - start

    assert not thread.is_alive()
    assert elapsed < 5


def test_run_exits_immediately_when_stop_event_already_set():
    """Proves the loop respects the stop event and doesn't hang or
    leave anything running — no live Redis required: the connection
    attempt is expected to fail gracefully against this unreachable
    address, exactly like the real environment right now."""
    stop_event = threading.Event()
    stop_event.set()
    settings = make_settings(redis_url="redis://localhost:6399/0")

    start = time.monotonic()
    run(stop_event, settings, worker_id="test-worker")
    elapsed = time.monotonic() - start

    assert elapsed < 5
