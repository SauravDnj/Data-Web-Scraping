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

T025 --- Record database. (T000-T002, T010, T011, T014, T015, T020-T024
complete. T012/T013 prepared but NOT verified — see below. T025 is
where the SQLite-substitution approach likely stops being appropriate
— dedup/canonical-key behavior deserves real MySQL verification.)

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

## Alembic foundation (T021) — also done without live MySQL

`apps/api/alembic.ini`: `sqlalchemy.url` deliberately blank (no
credential-shaped value, real or placeholder);
`database/migrations/env.py` sets it from `DATABASE_URL` via
`get_settings()` **only if not already configured** — this is what
lets `tests/integration/test_migrations.py` point Alembic at a
per-test temporary SQLite file via `Config.set_main_option(...)`
without needing `APP_SECRET`/`REDIS_URL` dummy env vars at all. Don't
"simplify" that `if not config.get_main_option(...)` guard away — it's
the whole reason the test doesn't need Settings() to succeed.

`script_location = %(here)s/../../database/migrations` (relative to
`alembic.ini`'s own location, so it resolves regardless of CWD).
`target_metadata = Base.metadata` from `app.db.base` — currently empty
(matches T020; real tables land T022+, at which point `env.py`'s
comment marks where to import those model modules so autogenerate
sees them).

Initial migration `3c36a83992e1_initial_no_tables_yet.py` is
deliberately a no-op (empty `upgrade()`/`downgrade()`) — proves the
Alembic harness itself (revision tracking, `alembic_version` table)
without inventing schema ahead of its task. Verified both manually
(`alembic upgrade head` → `alembic current` → `alembic downgrade base`
→ `alembic current`, against a temp SQLite file) and via the automated
`test_alembic_upgrade_and_downgrade_from_empty_database` test, which
asserts the `alembic_version` table directly.

**Scope boundary, deliberate**: `database/migrations/versions/*.py`
and `script.py.mako` are Alembic-generated and excluded from our
ruff/mypy enforcement (reformatting historical migrations after the
fact is bad practice anyway); `env.py` is hand-written and IS kept
ruff-clean (uses `../../database/migrations/env.py` as a target from
`apps/api/` — same trick as `workers/`).

**Still pending real MySQL**: this proves the migration *harness*
works, not that a real MySQL-dialect migration applies cleanly. Once
T012 lands, run `alembic upgrade head` against the real
`google_data_platform` database as a final confirmation — trivial
since there's still no real schema, but worth doing before T022 adds
one.

Verified locally: 19 passed, 1 skipped (the pre-existing T012-gated
MySQL test), ruff/mypy clean.

## Identity database (T022) — also done without live MySQL, plus a real cross-dialect bug found and fixed

`app/db/models/user.py`: `User` table matching
`docs/04_DATABASE_DESIGN.md` exactly (id, email unique, name nullable,
password_hash, status, created_at/updated_at). `UserStatus` is a plain
string-constant class (`active`/`disabled`/`pending`), not a DB ENUM —
matches every other VARCHAR(32) status column in the schema.
`app/core/security.py`: `hash_password`/`verify_password` (bcrypt) and
`normalize_email` (lowercase + trim) — deliberately NOT
"authentication service logic" (no login/tokens; that's T038), just
the primitives T022 needs so "password hash is never plaintext" is
testable now. `bcrypt>=4.1,<5.0` added to `apps/api/pyproject.toml`.

**Real bug found via the SQLite-testing approach, not a compromise**:
declaring `id` as plain `BigInteger` broke autoincrement under SQLite
— SQLite only rowid-aliases (auto-increments) a primary key typed
*exactly* `INTEGER`, not `BIGINT`. Fixed with SQLAlchemy's documented
cross-dialect idiom, now in `app/db/base.py` as `BigIntegerPK =
BigInteger().with_variant(Integer(), "sqlite")` — real `BIGINT` on
MySQL (matching the design doc), plain `INTEGER` (still
autoincrement-compatible) on SQLite. **Every future table's `id`
column must use `BigIntegerPK` from `app.db.base`, not a bare
`BigInteger`** — T023-T026 will hit the identical bug otherwise. This
is exactly the kind of real, portable issue the SQLite-substitution
strategy is supposed to catch before real MySQL is even involved.

Migration `9cb30c768410_create_users_table.py` autogenerated (had to
`alembic upgrade head` the temp DB to the prior no-op revision first,
or autogenerate refuses with "Target database is not up to date").
`app/db/models/__init__.py` now imports `User` so Base.metadata (and
thus autogenerate) sees it; `database/migrations/env.py` imports
`app.db.models` for the same reason.

Tests: `tests/unit/test_user_model.py` (create/retrieve, duplicate
normalized-email rejection via `IntegrityError`, password hash is
never plaintext + verifies correctly, email normalization) — all
against SQLite in-memory. `tests/integration/test_migrations.py`
extended: the migration itself (not just `create_all`) creates a real
`users` table with the unique constraint enforced, and downgrade
removes it — verified via raw `sqlite3`, not the ORM, to prove the
migration's actual DDL is correct independent of the model.

Verified locally: 24 passed, 1 skipped (T012-gated), ruff/mypy clean.

## Project database (T023)

`app/db/models/project.py` (`Project`, `ProjectStatus`) and
`app/db/models/collection_config.py` (`CollectionConfig`) match
`docs/04_DATABASE_DESIGN.md`. `CollectionConfig` is one immutable row
per version — never updated in place, a new row per version instead
(hard-enforced later by the service layer, T034; for now this is a
convention plus a `UniqueConstraint("project_id", "version")` so two
versions can never collide).

**Second real cross-dialect bug found, fixed at the engine level (not
just worked around per-test)**: SQLite doesn't enforce foreign keys
unless `PRAGMA foreign_keys=ON` is set per-connection — MySQL always
enforces them. Without this, `test_project_requires_an_existing_user`
would have silently passed for the wrong reason (SQLite just allowing
the orphan insert). Fixed in `app/db/session.py:build_engine()` with a
`sqlalchemy.event.listens_for(engine, "connect")` hook that runs the
pragma for any SQLite engine — automatic for every future SQLite-based
test, not something each test file needs to remember.

**Refactored the SQLite test fixture into `tests/unit/conftest.py`**
(`sqlite_engine`) — it had been copy-pasted into `test_db_session.py`
and `test_user_model.py`; T023 would have been a third copy.
`test_db_session.py`'s `_Widget` throwaway model and every real model
now share one `Base`, so `Base.metadata.create_all()` in the fixture
creates the whole schema every time, not just one table — harmless,
but worth knowing if a test seems to see tables it didn't expect.

Migration `88fb5b35267b_create_projects_and_collection_configs_.py`
autogenerated correctly (FKs to `users`/`projects`, both indexes from
`docs/04_DATABASE_DESIGN.md`'s index strategy, the unique constraint).

7 new tests in `tests/unit/test_project_and_config_models.py`: project
belongs to user (+ FK rejection for a nonexistent user — this is what
caught the SQLite FK-enforcement gap), config belongs to project,
historical versions retained with unmutated `config_json`, active
version selected deterministically via `.one()`, no-active-version is
a clean `NoResultFound` not a crash, duplicate version number
rejected. Plus a migration-level test confirming the DDL creates/drops
both tables.

Verified locally: 32 passed, 1 skipped (T012-gated), ruff/mypy clean.

## Job database (T024)

`app/db/models/job.py`: `Job` (matches
`docs/04_DATABASE_DESIGN.md`, `status` uses the canonical `JobStatus`
resolved at T000) and `JobRun` (one row per execution attempt —
`worker_id`/`attempt`/`heartbeat_at` exist specifically to support
T062 heartbeat / T065 recovery later; a narrower `JobRunStatus` since a
single run doesn't have draft/queued/paused states). Counters
(`total_units`, `successful_units`, etc.) all default to `0`, never
`NULL`, so aggregation is always safe.

Two indexes on `jobs`, deliberately: `(project_id, status,
requested_at)` from the design doc's index strategy (project-scoped
dashboard views), plus `(status, requested_at)` added here for
worker/scheduler polling ("show me queued jobs" is project-agnostic,
so it needs `status` as the leading column — the project-scoped index
doesn't serve that query well). Both are justified by distinct, named
access patterns, not blind guessing — but T027 should still confirm
with real query plans once MySQL is available.

Migration `89d4d3766467_create_jobs_and_job_runs_tables.py`
autogenerated. 7 new tests in `tests/unit/test_job_models.py`: a job
pins to one specific config *version* (not "whatever's active now" —
deliberately references the older of two versions to prove this), FK
rejection for nonexistent project/config, safe counter defaults, full
lifecycle timestamp progression (`requested_at` → `started_at` →
`finished_at`), a job_run records an attempt, FK rejection for
nonexistent job, and retries get their own new `job_run` row rather
than mutating the previous attempt. Plus a migration-level table test.

Verified locally: 40 passed, 1 skipped (T012-gated), ruff/mypy clean.

**Note for T025**: records/dedup is where the honest SQLite-substitution
approach this project has used through T020-T024 (2 real bugs caught:
BigInteger autoincrement, FK enforcement) likely stops applying —
`canonical_key` uniqueness-at-project-scope and dedup behavior are
worth verifying against real MySQL specifically, not just proven
"a temporary database can be created." Re-read T025's exact acceptance
criteria before assuming the same pattern still holds.

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
