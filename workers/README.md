# workers

Python worker process. Consumes queued jobs from Redis, executes the
permitted provider operation, and runs the normalize/validate/
deduplicate/persist pipeline — real queue consumption lands in
T060/T061; this currently has only the entry-point skeleton from T015
(config, logging, Redis connectivity check, graceful shutdown, and a
placeholder loop that processes nothing).

Runs inside `apps/api`'s virtual environment rather than having its
own (see `docs/16_MEMORY.md`) — `redis` and `pydantic-settings` are
already there, and this lets worker code depend on backend
domain/service interfaces once they exist (T030+) without a second
packaging setup.

## Run

From the repo root, with `apps/api`'s venv active (or invoked
directly):

```bash
apps/api/.venv/Scripts/python.exe -m workers.worker_main
```

Stop with Ctrl+C (SIGINT). SIGTERM is also handled, though Windows
doesn't reliably deliver it to a Python handler on external
termination the way POSIX (the Ubuntu deployment target) does.

## Commands

```bash
# from repo root
apps/api/.venv/Scripts/python.exe -m ruff format --check workers/
apps/api/.venv/Scripts/python.exe -m ruff check workers/
apps/api/.venv/Scripts/python.exe -m mypy --config-file workers/pyproject.toml workers
```

Tests live in the shared `tests/unit/test_worker.py` and run as part
of `apps/api`'s `pytest` (its `pythonpath` config makes `workers`
importable — see `apps/api/pyproject.toml`).
