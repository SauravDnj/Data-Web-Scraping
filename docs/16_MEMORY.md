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

T021 --- Alembic foundation. (T000-T002, T010, T011, T014, T015, T020
complete. T012/T013 prepared but NOT verified — see below.)

## T012 (MySQL) / T013 (Redis) — blocked on user action

Not marked complete. MySQL 9.7 is installed and running as a Windows
service, but this agent does not have (and should not be given) the
root password — `scripts/mysql_dev_setup.sql` is ready for the user to
run themselves. Redis has no official Windows build; user ruled out
WSL (production target is an Ubuntu VPS instead) and is deciding
between Memurai (native, no WSL) or skipping local Redis entirely.
Resume: once the user confirms MySQL is set up, run
`mysql -u app_user -p google_data_platform -e "SELECT 1;"` to verify
and mark T012 complete; once Redis is reachable (or the user says
skip), run `python scripts/redis_ping.py` and mark T013 accordingly.

## FastAPI skeleton (T014)

`apps/api/app/main.py` — `create_app()` factory (+ module-level `app`
for `uvicorn app.main:app`). `GET /health` (process only, always 200),
`GET /ready` (checks MySQL via direct pymysql connect + `SELECT 1`,
and Redis via redis-py `PING`, independently — deliberately not using
the SQLAlchemy engine T020 will add later). Both checks are FastAPI
dependencies (`check_database`/`check_redis` in
`app/core/dependencies.py`), overridable via
`app.dependency_overrides` — this is how tests cover the
healthy/unhealthy matrix without needing live infra.

`app/core/config.py`: pydantic-settings `Settings`, required
`app_secret`/`database_url`/`redis_url` (fails clearly if missing),
optional `google_maps_api_key` (not consumed until the provider tasks).
`app/core/logging.py`: custom JSON formatter (no new dependency),
includes `request_id` via a contextvar set by
`app/core/middleware.py`'s `RequestIdMiddleware` (echoes/generates
`X-Request-Id`). `app/core/errors.py`: `ApiError` base class + handlers
producing the `{"error": {...}, "request_id": ...}` envelope for
`ApiError`, validation errors, and any unhandled exception (logged
server-side, never leaked to the client).

Added `types-PyMySQL` to the `dev` extra (mypy needs it for
`pymysql` stubs).

Verified locally: 9/9 tests pass (unit config validation +
integration health/ready with dependency overrides), ruff
format/lint clean, mypy clean, and a real manual run
(`uvicorn app.main:app`) — `/health` → 200, `/ready` → 503 with
correct per-dependency detail and no credential leakage (MySQL/Redis
are genuinely not set up yet, so this is the real, expected failure
path), `X-Request-Id` header present. Server stopped after
verification.

Known minor issue (not blocking): `starlette.testclient` emits a
`StarletteDeprecationWarning` suggesting an `httpx2` package — left
as-is since it's an unfamiliar/very new package and tests pass; revisit
if it starts failing instead of warning.

## Worker skeleton (T015)

`workers/worker_main.py`: loads `WorkerSettings` (redis_url required,
worker_id optional/auto-generated as `hostname-<8 hex chars>`),
configures JSON logging (re-exported from `app.core.logging` — see
below), installs SIGINT/SIGTERM handlers that set a `threading.Event`,
attempts a Redis PING (logs healthy/unhealthy either way, never
crashes on failure), then loops on `stop_event.wait(timeout=5)` until
signaled — a placeholder only, no real job consumption until T060/T061.

**No separate `workers/pyproject.toml` package** — the worker runs
inside `apps/api`'s venv (redis/pydantic-settings already installed
there), which is also how it will reach backend domain/service
interfaces later per `docs/25_WORKER_FILE_PLAN.md`'s "should depend on
backend domain/service interfaces rather than duplicating business
logic." `apps/api/pyproject.toml` gained
`[tool.pytest.ini_options] pythonpath = ["../.."]` so `import workers`
resolves in tests without installing it.

`workers/pyproject.toml` DOES exist but only holds `[tool.ruff]` /
`[tool.mypy]` config (no `[project]`/`[build-system]` — not
installable). Required because `workers/queue.py` collides with the
stdlib `queue` module name under mypy's default file-to-module
resolution; fixed with `explicit_package_bases = true` +
`mypy_path = "apps/api"`. **Important**: that `mypy_path` is relative
to the CWD mypy is invoked from (repo root, via
`--config-file workers/pyproject.toml`), not relative to the config
file itself — the exact command is in `workers/README.md`. Get this
wrong and mypy silently can't resolve `app.core.logging`.

**Caveat found during testing**: passing an explicit test file path to
`pytest` from `apps/api/` (e.g. `pytest ../../tests/unit/test_worker.py`)
changes pytest's rootdir/config detection and breaks the `pythonpath`
resolution (`ModuleNotFoundError: workers`). The bare `pytest` command
apps/api/README.md documents (and CI uses) is unaffected — always
verified working. Don't pass explicit file paths when testing worker
code; use `-k <name>` for selection instead if needed.

Verified locally: 14/14 tests pass (2 new: stop-event-already-set and
stop-event-set-concurrently-from-another-thread, the latter proving
the actual signal-handler wakeup mechanism), ruff/mypy clean for
`workers/`. Manually ran `python -m workers.worker_main`: logged
startup, correctly reported Redis unavailable (real environment, T013
still pending) without crashing, and `kill -TERM` produced a clean
exit with no orphaned process.

## SQLAlchemy foundation (T020) — done without live MySQL

`app/db/base.py`: `Base(DeclarativeBase)` with an explicit
`NAMING_CONVENTION` (ix/uq/ck/fk/pk) so Alembic autogenerate (T021)
produces stable migrations. `app/db/session.py`: `build_engine()` /
`build_session_factory()` are plain factories (not singletons) so
tests can point them at SQLite; `get_engine()`/`get_session_factory()`
are the app's `lru_cache`'d singletons bound to `settings.database_url`.
`session_scope()` is the transaction boundary (commit on success,
rollback + re-raise on failure, always close); `get_db()` wraps it as
a FastAPI dependency. `app/db/models/` is an empty package — business
models land in T022-T026.

**Verified without a live MySQL connection, by design**: T020's own
acceptance text ("test can create a temporary schema") doesn't specify
which database, so `tests/unit/test_db_session.py` proves the actual
engine/session/Base/naming-convention plumbing against a real
temporary database — SQLite in-memory (`StaticPool`,
`check_same_thread=False`) — including rollback-on-error and the
naming convention actually landing on a real constraint
(`pk_test_widgets`). `tests/integration/test_db_connection_errors.py`
proves "connection errors are understandable" against a
deterministically-unreachable target (127.0.0.1:1, not the local dev
MySQL — so this test's result doesn't depend on T012's progress), and
also checks no credential leaks into the error message.

**Self-activating MySQL check**: `tests/integration/test_db_mysql.py`
probes the real configured `DATABASE_URL` and `pytest.mark.skipif`s
cleanly if unreachable (currently: skipped, T012 not done). Once T012
lands, this starts running for real with no code change — it doubles
as T012's own regression test. Run it after MySQL is set up to get
genuine MySQL-dialect confirmation, not just the SQLite proof above.

Verified locally: 18 passed, 1 skipped (as expected), ruff/mypy clean.

## Next.js environment (T011)

`apps/web` scaffolded with `create-next-app` (Next.js 16.3.1, React
19.2, App Router, TypeScript strict, Tailwind CSS v4, ESLint flat
config extending `eslint-config-next`). Added on top: `typecheck`
(`tsc --noEmit`) and `test`/`test:watch` (Vitest + React Testing
Library, jsdom) npm scripts — `test` runs `vitest run` (single pass,
not watch) specifically so CI's `npm test --if-present` doesn't hang.
`no-console` (warn, allow warn/error) added to ESLint.

Client/server config separation: `lib/api/config.ts` reads only
`NEXT_PUBLIC_API_BASE_URL` (safe for the browser bundle);
`lib/api/client.ts` is a typed fetch wrapper matching the
`{data, request_id}` / `{error, request_id}` envelope from
`docs/05_API_DESIGN.md`. The `server-only` package is installed for
when a real server-only secret is needed later — no module uses it yet
since none is needed at this stage.

`app/error.tsx`, `app/global-error.tsx`, `app/loading.tsx` added
(Next.js 16 file-convention error/loading UI — verified against the
bundled `node_modules/next/dist/docs/` since Next 16 warns it may
differ from training data; the error/loading conventions used here are
unchanged from what's documented there).

**Important**: Next.js only auto-loads `.env*` files from `apps/web/`
itself, not the repo root — added `apps/web/.env.example` in addition
to the root one (both list `NEXT_PUBLIC_API_BASE_URL`).

Verified locally: clean `npm install`, `npm run lint` (pass),
`npm run typecheck` (pass), `npm test` (2 passed), `npm run build`
(production build succeeds), and `npm run dev` actually serves the
page (curled http://localhost:3000, got 200 with expected content),
then the dev server process was stopped.

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
