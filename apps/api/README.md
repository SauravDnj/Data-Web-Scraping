# apps/api

FastAPI backend. Control plane only: auth, validation, job creation,
record query. Never performs long-running collection work in-request —
that belongs to `workers/`.

Application code (app entry point, settings, endpoints, database
models, services) lands in later tasks (T014+) following
`docs/24_BACKEND_FILE_PLAN.md`. This directory currently contains only
the Python project/dependency setup from T010.

## Setup (T010)

From `apps/api/`:

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
```

## Commands

Run from `apps/api/` with the virtual environment active:

```bash
ruff format --check .   # formatting check
ruff format .            # auto-format
ruff check .              # lint
mypy .                     # type check
pytest                      # tests (repo-root tests/ via testpaths)
```

No `.env` or credentials are required to install or run these checks.

