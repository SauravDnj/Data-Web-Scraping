# Completed Work

## Documentation pack

Status: COMPLETE

Verified outputs:

-   system explanation;
-   architecture;
-   requirements;
-   database design;
-   API design;
-   UI design;
-   provider workflow;
-   data pipeline;
-   worker design;
-   security;
-   testing;
-   task backlog;
-   task prompt template;
-   Claude Code master prompt;
-   progress/memory/work tracking.

## Implementation

### T000 --- Repository bootstrap

Status: COMPLETE

Evidence:

-   Git repository initialized; remote `origin` set to
    https://github.com/SauravDnj/Data-Web-Scraping.git.
-   Repository tree created: `apps/web`, `apps/api`, `workers`, `tests`,
    `database`, `scripts`, `docs` (existing).
-   Root `README.md` explains the product, layout, stack, and boundary.
-   `.gitignore` covers Python, Node, IDE files, `.env*` (except
    `.env.example`), logs, local databases, build output, and generated
    exports.
-   `.env.example` created with placeholders only (`APP_ENV`,
    `APP_SECRET`, `DATABASE_URL`, `REDIS_URL`, `GOOGLE_MAPS_API_KEY`,
    `FRONTEND_ORIGIN`, `LOG_LEVEL`) matching
    `docs/26_ENVIRONMENT_AND_CONFIG.md`.
-   Root `package.json` added as minimal repo metadata (no dependencies,
    no scripts).
-   Each new top-level directory has a placeholder `README.md` stating
    its purpose and which future task populates it.
-   No business logic, database schema, or provider code added.
-   `git status`/`git add -A` reviewed: only intentional files staged,
    no secret-like values.

Next task: T001 --- Coding standards.

### T001 --- Coding standards

Status: COMPLETE

Evidence:

-   `docs/CODING_STANDARDS.md` created, covering all 14 required areas:
    Python formatting/linting/typing (Black, Ruff, mypy), TypeScript
    strictness/linting, React/Next.js component conventions, API
    naming (REST, snake_case JSON, envelope), database naming,
    migration rules, test naming/placement, structured logging,
    Git branch/commit conventions, import ordering, error-handling
    conventions per layer, provider-adapter/secrets rules.
-   `.editorconfig` and `.gitattributes` (LF normalization) added at
    root — repo-wide, tool-agnostic, verified with `git status`/`git
    add` (no unexpected diffs).
-   `CONTRIBUTING.md` added at root pointing to the task protocol and
    coding standards.
-   Actual linter/formatter config files (pyproject.toml tool
    sections, ESLint) deliberately deferred to T010/T011 so they don't
    fight those tasks' scaffolding tools; exact rules are fully
    specified in `docs/CODING_STANDARDS.md` for those tasks to apply.
-   No application code existed to refactor; none was added. No new
    runtime dependencies added.
-   Local tooling check: Python 3.14 and Node 25 confirmed available
    for when T010/T011 need them.

Next task: T002 --- CI baseline.

### T002 --- CI baseline

Status: COMPLETE

Evidence:

-   `.github/workflows/ci.yml` created: `backend` job (Python 3.12,
    Ruff format check, Ruff lint, mypy, pytest) and `frontend` job
    (Node 20, npm lint/typecheck/test), each running from a clean
    checkout on push/PR/workflow_dispatch.
-   Both jobs detect whether their app manifest exists yet
    (`apps/api/pyproject.toml`, `apps/web/package.json`) and skip with
    a clear message if not — deterministic green build in the current
    minimal repository, no deploy/production DB/live Google API calls,
    no credentials stored.
-   Verified locally: manifest-detection shell logic runs correctly
    (both report "not yet present", as expected before T010/T011), and
    the workflow YAML parses as valid YAML.
-   Exact contract T010/T011 must satisfy (dependency-group name,
    script names) recorded in `docs/16_MEMORY.md` so CI activates
    without further edits.

Next task: T010 --- Python environment.

### T010 --- Python environment

Status: COMPLETE

Evidence:

-   `apps/api/pyproject.toml`: FastAPI, uvicorn, SQLAlchemy, Alembic,
    PyMySQL, redis-py, pydantic/pydantic-settings; `dev` extra with
    pytest, pytest-asyncio, httpx, ruff, mypy. Ruff/mypy config
    included (satisfies the CI contract from T002).
-   `apps/api/app/__init__.py` — minimal importable package (no
    business logic).
-   `tests/unit/test_environment.py` — smoke test verifying the
    package and all core dependencies import correctly.
-   `apps/api/README.md` updated with venv setup and command
    reference; root `README.md` Development section updated.
-   Verified locally end-to-end: `python -m venv .venv` →
    `pip install -e ".[dev]"` (clean install, no errors) →
    `pytest` (2 passed) → `ruff format --check .` (pass) →
    `ruff check .` (pass) → `mypy .` (pass). `.venv/` correctly
    excluded from Git (`git status` clean of it).
-   Fixed a relative-path bug in `testpaths` discovered during local
    verification (see docs/16_MEMORY.md).
-   No Google credentials, no browser automation, no scraping
    dependencies added.

Next task: T011 --- Next.js environment.

### T011 --- Next.js environment

Status: COMPLETE

Evidence:

-   `apps/web` scaffolded (Next.js 16.3.1, TypeScript strict, Tailwind
    v4, ESLint flat config + `no-console` rule, App Router).
-   `typecheck`, `test`, `test:watch` npm scripts added; Vitest +
    React Testing Library + jsdom configured
    (`vitest.config.mts`/`vitest.setup.ts`); `test` runs once (not
    watch) for CI compatibility.
-   Root layout metadata updated; minimal placeholder home page
    (no business logic); `app/error.tsx`, `app/global-error.tsx`,
    `app/loading.tsx` added.
-   `lib/api/config.ts` (client-safe `NEXT_PUBLIC_API_BASE_URL` only)
    and `lib/api/client.ts` (typed fetch wrapper matching the API
    envelope) establish the client/server config boundary; no
    provider credentials, no direct MySQL access, no collection logic.
-   `apps/web/.env.example` added (Next.js only reads `.env*` from its
    own directory); root `.env.example` also updated.
-   Verified locally end-to-end: `npm install` (clean), `npm run lint`
    (pass), `npm run typecheck` (pass), `npm test` (2/2 passed),
    `npm run build` (production build succeeds), `npm run dev` (dev
    server actually served the page, verified via curl, then stopped).
-   Fixed `apps/web/.gitignore` to allow-list `.env.example` (its
    default `.env*` pattern would otherwise have excluded it, unlike
    root `.gitignore`).

Next task: T012 --- MySQL local setup.

### T012 --- MySQL local setup: PREPARED, NOT COMPLETE

`scripts/mysql_dev_setup.sql`/`mysql_dev_reset.sql` written and
documented in `docs/10_LOCAL_SETUP.md`. Blocked on the user running
the setup script with their own MySQL admin access (this agent does
not have the root password). Will verify and mark complete once
confirmed.

### T013 --- Redis local setup: PREPARED, NOT COMPLETE

`scripts/redis_ping.py` written, verified to fail clearly (exit 1,
clear message) with no Redis running. Blocked on a user decision
(Memurai vs. skip local Redis) since Redis has no native Windows
build and WSL is ruled out.

### T014 --- FastAPI skeleton

Status: COMPLETE

Evidence:

-   `apps/api/app/main.py`, `app/core/{config,logging,middleware,
    errors,dependencies,request_context}.py`, `app/api/health.py`,
    `app/api/v1/__init__.py` — app factory, structured JSON logging,
    request ID middleware, CORS scoped to `FRONTEND_ORIGIN`, exception
    handling foundation, `/health` and `/ready` endpoints, independent
    MySQL/Redis readiness checks.
-   9 tests added (`tests/unit/test_config.py`,
    `tests/integration/test_health.py`, `test_ready.py`) covering
    settings validation and both the healthy and dependency-failure
    readiness paths via `app.dependency_overrides` — no live infra
    required for the automated suite.
-   Verified locally: full test suite (9/9), `ruff format --check`,
    `ruff check`, `mypy` all pass. Manually ran the real app
    (`uvicorn app.main:app`): `/health` → 200, `/ready` → 503 with
    correct, credential-free per-dependency detail against the actual
    (currently unset-up) local MySQL/Redis, `X-Request-Id` header
    present on responses. Server stopped after verification.
-   No provider calls, no auth business logic, no SQL in route
    handlers.

Next task: T015 --- Worker skeleton.

### T015 --- Worker skeleton

Status: COMPLETE

Evidence:

-   `workers/worker_main.py`, `workers/config.py`, `workers/queue.py`,
    `workers/observability/logging.py` — entry point, settings,
    Redis connectivity check, structured logging (reused from
    `app.core.logging`), SIGINT/SIGTERM handling via a
    `threading.Event`, placeholder loop (no real job consumption).
-   4 tests added to `tests/unit/test_worker.py`: settings validation,
    worker ID resolution (configured vs. auto-generated), and two
    shutdown-behavior tests (stop-event-pre-set, and
    stop-event-set-concurrently-from-another-thread — the latter is
    what a real signal handler relies on).
-   `apps/api/pyproject.toml` gained a `pythonpath` entry so `workers`
    resolves in tests without a separate installable package;
    `workers/pyproject.toml` added for ruff/mypy config only (not a
    package) — see `docs/16_MEMORY.md` for why `workers/queue.py`
    needed `explicit_package_bases`.
-   Verified locally: 14/14 tests pass (full suite), ruff/mypy clean
    for `workers/`, and a real manual run — `python -m
    workers.worker_main` logged startup, correctly reported the
    actual (still-pending) Redis as unavailable without crashing, and
    a `kill -TERM` produced a clean exit with no orphaned process.
-   No provider calls, no job-state modification, no scraping.

Next task: T012/T013 (blocked on user action) then T020 --- SQLAlchemy
foundation.

### T020 --- SQLAlchemy foundation

Status: COMPLETE

Evidence:

-   `apps/api/app/db/base.py` (`Base` + explicit naming convention),
    `app/db/session.py` (`build_engine`/`build_session_factory`
    factories, `get_engine`/`get_session_factory` cached singletons,
    `session_scope` transaction boundary, `get_db` FastAPI
    dependency), `app/db/models/` (empty, populated T022-T026).
-   4 new tests: `tests/unit/test_db_session.py` (temporary-schema
    creation, rollback-on-error, naming convention on a real
    constraint — all against SQLite in-memory, a real if
    non-MySQL database) and
    `tests/integration/test_db_connection_errors.py` (connection
    errors are clear and credential-free, against a
    deterministically-unreachable target).
-   `tests/integration/test_db_mysql.py` added: skips cleanly now
    (MySQL/app_user not set up — T012 pending), will run for real once
    T012 lands, with no code change needed.
-   Verified locally: 18 passed, 1 skipped as expected, ruff/mypy
    clean.
-   No business models created, no provider code, no live MySQL
    dependency for this task's own verification (deliberate — see
    docs/16_MEMORY.md for why that's a legitimate reading of the
    acceptance criteria).

Next task: T021 --- Alembic foundation (this one genuinely needs a
live MySQL connection to run a real migration against — likely the
next hard stop pending T012).

### T021 --- Alembic foundation

Status: COMPLETE

Evidence:

-   `apps/api/alembic.ini` (blank `sqlalchemy.url`, no credentials),
    `database/migrations/env.py` (URL from `DATABASE_URL` unless
    already configured — the latter is what makes this testable
    without live MySQL), `target_metadata = Base.metadata`.
-   Initial no-op migration
    (`3c36a83992e1_initial_no_tables_yet.py`) proves the harness
    without inventing schema ahead of T022+.
-   `tests/integration/test_migrations.py`: automated
    upgrade-head/downgrade-base round-trip against a temporary SQLite
    file, asserting the `alembic_version` table directly.
-   `database/migrations/README.md`, `database/README.md` document
    the upgrade/downgrade/history/revision commands.
-   Verified locally: manual round-trip
    (upgrade → current → downgrade → current) against a temp SQLite
    DB, plus the automated test; full suite 19 passed, 1 skipped
    (T012-gated), ruff/mypy clean.
-   Same honest caveat as T020: this proves the migration harness, not
    a real MySQL-dialect migration — trivial to re-confirm once T012
    lands since there's still no real schema yet.

Next task: T012/T013 (blocked on user action) then T022 --- Identity
database (first real business table — will need real MySQL to fully
verify per its own acceptance criteria, unlike T020/T021).

### T022 --- Identity database

Status: COMPLETE

Evidence:

-   `apps/api/app/db/models/user.py` (`User` table matching
    `docs/04_DATABASE_DESIGN.md`), `app/core/security.py`
    (bcrypt password hashing + email normalization, not auth service
    logic). `bcrypt` added as a dependency.
-   **Found and fixed a real cross-dialect bug**: `BigInteger` primary
    keys don't autoincrement under SQLite (only exact `INTEGER` does).
    Fixed via SQLAlchemy's `with_variant` idiom
    (`app/db/base.py:BigIntegerPK`) — real `BIGINT` on MySQL, working
    autoincrement on SQLite. This is the standard `id` column type for
    every future table (T023+).
-   Migration `9cb30c768410_create_users_table.py` autogenerated
    correctly (unique email constraint, matching naming convention).
-   6 new tests: model create/retrieve, duplicate normalized-email
    rejection, password-hash-never-plaintext + round-trip
    verification, email normalization, and two migration-level tests
    proving the actual DDL (not just the ORM model) creates/removes
    the table with the constraint enforced.
-   Verified locally: 24 passed, 1 skipped (T012-gated), ruff/mypy
    clean.
-   No authentication service logic (login/tokens) added — that's
    T038.

Next task: T012/T013 (blocked) then T023 --- Project database (will
reuse the `BigIntegerPK` fix from T022).

### T023 --- Project database

Status: COMPLETE

Evidence:

-   `app/db/models/project.py` (`Project`/`ProjectStatus`),
    `app/db/models/collection_config.py` (`CollectionConfig`,
    immutable-per-version, `UniqueConstraint(project_id, version)`).
-   **Found and fixed a second real cross-dialect bug**: SQLite
    doesn't enforce foreign keys by default. Fixed at the engine level
    (`app/db/session.py:build_engine()`, a `PRAGMA foreign_keys=ON`
    connect-event hook) rather than per-test, so every future
    SQLite-backed test gets real FK enforcement automatically.
-   Refactored the SQLite fixture into `tests/unit/conftest.py`
    (`sqlite_engine`) rather than adding a third copy-paste.
-   Migration `88fb5b35267b_..._configs_.py` autogenerated (FKs,
    both index-strategy indexes, unique constraint).
-   7 new tests: ownership FK (+ rejection test that caught the
    SQLite FK gap), config-project linkage, immutable historical
    versions, deterministic active-version selection, clean
    empty-result handling, duplicate-version rejection. Plus a
    migration-level table-creation/removal test.
-   Verified locally: 32 passed, 1 skipped (T012-gated), ruff/mypy
    clean.

Next task: T012/T013 (blocked) then T024 --- Job database.

### T024 --- Job database

Status: COMPLETE

Evidence:

-   `app/db/models/job.py`: `Job`/`JobStatus` (canonical states from
    T000) and `JobRun`/`JobRunStatus` (one row per execution attempt).
    Counters default to 0, never NULL.
-   Two justified indexes on `jobs` (project-scoped + status-leading
    for worker polling); `job_runs(job_id, status)`.
-   Migration `89d4d3766467_...` autogenerated.
-   7 new tests: exact config-version pinning, FK rejection
    (project/config and job), safe counter defaults, full lifecycle
    timestamp progression, execution-attempt recording, and retries
    creating new job_run rows rather than mutating history. Plus a
    migration-level table test.
-   Verified locally: 40 passed, 1 skipped (T012-gated), ruff/mypy
    clean.

Next task: T012/T013 (blocked) then T025 --- Record database (likely
where real MySQL becomes necessary — dedup/canonical-key behavior).

### T025 --- Record database

Status: COMPLETE

Evidence:

-   `app/db/models/record.py`: `Record` (project-scoped unique
    `canonical_key`, per the T000 dedup-scope decision) and
    `RecordProvenance`.
-   Migration `589cf4259331_...` autogenerated.
-   6 new tests: insert, FK rejection, duplicate-canonical-key
    rejection, cross-project dedup-scope proof (same key allowed in
    two different projects), provenance linkage + FK rejection. Plus
    a migration-level table test.
-   **Found and fixed a real gap**: `tests/` had never been linted —
    17 accumulated issues fixed, and `.github/workflows/ci.yml`'s
    backend job now runs ruff over `tests/` and `workers/` too, not
    just `apps/api/`. Verified the exact CI command locally.
-   Verified locally: 47 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean for `apps/api`.

Next task: T012/T013 (blocked) then T026 --- Operations database
(exports/schedules/audit_logs).

### T026 --- Operations database

Status: COMPLETE

Evidence:

-   `app/db/models/export.py` (no `job_id` — export is its own unit of
    work), `app/db/models/schedule.py`, `app/db/models/audit_log.py`
    (`entity_id` deliberately not an FK — polymorphic).
-   Migration `bafe7b89931a_...` autogenerated.
-   6 new tests: export independence from jobs, full export lifecycle,
    schedule enable/disable, audit actor/action/entity, system-
    initiated audit entries. Plus a migration-level table test.
-   Verified locally: 53 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean for `apps/api`.
-   All tables in `docs/04_DATABASE_DESIGN.md` now exist.

Next task: T012/T013 (blocked) then T027 --- Database indexes and
constraints (needs real query plans — likely the actual hard stop).

### T027 --- Database indexes and constraints

Status: PARTIAL — genuinely blocked on T012

Evidence:

-   `database/INDEX_REVIEW.md`: complete query-to-index mapping (every
    common query pattern → the index that serves it, most already
    added incrementally in T022-T026), FK-index review (5 FK columns
    deliberately left uncovered by an explicit index — InnoDB
    auto-indexes them, adding one manually would be redundant),
    uniqueness-constraint review (3 constraints, all justified),
    non-obvious-index rationale (the two overlapping `jobs` indexes).
-   **NOT done**: step 9, "Use EXPLAIN on representative synthetic
    queries" — requires real MySQL; SQLite's query planner doesn't
    predict MySQL's index usage. Not marked complete per the task
    protocol's "must not mark complete until acceptance criteria are
    verified."

This is the real stopping point for the SQLite-substitution approach
this project has used successfully through T020-T026 (2 real bugs
found and fixed, 1 real test-coverage gap found and fixed). All 8
schema tables exist; what remains needs live MySQL.

### T030 --- Domain models

Status: COMPLETE

Evidence:

-   `app/domain/{projects,jobs,records,exports,schedules}.py`: frozen
    dataclasses + `StrEnum` status values for every entity T030 names
    (Project, CollectionConfig, Job, JobRun, Record, Export, Schedule)
    — pure Python, no SQLAlchemy, no HTTP.
-   Status enums genuinely centralized: moved out of
    `app/db/models/{project,job,export}.py` into `app/domain/`, with
    the ORM files now importing (not redefining) them — verified by
    an identity-check test (`app.db.models.JobStatus is
    app.domain.jobs.JobStatus`).
-   Validation in `__post_init__` for each entity where meaningful
    (non-empty name/canonical_key, version >= 1, non-negative
    counters, attempt >= 1). `config`/`data`/`metrics` stay opaque
    dicts — no provider-specific fields modeled in generic domain
    objects.
-   17 new tests, all pure Python — zero DB/SQLite touched, proving
    domain logic really is unit-testable without MySQL (the literal
    T030 acceptance criterion).
-   Verified locally: 69 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (31 source files).

Next: T031 --- Job state machine (also pure-Python-testable in
principle, per its own dependencies: T030, T024).

### T031 --- Job state machine

Status: COMPLETE

Evidence:

-   `app/domain/job_state_machine.py`: explicit transition table
    (single source of truth), 4 terminal states, `transition()` /
    `is_legal_transition()`, typed `InvalidJobTransition` error.
-   Retrofitted the one existing place that assigned `Job.status`
    directly (`tests/unit/test_job_models.py`, from T024) to go
    through `transition()` — satisfies "database/service code uses
    this state machine rather than arbitrary status assignment" given
    no repository/service layer exists yet to refactor.
-   20 new tests: full legal-transition matrix, representative illegal
    transitions, the two acceptance criteria verbatim
    (completed→running, failed→completed), pause/resume symmetry,
    terminal-status exhaustiveness, full 8×8 completeness sweep,
    no-self-transition.
-   Verified locally: 100 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (32 source files).

Next: T032 --- Repository layer (likely wants real MySQL for proper
integration tests, not just the SQLite-substitution unit tests used
so far).

### T032 --- Repository layer

Status: COMPLETE

Evidence:

-   `app/repositories/base.py` (shared `SqlAlchemyRepository`/`Page`),
    plus exactly 7 concrete repositories (project, config, job,
    record, export, schedule, audit) each with a `Protocol` +
    SQLAlchemy implementation — matching T032's literal entity list
    (`JobRun`/`RecordProvenance` folded into `Job`/`Record` repos).
-   `JobRepository.update_status()` goes through
    `app.domain.job_state_machine.transition()`, not a direct
    assignment — verified by a test that a jump to an illegal target
    raises `InvalidJobTransition`.
-   Added `app/domain/audit.py` (`AuditLogEntry`) — a small, justified
    addition since T032 needs a domain type for audit entries that
    T030 didn't create.
-   **Found and fixed a real domain/schema mismatch**: `Record.
    collected_at`, `RecordProvenance.collected_at`, `Schedule.
    next_run_at` had misleading optional defaults despite being
    NOT NULL columns the repositories forward as-is — fixed by making
    them required, which now fails fast with a clear `TypeError`
    instead of a confusing SQL error.
-   Refactored shared test setup into `tests/unit/conftest.py`
    (`session_factory` fixture) and `tests/unit/factories.py`.
-   16 new tests, all working through domain objects only (no
    SQLAlchemy row type in any assertion) — satisfies the literal
    acceptance criterion.
-   Verified locally: 114 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (42 source files).

Next: T033 --- Project service (business rules + authorization
boundaries — likely the point where real MySQL integration testing
starts mattering more than the SQLite-substitution approach).

### T033 --- Project service

Status: COMPLETE

Evidence:

-   `app/services/errors.py` (`NotFoundError`/`PermissionDeniedError`/
    `InvalidStateError`, shared across future services) and
    `app/services/projects.py` (`ProjectService`).
-   Added `ProjectRepository.update_fields()`/`.set_status()` (T032
    didn't include these; T033 needed them).
-   `ensure_can_start_job()` guard method satisfies "archived project
    cannot start new jobs" — will be called by T035's job service.
-   Every mutation records an audit event via `AuditLogRepository`,
    verified directly (not just "didn't crash").
-   13 new tests: audit events, validation, cross-user access denial,
    not-found, both `ensure_can_start_job` outcomes, list-scoping.
-   Verified locally: 125 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (45 source files).

Next: T034 --- Configuration service (versioned provider config +
validation workflow).

### T034 --- Configuration service

Status: COMPLETE

Evidence:

-   `app/domain/provider_validation.py` (`ConfigValidationResult`,
    `ProviderConfigValidator` Protocol) resolves T034's circular
    dependency on T040.
-   `app/services/configs.py` (`ConfigurationService`): deterministic
    version numbering, validation strictly before any row is created,
    new `CollectionConfigRepository.set_active_version()` as the only
    post-creation mutation (`is_active` pointer only).
-   Test-only fakes in `tests/unit/fakes.py`.
-   11 new tests: versioning, single-active-version invariant,
    unmutated historical content, invalid-config rejection (generic +
    delegated), `activate_version`, cross-user denial.
-   Verified locally: 134 passed, 1 skipped (T012-gated), ruff clean,
    mypy clean (47 source files).

Next: T035 --- Job service (job creation/lifecycle commands, will use
`ProjectService.ensure_can_start_job`).

### T035 --- Job service

Status: COMPLETE

Evidence:

-   `app/services/jobs.py` (`JobService`): transactional `create_job()`
    (idempotency check, authorization, active-config lookup, insert,
    QUEUED transition all in one session), `cancel_job`/`pause_job`/
    `resume_job` (state-machine-enforced via `update_status`),
    `retry_job` (creates a new job, original `FAILED` job untouched,
    gated by `app.domain.job_errors.is_retryable`).
-   Added `jobs.idempotency_key` (nullable, UNIQUE) via a real schema
    migration. **This ALTER-TABLE migration initially failed on
    SQLite** (constraint changes need Alembic batch mode) — fixed with
    `batch_alter_table`, verified with a full upgrade/downgrade/
    upgrade/downgrade round-trip test. First real "ALTER an existing
    table" migration in the project; all prior ones were CREATE TABLE.
-   14 new tests: creation + audit, no-active-config/archived-project
    rejection, idempotency dedup, cancel/pause/resume, retry (all 3
    outcomes), not-found, cross-user denial.
-   Verified locally: 148 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (49 source files).

Next: T036 --- Record service (server-side search/filtering/detail
retrieval).

### T036 --- Record service

Status: COMPLETE

Evidence:

-   `app/domain/record_search.py` (`RecordSearchFilters`, `RecordSort`)
    and `app/services/records.py` (`RecordService`).
-   `RecordRepository.search()` translates provider/date/quality
    filters and sort into a real server-side query.
    `MAX_RECORD_PAGE_LIMIT = 200` enforced in the repository itself.
-   "Quality filtering" implemented as `has_provider_id` (generic,
    no dedicated schema field exists yet — T051 should extend/replace).
-   11 new tests including a synthetic 250-record dataset proving
    3-page pagination is disjoint, and a 100,000-row request clamped
    to 200. Plus scoping, filters, sort, detail, not-found, cross-user
    denial.
-   Verified locally: 158 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (51 source files).

Next: T037 --- Audit service (structured audit events — likely
substantially already covered by `AuditLogRepository`/the pattern
established across T033-T036; check what's actually left to add).

### T037 --- Audit service

Status: COMPLETE

Evidence:

-   `app/domain/audit_actions.py` (`AuditAction` StrEnum, single
    source of truth for action names) and
    `app/domain/audit_redaction.py` (`redact_details()`, recursive).
-   `app/services/audit.py` (`AuditService`): `record_event()` always
    redacts before persisting; new `list_for_entity()` (+ repository
    method) for full per-entity history, not just per-actor.
-   Refactored `ProjectService`/`JobService` to depend on
    `AuditService` instead of `AuditLogRepository` directly (removed
    duplicated private helpers); **added audit calls to
    `ConfigurationService`**, which had none before T037.
-   Updated all dependent test files' service constructors.
-   12 new tests: redaction (direct + through a real `record_event()`
    call proving a password never reaches persisted `details`),
    entity-scoped history, actor/entity identification.
-   Verified locally: 164 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (54 source files).

Next: T038 --- Authentication (secure V1 auth — likely the actual next
hard stop for the SQLite-substitution approach; session/token handling
benefits strongly from real integration tests).

### T038 --- Authentication

Status: COMPLETE

Evidence:

-   `app/domain/users.py` (`UserStatus`, `User`), `app/domain/auth.py`
    (`AuthSession`, `IssuedSession`, `as_naive_utc`),
    `app/db/models/session.py` (`Session` table), migration
    `9e753afdce70_...` (sessions table + `users.failed_login_attempts`/
    `locked_until`, with `server_default='0'` added by hand after
    autogenerate omitted it).
-   `app/repositories/{users,sessions}.py`, `app/services/auth.py`
    (`AuthService`: password login via bcrypt (T022), opaque
    `secrets.token_urlsafe(32)` session tokens stored SHA-256-hashed,
    12-hour session lifetime, lockout after 5 failed attempts for 15
    minutes, same error message for wrong-password/unknown-email — no
    enumeration, no self-registration in V1).
-   `app/api/envelope.py`, `app/api/dependencies.py`,
    `app/api/v1/auth.py` — first real `/api/v1` business routes
    (`POST /auth/login`, `POST /auth/logout`, `GET /auth/me`),
    establishing the `{"data": ..., "request_id": ...}` envelope every
    future route should reuse.
-   **Found and fixed a real cross-dialect bug** (MySQL too, not just
    SQLite): `DATETIME` columns drop timezone-awareness on read-back,
    but a freshly-created ORM object may still hold Python's original
    aware `datetime`, causing an intermittent
    `TypeError: can't compare offset-naive and offset-aware datetimes`.
    Fixed with `as_naive_utc()`, applied to both sides of every
    comparison. See `docs/16_MEMORY.md` for full detail.
-   **Found and fixed a real, pre-existing test bug** while running the
    full suite for the first time since T035: the migration round-trip
    test used a relative `downgrade(config, "-1")`, which implicitly
    assumed the idempotency-key migration was still `head` — T038's
    new migration broke that assumption. Fixed by targeting the exact
    parent revision by name instead.
-   15 new tests: login success/failure/lockout/counter-reset, expired
    session (via a forged, hashed, DB-persisted token — proves the
    real lookup path, not just the dataclass property), logout
    revocation + idempotency, disabled account, unknown/garbage token,
    plus full HTTP-layer coverage of all 3 routes.
-   Verified locally: 179 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (63 source files).

Next: T039 --- Authorization (project-level access, resource
isolation — depends on T038/T033/T035/T036, all already complete).

### T039 --- Authorization

Status: COMPLETE

Evidence:

-   Full review in `database/AUTHORIZATION_REVIEW.md` (same convention
    as T027's `database/INDEX_REVIEW.md`). Verified the ownership
    policy (a resource is authorized via its parent project's
    `user_id`, checked once in `ProjectService._require_owner` and
    reused everywhere via `ProjectService.get_project`/
    `ensure_can_start_job`) was already correctly enforced by every
    service that exists (`ProjectService`, `ConfigurationService`,
    `JobService`, `RecordService` — all built at T033-T036) — no
    service code needed to change.
-   **Closed a real gap**: no route ever mapped
    `PermissionDeniedError`/`NotFoundError`/`InvalidStateError` to an
    HTTP status except T038's `auth.py`, done by hand for one case.
    Added `app/api/service_errors.py`
    (`register_service_error_handlers`): 403/404/409 respectively,
    registered in `app/main.py`. Without this, every T070+
    project-scoped route would have needed to catch these individually
    or leak them as 500s.
-   **Closed a real coverage gap**: added 6 previously-missing negative
    (cross-user) tests for methods that already enforced ownership
    correctly but had no regression test proving it —
    `ProjectService.archive_project`, `ConfigurationService.
    activate_version`/`list_versions`, `JobService.pause_job`/
    `resume_job`/`retry_job`, and `JobService.create_job` (the literal
    T039 acceptance criterion: a stranger supplying someone else's
    `project_id`).
-   **Documented, not built speculatively**: `ExportService`/
    `ScheduleService` don't exist yet (only domain/repository layers)
    — authorization enforcement for them is now a recorded, binding
    obligation on T080/T083 rather than invented ahead of those
    services' real method signatures. No project-scoped HTTP endpoint
    exists yet either (only T038's auth router) — recorded as a
    transitive obligation on every T070+ route, pre-verified via
    `tests/integration/test_service_error_handlers.py`.
-   9 new tests total (6 negative-access + 3 for the new error
    handlers). Verified locally: 185 passed, 1 skipped (T012-gated),
    ruff clean across all three Python trees, mypy clean (66 source
    files).

Next: T040 --- Provider interface (generic `ProviderAdapter` contract —
resolves the interim `ProviderConfigValidator` Protocol T034 created
explicitly to be reconciled here).

### T040 --- Provider interface

Status: COMPLETE

Evidence:

-   `app/domain/provider_contracts.py`: `UsageEstimate` (rejects
    negative unit counts), `RawProviderItem` (PEP 695 type alias),
    `NormalizedItem` (field names match `Record.provider_record_id`/
    `Record.data` for a direct pipeline mapping later),
    `ProviderErrorCategory` (StrEnum, the exact 7 categories from
    `docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md`), `ProviderError`,
    `ProviderHealth`.
-   `app/providers/base.py` (new package): `ProviderAdapter`
    (`@runtime_checkable` Protocol) —
    `validate_config`/`estimate`/`collect`/`normalize`/
    `classify_error`/`health_check`, matching the T000-resolved method
    naming exactly. `collect()` returns a lazy `Iterator`, not a
    buffered list. No SDK import, no HTTP client, no browser-automation
    reference anywhere in the module (T040's explicit DO NOT list).
-   Reused `ConfigValidationResult`/`ProviderConfigValidator` from
    T034's `app.domain.provider_validation` rather than duplicating —
    exactly what that file's own docstring asked T040 to do.
-   `FakeProviderAdapter` added to `tests/unit/fakes.py` (already
    anticipated there since T034): deterministic, configurable raw
    items, no I/O.
-   **Documented rather than built speculatively**: docs/07's future
    `ProviderRegistry` (dispatching multiple adapters by name) isn't
    listed in any current task, so it wasn't built here — flagged in
    `ProviderAdapter`'s docstring instead. The overlap between
    `ProviderErrorCategory` (T040) and `app.domain.job_errors.
    RETRYABLE_ERROR_CLASSES` (T035's interim retry set) is explicitly
    left for T044 ("Provider error mapping") to reconcile, not
    resolved here — no dependency on T035/T044 exists at T040.
-   12 new tests (`tests/unit/test_provider_interface.py`): protocol
    satisfaction via `isinstance`, validation (valid/invalid),
    `UsageEstimate` behavior (+ its own negative-value rejection),
    `collect()` proven to be a real lazy iterator yielding every raw
    item, `normalize()`'s exact field mapping, both `classify_error`
    branches, `health_check()`, and a full
    validate→estimate→collect→normalize lifecycle test.
-   Verified locally: 197 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (67 source files).

Next: T041 --- Google configuration (validate Google-specific config
before execution — needs current, accurate Google Maps Platform
API/product documentation verified via web search, not assumed from
training knowledge).

### T041 --- Google configuration

Status: COMPLETE

Evidence:

-   `app/providers/google_maps/config.py`: `GoogleMapsConfigValidator`
    — the first real (non-fake) `ProviderConfigValidator` implementation
    plugged into T034's `ConfigurationService` (every prior use was a
    `tests/unit/fakes.py` fake). No network call, no SDK.
-   **Resolved a design decision no doc pinned down**: selected
    operation is Places API (New) — Text Search, chosen because
    docs/07's conceptual example config matches that operation's shape
    exactly (not the legacy Places API, deprecated; not Nearby Search,
    which filters by type rather than free text).
-   **Field names and limits verified against Google's live public
    documentation, fetched on 2026-08-20** (not recalled from training
    data, which predates "today" and would risk being stale):
    `pageSize`/`maxResultCount` 1-20 per page with a 60-result cap
    across all pages, `locationBias` radius 0.0-50,000.0 meters,
    required `X-Goog-FieldMask`, and the field→SKU-tier mapping behind
    `ALLOWED_FIELDS`. Documented as needing reverification against the
    live docs before production release (T041's own instruction).
-   Validates: server-side credential presence (`api_key`, never read
    from the request body itself), query non-empty, location lat/lng
    ranges, radius requires location + stays within Google's cap,
    fields required + each one a known field name, max_results within
    Google's real cap, price_levels excludes `PRICE_LEVEL_FREE`
    (request-invalid per Google), rank_preference enum.
-   **Caught a real inconsistency in the docs pack itself**: docs/07's
    own conceptual example config uses `max_results: 100`, 40 over
    Google's real 60-result cap — a dedicated test proves the validator
    rejects exactly that value with an actionable error naming the
    real limit.
-   19 new tests, including one wiring `GoogleMapsConfigValidator` into
    a real `ConfigurationService` (not a fake) to prove an invalid
    config never becomes an active, persisted version — T041's literal
    acceptance criterion.
-   Verified locally: 216 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (69 source files).

Next: T042 --- Google client (the real HTTP client boundary — request
construction/response parsing/pagination/retries against mocked
responses, no live credentials in the automated suite).

### T042 --- Google client

Status: COMPLETE

Evidence:

-   `app/providers/google_maps/client.py`: `GoogleMapsClient` — the
    real HTTP boundary against `POST
    https://places.googleapis.com/v1/places:searchText` (httpx,
    promoted from a dev-only to a real `[project.dependencies]` entry
    in `apps/api/pyproject.toml`). `GoogleMapsApiError` — the one
    structured exception type this client ever raises, for T044 to
    classify later.
-   Server-side credential loading: `api_key: str` required at
    construction, never read from a request body. Request timeout
    configurable. Retries only network-transport failures and HTTP 5xx
    (genuine infra hiccups) — **4xx responses (auth/invalid-request/
    quota/rate) are never retried inside this client**, a deliberate
    decision matching docs/07's "never bypass a policy/quota/rate
    denial" rule; those propagate for the job-level retry path
    (`JobService.retry_job`, T035) to decide about later, with real
    elapsed time between attempts.
-   Request construction translates T041's snake_case app config into
    Google's real camelCase body + `X-Goog-FieldMask` header (field
    names prefixed with `places.`, plus `places.id` and
    `nextPageToken` always included). Response parsing + pagination
    (`pageToken`/`nextPageToken`) up to the `max_results` cap T041
    already validates against (`MAX_RESULT_COUNT`, reused not
    re-declared). Lazy generator — a caller consuming only the first
    few items never triggers a later page.
-   Usage/quota metadata: verified against Google's live docs (same
    fetch as T041, 2026-08-20) that Text Search (New) responses carry
    no documented per-call quota field/header — recorded as an honest
    "not available"; quota exhaustion surfaces via the structured-error
    path instead.
-   Credential redaction: the API key is a request header, never
    logged, never echoed into an error message — verified directly by
    a dedicated test.
-   Dependency injection: `http_client: httpx.Client | None` — every
    one of the 17 new tests uses `httpx.MockTransport`, no real network
    call, no real credentials anywhere in the suite (T042's literal
    acceptance criterion).
-   Verified locally: 233 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (70 source files).

Next: T043 --- Google response mapper (convert raw Google Text Search
items into the platform's normalized internal record representation —
fixture-based, deterministic).

### T043 --- Google response mapper

Status: COMPLETE

Evidence:

-   `app/providers/google_maps/mapper.py`: `normalize_place()` — the
    real Google implementation of `ProviderAdapter.normalize()`
    (T040's Protocol), exhaustive over T041's `ALLOWED_FIELDS`.
    `map_place_to_record_draft()` — combines it with job/project
    context and a collection timestamp (T043 items 7/8), for the
    worker (T060+) to call.
-   New `app.domain.records.RecordDraft`: a `Record` minus
    `id`/`canonical_key`/`created_at`/`updated_at` — canonical-key
    computation is Stage 5 of `docs/08_DATA_PIPELINE_DEEP.md` (T052),
    explicitly not this task's job.
-   Field mapping: `displayName.text`→`name`,
    `formattedAddress`→`formatted_address`, `location`→
    `latitude`/`longitude` (both required together),
    `businessStatus`/`priceLevel`→lowercased, `primaryType`,
    `types`(filtered to strings), `rating`→float,
    `userRatingCount`→int, `internationalPhoneNumber`→`phone_number`,
    `websiteUri`→`website`, `currentOpeningHours`→
    `open_now`/`weekday_descriptions` (flattened). `id`→
    `provider_record_id`.
-   **Malformed-input handling, the key design decision**: a field
    present but wrong-typed is treated exactly like a missing field —
    silently omitted, never coerced, never raises. Verified directly
    with a fixture where every field is wrong-typed, asserting the
    result is empty (`data={}`) with no exception.
-   Provider/source reference: `GOOGLE_MAPS_TEXT_SEARCH_OPERATION`
    constant documents what T054 should use as
    `RecordProvenance.provider_operation`; `source_reference` is
    documented as deliberately `None` (Places API (New) has no
    separate reference field beyond `id`).
-   First fixture-based test directory in the project
    (`tests/fixtures/google_maps/`): `full_place.json` (every field
    populated), `minimal_place.json` (only id/name),
    `malformed_place.json` (every field wrong-typed). 10 new tests,
    including the literal acceptance criterion (same fixture always
    produces the same result).
-   Verified locally: 243 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (71 source files).

Next: T044 --- Provider error mapping (classify `GoogleMapsApiError`
into T040's `ProviderErrorCategory` taxonomy, reconcile with T035's
interim job-failure retry set, mark retryability explicitly).

### T044 --- Provider error mapping

Status: COMPLETE

Evidence:

-   `app/providers/google_maps/errors.py`: `classify_google_maps_
    error()` — the real Google implementation of `ProviderAdapter.
    classify_error()` (T040's Protocol). Maps Google's `error.status`
    string (`UNAUTHENTICATED`, `INVALID_ARGUMENT`, `RESOURCE_EXHAUSTED`,
    `UNAVAILABLE`, etc.) into `ProviderErrorCategory`, with an
    HTTP-status-code fallback when that string is missing.
-   Extended `ProviderError` (T040's shape) with a mandatory
    `retryable: bool` (no default — can never be silently omitted) and
    diagnostic `http_status_code`/`provider_status` fields. New
    `default_retryable_for_category()` — the taxonomy-level retry
    default (`RATE`/`TEMPORARY` retryable, everything else not),
    derived from `docs/09_JOB_QUEUE_WORKER_DEEP.md`'s "do not retry
    ... provider policy rejection" instruction (quota exhaustion is a
    policy rejection, not retryable, despite being grouped with rate
    in docs/07's prose).
-   **Documented a genuine upstream limitation rather than inventing
    false precision**: Google's Places API (New) exposes no status
    distinct from `RESOURCE_EXHAUSTED` for rate-limiting vs. quota
    exhaustion — this adapter maps that status to `QUOTA` only;
    `ProviderErrorCategory.RATE` exists for providers that do
    distinguish the two and is simply never produced here.
-   **Reconciled `app.domain.job_errors` with the real taxonomy** —
    `Job.error_code` now holds a `ProviderErrorCategory` value or the
    separate, always-retryable `"persistence"` code (transient
    database failures, which the provider taxonomy was never meant to
    cover). Replaces T035's provisional
    `"transient_network"`/`"rate_limit"` codes; updated the one
    existing test that asserted on the old value.
-   22 new tests (`tests/unit/test_google_maps_errors.py`): every
    documented Google status → category mapping, the HTTP-fallback
    path, unrecognized-status handling, retryability per category,
    diagnostic-context preservation, and the literal acceptance
    criterion (two identical classified errors yield the same retry
    decision).
-   Verified locally: 265 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (72 source files).

Next: T045 --- Provider contract tests (assemble the complete
fake-provider contract suite proving the whole Google adapter is
testable without live credentials).

### T045 --- Provider contract tests

Status: COMPLETE

Evidence:

-   `app/providers/google_maps/provider.py`: `GoogleMapsProvider` — the
    first concrete `ProviderAdapter` (T040's Protocol) in the
    codebase, assembled purely by composition from T041
    (`GoogleMapsConfigValidator`), T042 (`GoogleMapsClient`), T043
    (`normalize_place`), and T044 (`classify_google_maps_error`).
    `isinstance(provider, ProviderAdapter)` passes.
-   `estimate()`/`health_check()` — no prior implementation existed
    anywhere for either. Written honestly scoped: `estimate()` reports
    the config's own bounded `max_results` (Google has no pre-call
    usage-estimate endpoint); `health_check()` only confirms the
    adapter was constructed with a credential, deliberately not
    spending real API quota on a live probe.
-   **Found and fixed a real robustness gap** in T042's
    `GoogleMapsClient.search_text()` while writing the malformed-
    response test: a top-level malformed response (`places` not a
    list) would have iterated a string's characters instead of failing
    gracefully. Fixed with type checks on both `places` and each
    individual `place` entry, and tightened `nextPageToken` handling
    the same way.
-   New fixtures (`tests/fixtures/google_maps/`): full search-response
    shapes (valid/empty/malformed/paginated) and realistic Google
    error bodies (quota/authentication/transient).
-   15 new tests, one per T045 IMPLEMENT item, plus Protocol-
    satisfaction proof and coverage for the two methods this task
    introduced.
-   Verified locally: 280 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (73 source files).

**Phase 4 (Provider) is now fully complete**: T040 (interface) → T041
(Google config validation) → T042 (Google HTTP client) → T043 (Google
response mapping) → T044 (Google error classification) → T045
(assembled + contract-tested). Every `ProviderAdapter` method has a
real, tested Google implementation — no live network call made against
Google anywhere in this codebase yet, which is correct: nothing in the
task list asks for that before the worker (T060+) actually needs it.

Next: T050 --- Normalization pipeline (Stage 3 of the data pipeline —
provider-agnostic, deterministic value transformations on top of
T043's already-mapped output).

### T050 --- Normalization pipeline

Status: COMPLETE

Evidence:

-   `app/pipeline/normalize.py` (new package): `FieldKind` (StrEnum:
    TEXT/URL/NUMBER/TIMESTAMP/CATEGORY) + `normalize_record_data()` —
    pure, total, provider-agnostic Stage 3 transformations, applied
    after (and separate from) a provider's own field mapping (T043).
-   Field kinds are declared by the caller, never guessed from a
    value's shape — the only way to keep "never invent a default"
    honest at the kind-detection level, not just the value level.
    Undeclared keys default to `FieldKind.TEXT` (universally safe:
    trim + NFC).
-   Unicode: NFC only, never NFKC — NFC is lossless/canonical, NFKC
    changes actual content (™→TM, fullwidth→ASCII digits). Every
    per-kind transform falls back to text-only cleanup when a value
    doesn't match its declared kind (non-numeric string under NUMBER,
    unparseable/no-explicit-timezone TIMESTAMP, malformed URL) —
    never coerced, never guessed.
-   Wired into `app/providers/google_maps/mapper.py`'s
    `map_place_to_record_draft()` immediately via a new `FIELD_KINDS`
    constant, not left an orphaned, unused module. Existing T043
    tests re-verified to still pass unchanged.
-   **Found and worked around a real tool-level limitation** while
    writing the Unicode NFC/NFKC test: two visually-identical accented
    characters (one NFC, one NFD) typed as literal source text could
    not be reliably distinguished/matched by the file-editing tooling.
    Fixed by building both forms explicitly via `chr()` code points
    instead of literal characters — worth remembering for any future
    test needing an exact non-ASCII byte sequence.
-   25 new tests, one section per T050 IMPLEMENT item, plus a
    dedicated regression fixture
    (`tests/fixtures/pipeline/normalize_regression.json`) covering
    every kind in one realistic mixed record.
-   Verified locally: 305 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (75 source files).

**Phase 5 (Data pipeline) is now started.**

Next: T051 --- Validation pipeline (field-level data quality system —
valid/warning/rejected states, type/range/required-field/coordinate/
URL validation, deterministic, no network calls).

### T051 --- Validation pipeline

Status: COMPLETE

Evidence:

-   `app/pipeline/validate.py`: `RecordQuality` (VALID/WARNING/
    REJECTED), `FieldRule`, `FieldValidationError`, `ValidationResult`,
    `validate_record_draft()` — Stage 2 ("Schema validation") + Stage
    4 ("Quality") combined into one pass, since a field either passes
    or fails with a severity and the record's overall verdict is just
    the worst severity among its fields.
-   **Key decision**: "missing" and "present but invalid" are separate
    knobs (`missing_severity` vs. `severity`) — directly matching
    docs/08's two worked examples ("missing website → warning",
    "invalid coordinate → rejected"), which a single `required: bool`
    flag could not express together.
-   Coordinate range validation needed no dedicated mechanism (just
    `min_value`/`max_value` on a coordinate field); URL syntax
    validation is syntax-only (`urllib.parse.urlsplit`), never a real
    request — what makes "no network calls" trivially true.
    `bool` is explicitly guarded against silently passing a numeric
    type check.
-   Wired into `app/providers/google_maps/mapper.py` via
    `GOOGLE_FIELD_RULES` + `validate_google_place_record()`, an
    explicit separate step from `map_place_to_record_draft()`, not
    silently chained into it.
-   28 new tests across `tests/unit/test_pipeline_validate.py` (one
    section per IMPLEMENT item) and `tests/unit/test_google_maps_
    mapper.py` (3 tests proving the real Google field rules produce
    the right verdict, not just the generic module in isolation).
-   Verified locally: 333 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (76 source files).

Next: T052 --- Canonical identity (deterministic record identity
strategy — prefer the stable provider identifier, fallback
canonicalization only where needed, project+provider scope, documented
collision limitations).

### T052 --- Canonical identity

Status: COMPLETE

Evidence:

-   `app/pipeline/canonical_identity.py`: `compute_canonical_key()` —
    fully generic, no Google-specific wiring needed anywhere.
-   Resolved a real ambiguity between T000's conceptual decision
    ("project_scope + provider + provider_id") and the actual schema:
    `records`'s composite `UniqueConstraint(project_id, canonical_key)`
    (T025) already scopes uniqueness per-project, so `project_id`
    isn't embedded in the string; `provider` is embedded, since the DB
    constraint has no separate `provider` dimension.
-   Preference order: `provider_record_id` always wins when present;
    fallback (SHA-256 hash of normalized `name`+`formatted_address`
    together, never name alone — T052's explicit DO NOT rule) only
    when no provider identifier exists. Hashed, not embedded verbatim,
    to stay safely within `canonical_key`'s `String(512)` bound
    regardless of input length.
-   Known collision limitations (false merge / false split) documented
    directly in the module docstring, not glossed over.
-   15 new tests: provider-id preference, provider-embedding (no
    cross-provider collision), fallback triggers/raises correctly,
    the DO NOT rule, repeated-identical-input determinism, minor-
    formatting-difference insensitivity, different-businesses
    non-collision.
-   Verified locally: 348 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (77 source files).

Next: T053 --- Deduplication (batch + database dedup using canonical
identity, update-vs-skip policy, false-merge/duplicate-batch/
DB-constraint tests).

### T053 --- Deduplication

Status: COMPLETE

Evidence:

-   `app/pipeline/deduplicate.py`: `deduplicate_within_batch()` (pure,
    streaming, within+across pages) + `resolve_against_existing()`
    (DB-touching, uses T032's `get_by_canonical_key`) +
    `deduplicate_batch()` (composes both, tracks `DedupSummary`).
-   New `RecordRepository.update_collected_data()` — T032 never
    included an update path; added now since T053 genuinely needs one.
-   Update-vs-skip policy: `update_existing=True` by default (repeat
    collections refresh stale data — ratings/hours/status genuinely
    change), `update_existing=False` fully supported as a real,
    equally-exercised alternative, not a hardcoded assumption.
-   `deduplicate_within_batch()` yields every draft with an
    `is_duplicate` flag (not just first occurrences), so duplicate
    counts can be tallied in one pass.
-   Database-constraint test proves the T025 `UniqueConstraint` is the
    final safety net independent of this module's own correctness —
    two direct `RecordRow` inserts with the same
    `(project_id, canonical_key)`, bypassing `deduplicate_batch()`
    entirely, and the second flush raises `IntegrityError`.
-   11 new tests: within/across-page dedup, create/update/skip against
    a real repository, summary counting every outcome kind,
    false-merge (two different businesses both kept), duplicate-batch
    (5 repeats → 1 row + 4 counted duplicates), the database-constraint
    test above.
-   Verified locally: 359 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (78 source files).

Next: T054 --- Transactional persistence (atomic batch writes,
provenance storage, rollback-safe, counters incremented only after
success).

### T054 --- Transactional persistence

Status: COMPLETE

Evidence:

-   `app/pipeline/persist.py`: `persist_batch()`/`_persist_one()` —
    wraps each T053 dedup decision in its own SAVEPOINT
    (`session.begin_nested()`), so one record's failure rolls back
    only that record, never siblings already written earlier in the
    same outer transaction — the literal reading of "a failed
    transaction does not leave partial inconsistent state" at record
    granularity, matching docs/08's "never hide failures"/
    `partially_completed` philosophy rather than batch-wide
    all-or-nothing.
-   **Found and fixed a real correctness gap in T053**: its
    `DedupSummary` counters incremented right after a repository
    `flush()`, not a `commit()` — if a later record in the same outer
    transaction failed with no per-record isolation, those counters
    would have claimed successes a subsequent rollback then silently
    undid. T054's SAVEPOINT is what makes each record's own success
    durable within the still-open outer transaction.
-   Provenance stored only for actual writes (CREATED/UPDATED);
    `provider_operation` is caller-supplied, zero Google-specific
    imports in this module.
-   Constraint-conflict tests use a `_StaleCheckRepository` wrapper
    whose `get_by_canonical_key` always returns `None` (simulating a
    concurrent insert) around the REAL repository, so the actual T025
    `UniqueConstraint` raises the `IntegrityError`, not a mock.
-   Tests placed in `tests/integration/` (item 7's explicit ask) —
    exercise a full commit-at-the-end lifecycle, re-opening a fresh
    session after commit to prove durability.
-   8 new tests: create, update-vs-skip, provenance-for-writes-only,
    constraint-conflict-marked-FAILED-not-raised, the core "failed
    record doesn't roll back earlier successes" proof, and
    summary-matches-committed-row-count.
-   Verified locally: 367 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (79 source files).

Next: T055 --- Pipeline metrics (accurate job/pipeline counters —
work units, records created/updated/rejected, retries — atomic with
the records they describe).

### T055 --- Pipeline metrics

Status: COMPLETE

Evidence:

-   `app/pipeline/metrics.py`: `compute_job_counters()` aggregates
    T051's `ValidationResult`s and T054's `PersistOutcome`s into
    `JobCounters` (T024's existing shape). `count_job_run_attempts()`
    surfaces "retries" from the already-existing `JobRun.attempt`
    field rather than inventing a new concept or schema change. New
    `JobRepository.update_counters()`.
-   Documented bucket-mapping decision: a DB-conflict `FAILED` outcome
    counts toward `failed_units` but deliberately NOT
    `records_rejected` (reserved for Stage-4 quality rejections) —
    conflating the two would make `records_rejected` an inaccurate
    quality signal. `total_units == successful_units + failed_units +
    skipped_units` always holds by construction, verified directly.
-   Atomicity (the literal acceptance criterion — "counters never
    claim success for uncommitted records") proven by an integration
    test committing counters and records together, then re-reading
    from a fresh post-commit session.
-   **Found and fixed a real pytest collision** while adding the
    integration test: `tests/unit/test_pipeline_metrics.py` and a
    same-named `tests/integration/` file collided at collection
    (no `__init__.py` in either directory) — renamed the integration
    file to `test_pipeline_metrics_transaction.py`.
-   15 new tests (10 pure aggregation + 1 transactional-atomicity
    integration test), one per T055 test scenario (all-success,
    partial-failure, retry, duplicate, rejected-record) plus the
    `total_units` invariant.
-   Verified locally: 378 passed, 1 skipped (T012-gated), ruff clean
    across all three Python trees, mypy clean (80 source files).

**Phase 5 (Data pipeline) is now fully complete**: T050 (normalize) →
T051 (validate) → T052 (canonical identity) → T053 (deduplicate) →
T054 (persist) → T055 (metrics) — every stage of
`docs/08_DATA_PIPELINE_DEEP.md` implemented, tested, provider-agnostic.

Next: T060 --- Redis queue (first task of Phase 6, Worker — queue
interface, Redis implementation, minimal job-ID-only payload, MySQL
remains the system of record).
