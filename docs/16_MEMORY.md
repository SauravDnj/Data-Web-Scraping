# Persistent Project Memory

## Product

A local-first data collection platform focused primarily on Google Maps
Platform workflows.

## User objective

Build a complete application rather than a single scraper script.

## Primary workflow

``` text
Project
 → Configuration
 → Validation
 → Job
 → Queue
 → Worker
 → Provider
 → Normalize
 → Validate
 → Deduplicate
 → MySQL
 → Dashboard
 → Export
```

## Technology decisions

-   Next.js
-   TypeScript
-   FastAPI
-   Python
-   SQLAlchemy
-   Alembic
-   MySQL
-   Redis
-   Playwright only where appropriate/permitted
-   Pandas
-   Pytest
-   Git

## Development decision

Start without Docker.

## Architecture decision

Use provider adapters so Google-specific code is isolated.

## Data decision

MySQL is the durable system of record.

## Queue decision

Redis is coordination only.

## Safety decision

Do not bypass CAPTCHA, anti-bot, authentication, rate limits, or other
access controls.

## Current phase

Phase 1 (Local foundation).

## Current task

T011 --- Next.js environment. (T000, T001, T002, T010 complete.)

## Python environment (T010)

`apps/api/pyproject.toml`: FastAPI, uvicorn, SQLAlchemy 2.x, Alembic,
PyMySQL, redis-py, pydantic + pydantic-settings; dev extra: pytest,
pytest-asyncio, httpx, ruff, mypy. Editable install:
`pip install -e ".[dev]"` from `apps/api/`, Python >=3.12 (matches CI's
3.12 pin; local machine has 3.14, both fine).

**Important repo-layout note**: `tests/` (root-level, per coding
standards) is TWO directories above `apps/api/pyproject.toml`, so its
`[tool.pytest.ini_options] testpaths` is `["../../tests"]`, not
`["../tests"]` — verified locally (`../tests` silently found nothing
and fell back to recursive discovery). If a future task adds another
per-app pyproject.toml, recompute this relative path from that file's
actual location, don't copy the value blindly.

Verified locally: clean venv install succeeds with no errors, `pytest`
(2 passed), `ruff format --check`, `ruff check`, and `mypy` all pass
from a clean environment.

## CI (T002)

`.github/workflows/ci.yml`: two jobs (backend, frontend), each detects
whether its app manifest exists (`apps/api/pyproject.toml`,
`apps/web/package.json`) and no-ops with a message if not, so CI is
green from a clean checkout right now and activates automatically once
T010/T011 land — no CI file edit needed then. Pinned: Python 3.12,
Node 20.

**Contract T010 must satisfy:** `apps/api/pyproject.toml` installable
via `pip install -e ".[dev]"`, with `ruff`, `mypy`, `pytest` in the
`dev` extra; `ruff format --check .`, `ruff check .`, `mypy .`,
`pytest` must all run from `apps/api/`.

**Contract T011 must satisfy:** `apps/web/package.json` with npm
scripts named exactly `lint`, `typecheck`, and (optional) `test`,
runnable via `npm run lint` / `npm run typecheck` / `npm test
--if-present` from `apps/web/`.

## Coding standards

Established at T001 in `docs/CODING_STANDARDS.md`. Key picks: Black +
Ruff + mypy for Python; strict TypeScript + ESLint (next/core-web-vitals
+ typescript-eslint); snake_case JSON field names in the API (no
camelCase alias layer); Conventional Commits; `task/T0NN-slug` branch
names. Actual tool config files land in T010 (`apps/api`) and T011
(`apps/web`) respectively so they don't fight those tasks'
scaffolding.

## Repository

Git initialized locally; remote `origin` =
https://github.com/SauravDnj/Data-Web-Scraping.git (empty at time of
first push). Layout created: `apps/web`, `apps/api`, `workers`, `tests`,
`database`, `scripts`, `docs`.

## Resolved design decisions (recorded at T000)

The docs pack contained several unreconciled disagreements across
different files. Resolved as follows so later tasks are unambiguous:

-   **Backend layout**: use `apps/api` (matches T000_PROMPT.md and
    `02_SYSTEM_ARCHITECTURE.md`), not a root-level `backend/`. Internal
    module breakdown when scaffolded (T014+) follows
    `docs/24_BACKEND_FILE_PLAN.md`:
    `apps/api/app/{api,core,db,domain,services,repositories,providers,pipeline,schemas}`.
-   **Job state machine**: canonical states are
    `draft → queued → running → {completed, partially_completed,
    failed, cancelled, paused}`, with `paused` re-entrant to `running`.
    Apply this in T031 (job state machine) and T024 (job database).
-   **Provider interface naming**: use the generic `ProviderAdapter`
    contract (`validate_config`, `estimate`, `collect`, `normalize`,
    `classify_error`); `GoogleMapsProvider` (T041--T044) implements
    this contract exactly rather than using its own differently-named
    methods.
-   **Dedup canonical key scope**: include `project_scope` in the
    canonical key (`project_scope + provider + provider_id`) to avoid
    cross-project collisions. Apply in T052 (canonical identity).

## Last decision

Build the platform incrementally and keep documentation synchronized
with implementation.
