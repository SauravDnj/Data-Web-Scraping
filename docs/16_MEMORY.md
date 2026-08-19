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

T062 --- next up. (T000-T002, T010, T011, T014, T015, T020-T026 fully
complete, T027 PARTIAL (see database/INDEX_REVIEW.md), T030-T045,
T050-T055, and T060-T061 complete — Phase 4 Provider and Phase 5 Data
pipeline both fully done, Phase 6 Worker's first vertical slice
(T061) working end-to-end. T012/T013 prepared but NOT verified — see
below. See the dated sections further down for detail; this header is
not updated inline each time, check docs/17_CURRENT_WORK.md for the
authoritative up-to-the-minute status.)

## T027 — the real hard stop

Steps 1-8 and 10 of T027 done without MySQL: query-to-index mapping,
FK-index review, uniqueness-constraint review, and rationale
documentation — all in `database/INDEX_REVIEW.md`. Step 9 ("Use
EXPLAIN on representative synthetic queries") genuinely requires real
MySQL — SQLite's query planner doesn't predict MySQL's index usage.
**Do not mark T027 complete until that step is done for real.**

This closes out the run of tasks that could proceed without live
infra. Everything from here (T030 domain models is fine, but T031 job
state machine / T032 repository layer / T033+ will increasingly want
real integration testing) benefits from T012 being resolved. Check
back with the user before continuing further into T030+.

## Domain models (T030) — current task now T031

`app/domain/{projects,jobs,records,exports,schedules}.py`: frozen
dataclasses (`Project`, `CollectionConfig`, `Job`, `JobCounters`,
`JobRun`, `Record`, `RecordProvenance`, `Export`, `Schedule`) plus
`StrEnum`-based status enums (`ProjectStatus`, `JobStatus`,
`JobRunStatus`, `ExportStatus`). No SQLAlchemy, no HTTP — pure Python,
importable and testable without any DB.

**Centralized status values for real, not just re-implemented in a
new location**: moved `ProjectStatus`/`JobStatus`/`JobRunStatus`/
`ExportStatus` OUT of `app/db/models/{project,job,export}.py` (where
T022-T026 originally defined them) and INTO `app/domain/`; the
SQLAlchemy model files now `from app.domain.X import YStatus` and
re-export via `__all__` rather than redefining — `app.db.models.
JobStatus is app.domain.jobs.JobStatus` (same object), verified by an
identity-check test. This fixes the dependency direction retroactively
to match `docs/02_SYSTEM_ARCHITECTURE_DEEP.md` (domain is the inner
layer; persistence depends on it, not the reverse). `UserStatus` and
`AuditLog` were deliberately left alone — out of T030's literal scope
(no "Define User" in the prompt).

Validation lives in `__post_init__` (project name non-empty, config
version >= 1, job counters non-negative, job_run attempt >= 1, record
canonical_key non-empty) — this is where "value objects... where
useful" landed. `CollectionConfig.config` / `Record.data` /
`JobRun.metrics` stay opaque `dict[str, Any]` — no provider-specific
fields modeled here, per T030's explicit instruction.

17 new tests, all pure Python (no `sqlite_engine` fixture, no DB
touched at all) — validation rejection cases, sensible defaults,
immutability (`frozen=True` → `AttributeError` on mutation), and the
status-enum-identity proof.

Verified locally: 69 passed, 1 skipped (T012-gated), ruff clean across
all three Python trees, mypy clean (31 source files now, up from 25).

## Job state machine (T031)

`app/domain/job_state_machine.py`: `_ALLOWED_TRANSITIONS` dict is the
single source of truth. Terminal states (no legal outgoing
transition): `COMPLETED`, `PARTIALLY_COMPLETED`, `FAILED`,
`CANCELLED` — a job that needs to run again is a NEW `Job` row, not a
resurrection of the old one. `DRAFT -> RUNNING` directly is illegal
(must go through `QUEUED`); only `RUNNING` can go to `PAUSED`, and
`PAUSED` can only return to `RUNNING` or go to `CANCELLED` (not
directly to any outcome state — must resume first).

`transition(current, target) -> target` raises `InvalidJobTransition`
(typed domain error, carries `.current`/`.target`) on an illegal
transition; returns the target unchanged on success. Deliberately
stateless/pure — doesn't mutate a `Job`, callers persist the result.
**Retrofitted the one place that already assigned `Job.status`
directly** (`tests/unit/test_job_models.py`'s lifecycle test, from
T024) to go through `transition()` instead — this is what "database/
service code uses this state machine rather than arbitrary status
assignment" means in practice until T032/T035 exist.

20 new tests: every one of the 11 legal transitions (parametrized),
12 representative illegal ones (parametrized), the two acceptance
criteria phrased literally (completed→running, failed→completed),
pause/resume symmetry, terminal-status exhaustiveness, a
no-status-left-undefined completeness sweep (all 8×8 pairs), and
no-self-transition.

Verified locally: 100 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (32 source files).

## Repository layer (T032)

`app/repositories/base.py`: `SqlAlchemyRepository[OrmT, DomainT]`
(PEP 695 generic syntax — ruff's `UP046` flagged the old
`Generic[...]` subclass form given `target-version = "py312"`) with
shared `get()`/`_paginate()`; `Page[DomainT]` dataclass (items, total,
limit, offset). Repositories never call `session.commit()` — the
caller's `session_scope()` (T020) owns the transaction, which is what
"transaction-aware" means in practice here.

Exactly 7 concrete repositories, matching T032's literal list —
`JobRun` operations folded into `JobRepository` (`create_run`,
`list_runs_for_job`) and `RecordProvenance` into `RecordRepository`
(`add_provenance`), since T032 only names 7 entities for 9 tables.
Each has a `typing.Protocol` (what services depend on) + a
`SqlAlchemy*` concrete class. `JobRepository.update_status()` is the
one place that goes through `app.domain.job_state_machine.transition()`
rather than assigning `.status` directly — enforcing structural
validity is a repository-layer job; deciding *when* to transition
stays in the service layer (T035, doesn't exist yet).

**Added `app/domain/audit.py` (`AuditLogEntry`) — not in T030's
literal entity list**, but the audit repository needs a domain type to
return like every other one does; this is a small, justified addition
at T032, not scope creep into T030's already-closed task.

**Found and fixed a real domain/schema mismatch while writing repo
tests**: `Record.collected_at`, `RecordProvenance.collected_at`, and
`Schedule.next_run_at` all had misleading `datetime | None = None`
defaults in the T030 domain dataclasses, but their DB columns are
`NOT NULL` with no server-side default, AND the repositories forward
them as-is at creation time (unlike DB-generated timestamps like
`created_at`, which repositories never forward). Fixed by making all
three required fields (no default) — this surfaces the mistake at
domain-object construction with a clear `TypeError`, not a confusing
`NOT NULL constraint failed` SQL error three layers down. Updated the
T030 tests that constructed these without the now-required field.

Added a `session_factory` fixture to `tests/unit/conftest.py`
(wrapping `build_session_factory(sqlite_engine)`) and
`tests/unit/factories.py` (plain ORM-row-creation helper functions —
`make_user`/`make_project`/`make_config`/`make_job`) to avoid a 4th/5th
copy-paste of the same setup boilerplate that T023-T026's test files
had each been repeating. Existing test files weren't retrofitted
(out of scope) — only new T032 tests use the shared helpers.

16 new tests across all 7 repositories, working entirely through
domain objects (no SQLAlchemy row type ever appears in an assertion),
including one that proves `update_status` really enforces the state
machine (not just writes whatever status it's given).

Verified locally: 114 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (42 source files).

## Project service (T033)

`app/services/errors.py`: `ServiceError` base + `NotFoundError`,
`PermissionDeniedError`, `InvalidStateError` — shared across every
future service (T034+), deliberately NOT `app.core.errors.ApiError`
(that's HTTP-transport, translated by the API layer later; services
never import `app.core` or `app.api`). `app/services/projects.py`:
`ProjectService` — create/get/list/update/archive, all
owner-authorization-checked via `_require_owner`. Archive, not delete
— no delete method exists anywhere in the project stack.

Added two repository methods T032 didn't include but T033 needed:
`ProjectRepository.update_fields()` and `.set_status()`.

**`ensure_can_start_job()`** is the concrete answer to "archived
project cannot start new jobs" — a guard method living on
`ProjectService` (not duplicated into the not-yet-existing T035 job
service) that T035 will call before creating a `Job`. Raises
`InvalidStateError` for an archived project's owner, `NotFoundError`/
`PermissionDeniedError` first via the same `get_project()` path other
methods use.

Every mutating method calls `_record_audit_event()` →
`AuditLogRepository.create()` — verified directly in tests (not just
"the method didn't crash").

13 new tests: create + audit event, empty-name rejection (both create
and update), cross-user access denial (get and update), not-found,
update + audit event, archive + audit event, the two
`ensure_can_start_job` outcomes, and list-scoping (only the requesting
user's projects come back).

Verified locally: 125 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (45 source files).

## Configuration service (T034) — current task now T035

`app/domain/provider_validation.py` (`ConfigValidationResult`,
`ProviderConfigValidator` Protocol) resolves T034's circular
dependency on T040 — see that file's docstring. `app/services/
configs.py`: `ConfigurationService.create_version()` validates
(generic provider-name check + delegated `validator.validate_config()`)
strictly before creating any row, so an invalid config never becomes
active. New `CollectionConfigRepository.set_active_version()` is the
ONLY mutation ever applied to a `CollectionConfig` row after creation
(`is_active` is a pointer; `provider`/`config_json`/`version` never
change). `activate_version()` lets an existing historical version be
reactivated without creating a new row. Reuses `ProjectService` for
authorization rather than duplicating ownership checks.

Test-only fakes in `tests/unit/fakes.py` — a real `FakeProvider`
matching T040's full contract belongs at that task.

11 new tests: deterministic version numbering, single-active-version
invariant, old-version-content-provably-unmutated-when-active-changes,
invalid config rejected (both generic and provider-delegated),
`activate_version` pointer switch, cross-user access denial.

Verified locally: 134 passed, 1 skipped (T012-gated), ruff clean,
mypy clean (47 source files).

## Job service (T035) — current task now T036

`app/services/jobs.py` (`JobService`): `create_job()` is the one place
"transactional" matters most — idempotency check, ownership +
archived-project guard (`ProjectService.ensure_can_start_job`), active-
config lookup (`ConfigurationService.get_active`), insert, and the
DRAFT→QUEUED transition all happen against the same session, so the
caller's `session_scope()` commits or rolls back all of it together.
`cancel_job`/`pause_job`/`resume_job` just call
`JobRepository.update_status()`, inheriting the T031 state-machine
enforcement for free (no re-validation needed here).

**Added `jobs.idempotency_key` (nullable, `UNIQUE`)** — a real schema
change via `database/migrations/versions/0e4e1aa2581b_...py`.
**This migration is the first ALTER-TABLE-with-constraint in the
project and it failed outright on SQLite** (`NotImplementedError: No
support for ALTER of constraints in SQLite dialect`) — SQLite can't
alter a constraint directly, only Alembic's **batch mode**
(`with op.batch_alter_table(...)`) handles it, via a copy-and-move
strategy; on MySQL batch mode still just emits plain ALTER statements,
so this costs nothing there. **Any future migration that alters an
existing table's columns/constraints (not just CREATE TABLE) must use
`batch_alter_table`, checked by actually running it against SQLite
before assuming it works** — CREATE TABLE migrations (T021-T026) never
exposed this because they don't ALTER anything.
`tests/integration/test_migrations.py`'s new test round-trips
upgrade→downgrade→upgrade→downgrade specifically to catch this class
of bug permanently, not just check table existence like the earlier
migration tests do.

**`retry_job()` resolves a real tension**: T031 made `FAILED` terminal
("a job that needs to run again is a new Job row, not a resurrected
old one" — that decision predates T035 and is unchanged). So retry
creates a **new** `Job` referencing the same project/config; the
original stays `FAILED` forever. Gated by
`app.domain.job_errors.is_retryable()` — a small, explicitly-interim
retryable-error-class set (`transient_network`, `rate_limit`,
`persistence`) that **T044 ("Provider error mapping") must reconcile
with or replace**, not silently diverge from — same resolution pattern
as T034's circular T040 dependency.

14 new tests: creation (+ audit event), no-active-config rejection,
archived-project rejection, idempotency dedup (same key → same job,
different keys → different jobs), cancel/pause/resume (including pause
illegal from QUEUED), retry (creates new job, original untouched,
rejected when not FAILED, rejected when error class isn't retryable),
not-found, cross-user denial.

Verified locally: 148 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (49 source files).

## Record service (T036) — current task now T037

`app/domain/record_search.py` (`RecordSearchFilters`, `RecordSort`/
`RecordSortField`) and `app/services/records.py` (`RecordService`).
`RecordRepository.search()` (new) translates provider/date-range/
"quality" filters and sort into a real server-side SQLAlchemy query —
never fetches unfiltered rows and filters in Python.

**"Quality filtering" has no dedicated schema field yet** (T051,
Validation pipeline, isn't built) — implemented as
`has_provider_id: bool | None`, a genuine, generic, non-provider-
specific proxy (does this record have a resolved stable provider ID,
vs. only a canonical-key fallback). T051 should extend or replace this
with a real `validation_status`/quality field, not silently diverge.

**`MAX_RECORD_PAGE_LIMIT = 200`** enforced inside the repository
itself (`app/repositories/records.py`), not just the service — so
"DO NOT load all records into memory" holds even if a caller bypasses
`RecordService` and calls the repository directly. Chose capped
offset/limit pagination over true cursor/keyset pagination (T036 says
"cursor OR safe pagination" — either satisfies it); revisit with
keyset pagination if T092 (performance review) finds offset pagination
a real bottleneck at production scale.

11 new tests, including the literal "synthetic large dataset" item:
250 records, 3-page pagination proven disjoint; a separate test proves
a 100,000-row request gets clamped to 200. Plus project-scoping,
provider filter, date filter, quality filter, sort order, detail
retrieval, not-found, cross-user denial (both search and detail).

Verified locally: 158 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (51 source files).

## Audit service (T037) — current task now T038

Checked what was already covered before building: `AuditLogRepository`
(T032) existed, and `ProjectService`/`JobService` already called it
via private `_record_audit_event` helpers using ad-hoc string action
names. `ConfigurationService` had **no audit calls at all** — T034's
IMPLEMENT list never mentioned audit (T033's did), so it was
genuinely missing, not an oversight worth flagging separately.

Real new work: `app/domain/audit_actions.py` (`AuditAction` StrEnum —
the single source of truth for action names, e.g.
`AuditAction.PROJECT_CREATED == "project.created"`);
`app/domain/audit_redaction.py` (`redact_details()` — recursively
scrubs keys matching `password`/`secret`/`token`/`api_key`/
`authorization`/`credential`/`private_key`, case-insensitive substring
match); `app/services/audit.py` (`AuditService.record_event()` —
redacts before persisting, requires an `AuditAction` not a raw string).
New `AuditLogRepository.list_for_entity()` (+ `AuditService` wrapper)
— "audit events are queryable" previously only meant "by actor",
now also "by entity" (e.g. full history of one project/job).

**Refactored `ProjectService`/`JobService` to depend on `AuditService`
instead of `AuditLogRepository` directly** (removed each service's
private `_record_audit_event` duplicate), and **added audit calls to
`ConfigurationService`** (`config.created`, `config.activated`) which
had none before. This changed all three services' constructors —
updated every test file that builds them
(`test_project_service.py`, `test_configuration_service.py`,
`test_job_service.py`, `test_record_service.py`) to wrap
`SqlAlchemyAuditLogRepository` in `AuditService` rather than passing
it directly. `test_repositories.py`'s repository-level tests are
unaffected — they intentionally exercise `SqlAlchemyAuditLogRepository`
directly, not through `AuditService`.

12 new tests: redaction (scrubbing + recursive), a real
`record_event()` call proving a password never reaches the persisted
`details`, `list_for_entity` scoping, actor/entity identification.

Verified locally: 164 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (54 source files).

## Authentication (T038) — current task now T039

`app/domain/users.py`: `UserStatus` (StrEnum) + `User` frozen dataclass
— centralizes what `app/db/models/user.py` used to define itself (same
"domain owns status enums" pattern as T030), and adds
`failed_login_attempts`/`locked_until` fields the DB model needed.
`app/domain/auth.py`: `AuthSession`/`IssuedSession` frozen dataclasses,
plus `as_naive_utc()` (see the bug below). `app/db/models/session.py`:
`Session` ORM table (`token_hash` unique, not the raw token — the raw
value only ever exists transiently in `IssuedSession.token`, at
login). Migration `9e753afdce70_...`: creates `sessions`, adds
`users.failed_login_attempts`/`locked_until` — **the autogenerated
`ADD COLUMN ... NOT NULL` for `failed_login_attempts` had no
`server_default`**, which would break against a table with existing
rows; fixed by adding `server_default='0'` by hand and verifying
against a SQLite DB pre-seeded with a user row (backfills to 0
correctly) — autogenerate doesn't infer this from the Python-side
`default=0`.

**Strategy (deliberately the simplest secure option)**: password login
(bcrypt, reused from T022) + opaque server-side session tokens
(`secrets.token_urlsafe(32)`, SHA-256-hashed for storage/lookup —
correct here specifically because a 32-byte random token is already
high-entropy, unlike a human password, so bcrypt's deliberate slowness
would only cost latency for no security benefit). 12-hour session
lifetime, lockout after 5 failed attempts for 15 minutes, no
self-registration (V1 has no public signup requirement anywhere in the
docs), same error message for wrong-password vs. unknown-email (no
enumeration).

**Real bug found (not SQLite-only — this is a MySQL behavior too)**:
`DATETIME` columns drop timezone-awareness on read-back in both
dialects, but a freshly-created-but-not-yet-re-queried ORM object may
still hold Python's original timezone-aware `datetime`, inconsistent
depending on SQLAlchemy identity-map state. Comparing "now"
(`datetime.now(UTC)`, aware) against a stored `expires_at`/
`locked_until` that might be either raised `TypeError: can't compare
offset-naive and offset-aware datetimes` intermittently. Fixed with
`app.domain.auth.as_naive_utc()`, applied to **both** sides of every
such comparison (`AuthSession.is_active`, the lockout check in
`AuthService.login()`) — normalize-both, not just one, or the same bug
resurfaces depending on which side happens to be naive.

**Test-suite runtime caveat, not a bug**: the full suite now takes
~100-130s locally (up from ~40s pre-T038) because `bcrypt`'s
deliberate slowness gets exercised many times per test (each login
attempt hashes/verifies) — `test_repeated_failures_lock_the_account`
alone does 6 bcrypt verifies. **Any tool/harness with a pytest timeout
under ~150s will report a false "killed"/hang** — this happened
repeatedly here before being correctly diagnosed via `--collect-only`
(which completed in 38s, proving collection itself isn't the slow
part) and then a full `-k "auth"` run with a longer timeout (41s,
genuinely passed). Not a real hang; budget test-run timeouts
accordingly for any future auth-service work.

**Also found via the first full-suite run since T035**: the T035
migration round-trip test (`test_idempotency_key_column_migration_
round_trips_on_sqlite`) started failing — not flaky, a real bug in the
*test*: it downgraded with a relative `"-1"` offset, which implicitly
assumed the idempotency-key migration was still `head`. T038 added a
new migration on top, so `-1` from head now undoes the *wrong*
migration. **Fixed by targeting the specific parent revision by name**
(`"bafe7b89931a"`) instead of a relative offset — any migration test
using `downgrade(config, "-1")` from `"head"` is fragile the moment
another migration lands on top; prefer naming the exact revision.

15 new tests (`tests/unit/test_auth_service.py`,
`tests/integration/test_auth_api.py`): login success/wrong-password/
unknown-email(same message)/lockout/counter-reset, expired session
(forges a known raw token via the service's own `_hash_token()` —
acceptable white-box testing — hashes it, inserts a session with a
past `expires_at`, then proves `get_current_user()` rejects it; the
original version of this test only re-asserted `is_active` on an
object never round-tripped through a repository, which didn't
actually prove anything about the real lookup path), logout revocation
+ idempotency, disabled account, unknown/garbage token; plus HTTP-layer
tests for `/api/v1/auth/{login,logout,me}` via `TestClient` with
`get_db` overridden to SQLite (same technique as T014).

`app/api/envelope.py`, `app/api/dependencies.py`, `app/api/v1/auth.py`
establish the `{"data": ..., "request_id": ...}` success envelope
(`docs/05_API_DESIGN.md`) for the first real business routes — every
future route should reuse `Envelope`/`envelope()` rather than
returning a bare Pydantic model. Uses PEP 695 generic syntax
(`class Envelope[T](BaseModel)`, `def envelope[T](...)`), matching
`SqlAlchemyRepository[OrmT, DomainT]`'s existing pattern (ruff's
`UP046`/`UP047` flag the old `Generic[T]`/`TypeVar` form). FastAPI
dependency defaults use `Annotated[X, Depends(...)]`, not
`X = Depends(...)` — matches `app/api/health.py`'s existing style and
avoids ruff's `B008`.

Verified locally: 179 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (63 source files).

## Authorization (T039)

Full review in `database/AUTHORIZATION_REVIEW.md` (same convention as
`database/INDEX_REVIEW.md` for T027). Headline finding: **the
ownership policy was already correctly enforced everywhere a service
exists** (`ProjectService._require_owner`, reused via
`ProjectService.get_project`/`ensure_can_start_job` by every other
service since T033-T036) — T039 formalized/documented that as the
canonical policy rather than re-implementing it, then closed real gaps
found while reviewing:

-   **No route ever mapped `PermissionDeniedError`/`NotFoundError`/
    `InvalidStateError` to HTTP status codes except T038's `auth.py`,
    which did it by hand for one case.** Any future project-scoped
    route (T070+) would have leaked these as unhandled 500s unless
    every route author remembered to catch them individually. Fixed
    with `app/api/service_errors.py`
    (`register_service_error_handlers`) — centralized FastAPI
    exception handlers: `NotFoundError`→404, `PermissionDeniedError`
    →403 (not 401 — by the time a service raises this the caller is
    already authenticated; 401 stays reserved for T038's
    not-authenticated-at-all case, which `auth.py` still handles
    itself), `InvalidStateError`→409. Registered in `app/main.py`
    alongside T014's `register_exception_handlers`. Lives in
    `app.api`, not `app.core.errors`, because `app.core` never imports
    from `app.services` (verified: no existing `app/core/*.py` file
    does) and this handler must import `app.services.errors`.
-   **Missing negative (cross-user) tests on methods that already
    enforced ownership correctly but had no regression test proving
    it**: `ProjectService.archive_project`, `ConfigurationService.
    activate_version`/`list_versions`, `JobService.pause_job`/
    `resume_job`/`retry_job`, and — the literal T039 acceptance
    criterion — `JobService.create_job` when a stranger supplies
    someone else's `project_id`. 6 new tests added across
    `test_project_service.py`/`test_configuration_service.py`/
    `test_job_service.py`. `RecordService` already had full coverage
    from T036 — reviewed, nothing to add.
-   **`ExportService`/`ScheduleService` don't exist yet** (only
    domain/repository layers, from T026/T032) — enforcing
    authorization on services that don't exist yet would mean
    inventing their method signatures speculatively. Documented as a
    binding obligation for T080/T083 (each already lists "validate
    project authorization" as their own first implement step) rather
    than built speculatively here.
-   **No project-scoped HTTP endpoint exists yet** — only T038's auth
    router is mounted. "Review every project-scoped endpoint" (T039
    item 9) has nothing to review at the HTTP layer today; recorded as
    a transitive obligation on every T070+ route (must call a
    service's `requesting_user_id`-checked method, never query a
    repository directly from a route handler) and pre-verified via
    `tests/integration/test_service_error_handlers.py`, which proves
    the 403 mapping works correctly ahead of any real route existing.

3 new tests (`test_service_error_handlers.py`) + 6 new negative-access
tests = 9 new tests total.

Verified locally: 185 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (66 source files).

## Provider interface (T040) — current task now T041

`app/domain/provider_contracts.py`: `UsageEstimate` (validates
non-negative), `RawProviderItem` (PEP 695 `type` alias for
`Mapping[str, Any]`, matching `Envelope[T]`'s PEP 695 style),
`NormalizedItem` (`provider_record_id`/`data` — field names
deliberately match `Record.provider_record_id`/`Record.data` for a
direct 1:1 mapping once T052/T053 build the real pipeline),
`ProviderErrorCategory` (StrEnum, the exact 7 categories from
`docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md`'s "Errors" section:
authentication/quota/rate/invalid_request/temporary/permanent/
unknown), `ProviderError`, `ProviderHealth`. `ConfigValidationResult`
deliberately stays where T034 put it
(`app.domain.provider_validation`) — reused, not duplicated, exactly
as that file's own docstring said T040 should do.

`app/providers/base.py` (new package, per
`docs/24_BACKEND_FILE_PLAN.md`): `ProviderAdapter`
(`@runtime_checkable` Protocol) — `validate_config`/`estimate`/
`collect`/`normalize`/`classify_error` naming matches the T000-resolved
decision exactly (docs/16_MEMORY.md's "Resolved design decisions"), so
a future `GoogleMapsProvider` (T041-T044) implements this contract
directly rather than inventing its own method names. `collect()`
returns `Iterator[RawProviderItem]`, not a buffered list/result object
— same "never require everything in memory at once" principle T036
applied to `RecordService`. No SDK import, no HTTP client, no browser
automation reference anywhere in this module (T040's explicit "DO
NOT" instructions) — the module docstring says so explicitly as a
guardrail for future edits.

**One deliberately-NOT-built piece, flagged rather than silently
skipped**: docs/07 describes a future `ProviderRegistry` that would
let `ConfigurationService`'s `ProviderConfigValidator` dispatch across
multiple registered `ProviderAdapter`s by name. No task in
`docs/00_TASK_INDEX.md`/`docs/T0*_PROMPT.md` currently lists building
that registry, and T040's own IMPLEMENT list doesn't mention it — so
it's out of scope here, documented in `ProviderAdapter`'s docstring
rather than built speculatively ahead of a task that asks for it.

**Interim taxonomy note carried forward, not resolved here**:
`app.domain.job_errors.RETRYABLE_ERROR_CLASSES` (T035's interim
job-failure retry set: `transient_network`/`rate_limit`/`persistence`)
is a different, already-existing taxonomy from
`ProviderErrorCategory`'s 7 categories — T044 ("Provider error
mapping") is where these get reconciled, not T040 (T040 has no
dependency on T035/T044 and doesn't touch job retry logic).

`FakeProviderAdapter` added to `tests/unit/fakes.py` (that file's
docstring already said this belonged there, written at T034):
deterministic, no I/O, configurable raw items;
`classify_error` maps `TimeoutError` → `TEMPORARY`, anything else →
`UNKNOWN` (a real adapter's classification, T041+, will be far more
specific — this is just enough for the contract test to prove
dispatch happens).

12 new tests (`tests/unit/test_provider_interface.py`): protocol
satisfaction via `isinstance(fake, ProviderAdapter)` (only possible
because the Protocol is `@runtime_checkable`), config validation
(valid/invalid), `UsageEstimate` reflecting available items + its own
negative-value rejection, `collect()` proven to be a real lazy
iterator (not a list — `iter(items) is items`) that yields every raw
item, `normalize()`'s exact field mapping, both `classify_error`
branches, `health_check()`, and a full
validate→estimate→collect→normalize lifecycle test matching docs/07's
diagram (minus the budget check and the real network call, neither of
which exist yet).

Verified locally: 197 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (67 source files).

## Google configuration (T041) — current task now T042

`app/providers/google_maps/config.py` (new subpackage, per
`docs/24_BACKEND_FILE_PLAN.md`'s `app/providers/google_maps/`):
`GoogleMapsConfigValidator`, satisfying T034's
`ProviderConfigValidator` Protocol exactly — this is the first
*real* validator plugged into `ConfigurationService` (every use before
this was a `tests/unit/fakes.py` fake). No network call, no SDK — pure
validation, matching T041's scope boundary against T042 (which builds
the actual HTTP client) exactly.

**Selected operation — a design decision this task had to make, no
doc pinned one down**: **Places API (New) — Text Search**
(`POST /v1/places:searchText`), chosen because docs/07's conceptual
example config (`query` + `location` + `radius_meters` + `fields` +
`max_results`) matches that operation's shape exactly — Nearby Search
filters by place type rather than free text, and the legacy (pre-2025)
Places API is deprecated in favor of "New". Recorded as a resolved
decision T042 must build against or explicitly revise, same pattern as
T000's four resolved disagreements.

**Verified against Google's live public docs on 2026-08-20** (fetched
directly, not recalled from training data — Google Maps Platform specs
change and this agent's knowledge cutoff predates "today"):
`https://developers.google.com/maps/documentation/places/web-service/text-search`
(pageSize/maxResultCount 1-20 per page, 60 results total across all
pages — `MAX_RESULT_COUNT`; locationBias circular radius 0.0-50,000.0
meters — `MAX_RADIUS_METERS`; `X-Goog-FieldMask` required, no default
field list) and
`.../data-fields` (field→SKU-tier mapping — `ALLOWED_FIELDS` here is a
curated subset of real, current field names, not Google's entire
catalog). **Must be reverified against those same live pages before
production release** — this is T041 item 10's explicit instruction,
not just good practice; a config validator silently trusting stale
limits would defeat the entire point of "invalid requests never reach
provider execution."

**This app's config field names are snake_case
(`docs/CODING_STANDARDS.md`'s convention) — deliberately NOT Google's
own camelCase request-body field names.** Translating
`{"query": ..., "fields": [...]}` into the real
`{"textQuery": ..., <X-Goog-FieldMask header>}` shape is T042's job;
T041 only proves a config *could* become a legal request.

**Server-side credential presence, checked here specifically because
T041's own IMPLEMENT list asks for it**: `GoogleMapsConfigValidator`
takes `api_key: str | None` at construction (sourced from
`app.core.config.Settings.google_maps_api_key`, added at T014, unused
until now) — never read from the `config` dict itself, so a request
body can never smuggle in a credential value. Missing key produces a
deliberately generic error message (same "don't leak operational
detail" instinct as T038's same-message-for-wrong-password/
unknown-email, for a different reason here).

**A genuinely useful catch, not a hypothetical**: docs/07's own
conceptual example config literally uses `"max_results": 100` — 40
over Google's real 60-result cap. `test_max_results_over_googles_
hard_cap_is_rejected` uses exactly that value, proving the validator
catches the docs' own example as unrealistic, with an actionable error
naming the real limit — exactly the kind of gap T041 exists to close
before a job ever reaches the worker.

19 new tests (`tests/unit/test_google_maps_config.py`): every rule
individually broken from one fully-valid example config (proving each
rule causes its own rejection, not some interacting combination),
multiple simultaneous violations all reported together, and one
service-layer test wiring `GoogleMapsConfigValidator` into a real
`ConfigurationService` (not a fake) proving an invalid config never
becomes an active, persisted version — T041's literal acceptance
criterion.

Verified locally: 216 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (69 source files).

## Google client (T042) — current task now T043

`app/providers/google_maps/client.py`: `GoogleMapsClient` — the real
HTTP boundary against `POST
https://places.googleapis.com/v1/places:searchText` (httpx 0.28.1,
newly promoted from a dev-only dependency to a real
`[project.dependencies]` entry in `apps/api/pyproject.toml`, since it's
now used at runtime, not just by `TestClient` in tests). Owns exactly
one concern — talking to Google — and deliberately does NOT validate
configs (T041 already did) or classify errors into
`ProviderErrorCategory` (T044's job); `GoogleMapsApiError` is the
stable, structured shape T044 will classify.

**Retry policy, a deliberate design decision worth remembering**: only
transport failures and HTTP 5xx are retried automatically inside this
client (`max_retries`, default 2, no real backoff delay needed at this
layer — these are simple immediate-retry-on-infra-hiccup cases, not
policy-sensitive). **4xx responses (auth/invalid-request/quota/rate)
are never retried here** — docs/07's "Important rule" (never bypass a
quota/rate/authorization/policy denial) means an immediate in-client
retry with no real elapsed time would look exactly like bypassing;
those failures propagate as `GoogleMapsApiError` for the *job*-level
retry path (`JobService.retry_job`, T035, already exists) to decide
about later, with real time between attempts. Verified directly:
`test_authentication_error_is_never_retried`/
`test_quota_error_is_never_retried` assert `call_count == 1`.

**Field mask construction**: T041's `config["fields"]` (unprefixed,
e.g. `"displayName"`) get prefixed to Google's real
`"places.displayName"` syntax here, plus `"places.id"` (always, even
if not requested — normalize()/T043 will need *something* to identify
the raw item by) and `"nextPageToken"` (needed to know if another page
exists) are always appended — this app-level config vs. real Google
request-body translation boundary (T041 validates the former, T042
builds the latter) is deliberate, not accidental duplication.

**Pagination**: loops requesting `min(20, remaining)`-sized pages
(Google's real per-page cap) until either the config's `max_results`
(default `MAX_RESULT_COUNT` = 60, from T041's config module — reused,
not re-declared) is reached or Google stops returning `nextPageToken`.
Lazy generator — a caller consuming only the first few items never
triggers a second page request.

**Usage/quota metadata (item 7)**: verified against the same live
Google docs fetched for T041 that Text Search (New) responses carry no
documented per-call quota/usage-remaining field or header — recorded
as an honest "not available", not a gap; quota exhaustion surfaces via
the structured-error path (`RESOURCE_EXHAUSTED` status) instead, for
T044 to classify.

**Credential loading (item 1) — deliberately minimal, not
speculative**: `GoogleMapsClient.__init__` requires `api_key: str`
(never optional, never read from a request body); no FastAPI
dependency/factory function wires it to `Settings.
google_maps_api_key` yet, because nothing consumes this client yet
(same reasoning as T041's validator having no route to attach to —
that wiring belongs to whichever task first actually calls this
client, likely the worker at T060+). `http_client: httpx.Client | None`
is the injection point (item 10) — every test uses
`httpx.MockTransport`, never a real network call, matching the literal
T042 acceptance criterion ("Mock tests verify request construction and
response handling; no real credentials are committed" —
`test_api_key_never_appears_in_a_raised_error_message` checks this
directly, not just by absence of a real key in the repo).

17 new tests (`tests/unit/test_google_maps_client.py`): endpoint URL +
credential header, exact field-mask string, request body field mapping
(query/location/radius/omitted-when-absent), single-page yield,
early-stop once `max_results` is reached mid-page, multi-page
pagination (page-token propagation verified on the wire, not just the
yielded count), 5xx retry-then-succeed and retry-exhausted, transport-
error retry-then-succeed and retry-exhausted, auth/quota errors proven
never retried, and the credential-never-leaks check.

**Side note, unrelated to T042's own logic but caught while re-running
`pip install -e ".[dev]"` after moving `httpx` to real dependencies**:
`bcrypt` was pinned `>=4.1,<5.0` in `pyproject.toml` but the installed
venv actually had `5.0.0` (outside that range) — the reinstall
corrected it to `4.3.0`. Not a T042 bug; just a pre-existing
unenforced-until-now pin mismatch, worth knowing if bcrypt behavior
ever seems to have silently changed underfoot again.

Verified locally: 233 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (70 source files).

## Google response mapper (T043) — current task now T044

`app/providers/google_maps/mapper.py`: `normalize_place(raw_item) ->
NormalizedItem` — the real Google implementation of
`ProviderAdapter.normalize()` (T040's Protocol). `map_place_to_
record_draft(raw_item, *, project_id, job_id, collected_at) ->
RecordDraft` — combines it with job/project context and a collection
timestamp normalize() itself can't know (T043 items 7/8), for the
worker (T060+) to call once it orchestrates a real run.

**New domain type**: `app.domain.records.RecordDraft` — a `Record`
minus `id`/`canonical_key`/`created_at`/`updated_at`, since canonical
key computation is explicitly Stage 5 of
`docs/08_DATA_PIPELINE_DEEP.md` (T052), not this task's job. Added
next to `Record` in `app/domain/records.py`, not inside the
`google_maps` subpackage — the shape is provider-agnostic even though
today only `map_place_to_record_draft` produces one.

**Field mapping is exhaustive over T041's `ALLOWED_FIELDS` exactly** —
`displayName.text`→`name`, `formattedAddress`→`formatted_address`,
`location.{latitude,longitude}`→same (both required together — a
partial pair from a malformed response is treated as fully absent, not
half-populated), `businessStatus`/`priceLevel`→lowercased,
`primaryType`→`primary_type`, `types`→filtered to string entries only,
`rating`→`float`, `userRatingCount`→`int`,
`internationalPhoneNumber`→`phone_number`, `websiteUri`→`website`,
`currentOpeningHours.{openNow,weekdayDescriptions}`→`open_now`/
`weekday_descriptions` (flattened out of the nested object — nothing
else from that object is kept). `id`→`provider_record_id` (top-level
on `NormalizedItem`, not inside `data`).

**Malformed-input handling, the key design decision (T043 item 10)**:
a field present but of the wrong type is treated *exactly* like a
missing field — silently omitted from `data`, never coerced, never
raises. Verified directly:
`test_malformed_response_never_crashes_and_produces_no_data` feeds a
fixture where every single field has the wrong type and asserts the
result is `NormalizedItem(provider_record_id=None, data={})` — no
exception, no invented values. True schema *validation* (marking a
response `warning`/`rejected`) is Stage 4 of the pipeline doc, a
separate task (T051) — explicitly not this one's job, documented in
the module docstring so a future edit doesn't accidentally conflate
the two.

**Provider/source reference (item 3)**: Places API (New) has no
separate "reference" field distinct from `id` (the legacy Places API's
did, dropped in "New") — `GOOGLE_MAPS_TEXT_SEARCH_OPERATION =
"google_maps.places.text_search"` is what T054 (persistence) should
record as `RecordProvenance.provider_operation`;
`RecordProvenance.source_reference` should stay `None` for this
operation, a deliberate documented decision, not a gap.

**Fixture-based tests, per T043's own instruction** — new
`tests/fixtures/google_maps/` directory (first fixtures directory in
the project; not under `tests/unit/` or `tests/integration/` since
fixtures are shared test data, not tests themselves):
`full_place.json` (every handled field populated, real Google response
shape), `minimal_place.json` (only `id`/`displayName` present),
`malformed_place.json` (every field present but wrong-typed). 10 new
tests (`tests/unit/test_google_maps_mapper.py`), including the literal
acceptance criterion (`test_same_fixture_always_produces_the_same_
result`) and the malformed-response test above.

Verified locally: 243 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (71 source files).

## Provider error mapping (T044) — current task now T045

`app/providers/google_maps/errors.py`: `classify_google_maps_error()`
— the real Google implementation of `ProviderAdapter.classify_error()`
(T040's Protocol), mapping `GoogleMapsApiError` (T042) into T040's
`ProviderErrorCategory` taxonomy using Google's own `error.status`
string (`google.rpc.Code`-style: `UNAUTHENTICATED`,
`INVALID_ARGUMENT`, `RESOURCE_EXHAUSTED`, `UNAVAILABLE`, ...) with an
HTTP-status-code fallback when that string is missing/unparseable.

**Extended `ProviderError` itself (T040's shape), because T044's own
IMPLEMENT list needs fields it didn't have**: added `retryable: bool`
(mandatory, no default — item 8, "mark retryability explicitly," can
never be silently skipped) and `http_status_code`/`provider_status`
(item 7, "preserve safe diagnostic context" — generic field names, any
HTTP-based provider has both). `default_retryable_for_category()`
(new, `app.domain.provider_contracts`) is the taxonomy-level default
retry policy — `{RATE, TEMPORARY}` retryable, everything else not —
derived directly from `docs/09_JOB_QUEUE_WORKER_DEEP.md`'s "Do not
retry: invalid configuration; invalid credentials; forbidden
operation; provider policy rejection" (quota exhaustion **is** a
provider policy rejection, not retryable, despite docs/07 mentioning
it alongside rate in the same "stop/backoff" sentence — rate limiting
is the industry-standard retry-after-backoff case, quota is a harder
cap that needs a human, not a retry).

**A genuine upstream limitation, documented rather than worked
around**: Google's Places API (New) does not expose a status distinct
from `RESOURCE_EXHAUSTED` for "sending too fast" versus "quota
allotment used up" — both look identical. This adapter maps
`RESOURCE_EXHAUSTED`/429 to `QUOTA` only; `ProviderErrorCategory.RATE`
exists for providers that DO distinguish the two, and this Google
adapter simply never produces it. `TimeoutError`/network-transport
failures (`GoogleMapsApiError.status_code is None`, meaning
`GoogleMapsClient` already exhausted its own `max_retries`) classify
as `TEMPORARY`.

**Reconciled `app.domain.job_errors` with the new taxonomy (the
"T044 must reconcile" note from T035/T040's memory entries) —
`Job.error_code` now holds either one of `ProviderErrorCategory`'s own
string values, or `"persistence"`**, a separate, always-retryable,
explicitly non-provider code for a transient database failure during a
write (`ProviderErrorCategory` was never meant to cover that). This
replaces T035's original provisional set
(`"transient_network"`/`"rate_limit"`/`"persistence"`) — the first two
are superseded now that the real taxonomy's own string values exist.
**Updated `tests/unit/test_job_service.py`'s
`test_retry_creates_a_new_job_when_error_is_retryable`**, which used to
assert on the now-removed `"transient_network"` — changed to
`"temporary"`, the reconciled equivalent; nothing else needed to
change since `"authentication"` (used by the sibling non-retryable
test) was already a valid `ProviderErrorCategory` value by
coincidence.

22 new tests: `tests/unit/test_google_maps_errors.py` (every documented
Google status → category mapping, the HTTP-status fallback path, an
unrecognized 4xx → `PERMANENT`/not-retryable, an unrecognized
non-4xx/5xx status → `UNKNOWN`/not-retryable, retryability for
auth/quota vs. temporary, diagnostic context preservation, and the
literal T044 acceptance criterion — two identical classified errors
yield the same retry decision).

Verified locally: 265 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (72 source files).

## Provider contract tests (T045) — current task now T050, Phase 4 (Provider) now complete

`app/providers/google_maps/provider.py`: `GoogleMapsProvider` — the
first, and so far only, concrete `ProviderAdapter` (T040's Protocol)
in the codebase, assembled purely by composition from every piece
built T041-T044 (`validate_config`→`GoogleMapsConfigValidator`,
`collect`→`GoogleMapsClient.search_text`,
`normalize`→`normalize_place`,
`classify_error`→`classify_google_maps_error`). No new business logic
of its own. `isinstance(provider, ProviderAdapter)` passes — concrete
proof the whole chain genuinely satisfies the Protocol, not just each
piece in isolation.

**`estimate()`/`health_check()` had no implementation anywhere before
this** (flagged as an open question in T044's own memory entry) —
written here, honestly scoped rather than invented: `estimate()`
reports exactly the config's own `max_results` (already bounded by
T041's `MAX_RESULT_COUNT`) since Google's Places API (New) has no
pre-call usage-estimate endpoint (verified, not assumed);
`health_check()` only confirms the adapter was constructed with a
credential — it deliberately does NOT spend real API quota on a live
probe call just to answer a routine health check, since no task asked
for that and it would be real, ongoing cost for no task-driven reason.

**Found and fixed a real robustness gap in T042's `GoogleMapsClient.
search_text()` while writing the "malformed response" test (T045 item
4)**: a top-level malformed response (`places` present but not a list,
e.g. a string) would have made `for place in places` iterate the
string's *characters* instead of failing gracefully — T043's "never
invent, never crash" principle wasn't actually applied at the
collection layer, only at the per-item mapping layer. Fixed:
`places` is now type-checked (treated as empty if not a list), and
each `place` entry is type-checked too (skipped if not a dict) — same
principle, now applied consistently at both layers.
`nextPageToken` handling tightened the same way (empty-string/
non-string token now correctly stops pagination, matching the
original intent that a slightly looser check had drifted from).

**New fixtures** (`tests/fixtures/google_maps/`, extending T043's
per-place fixtures with full search-response and error-response
shapes): `text_search_response_{valid,empty,malformed}.json`,
`text_search_response_page{1,2}.json` (pagination), `error_
{quota,authentication,transient}.json` (realistic Google error bodies,
matching T044's classifier inputs).

15 new tests
(`tests/unit/test_google_maps_provider_contract.py`) — one per T045
IMPLEMENT item (valid/empty/malformed/paginated collection, quota/
authentication/transient error classification with retry-count
assertions, normalization delegation, provenance survival through the
full collect→normalize chain, deterministic mapping), plus the
Protocol-satisfaction proof and `validate_config`/`estimate`/
`health_check`/unknown-exception-fallback coverage for the two methods
this task itself introduced.

**Phase 4 (Provider) is now fully complete** — T040 (interface) →
T041 (Google config validation) → T042 (Google HTTP client) → T043
(Google response mapping) → T044 (Google error classification) → T045
(assembled + contract-tested). Every method of `ProviderAdapter` has a
real, tested Google implementation. Still true and unchanged: no real
network call has ever been made against Google in this codebase — the
next genuine "does this actually work against the live API" check
happens whenever the user is ready to supply a real
`GOOGLE_MAPS_API_KEY` and run a manual smoke test; nothing in the
documented task list currently asks for that explicitly before T050+.

Verified locally: 280 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (73 source files).

## Normalization pipeline (T050) — current task now T051, Phase 5 (Data pipeline) started

`app/pipeline/normalize.py` (new package, per
`docs/24_BACKEND_FILE_PLAN.md`'s `app/pipeline/normalize.py`) — Stage 3
("Normalization") of `docs/08_DATA_PIPELINE_DEEP.md`, applied AFTER a
provider's own field mapping (T043's `normalize_place()` does Stage-1-
equivalent field mapping only; this is the separate, later stage).
`FieldKind` (StrEnum: `TEXT`/`URL`/`NUMBER`/`TIMESTAMP`/`CATEGORY`) +
`normalize_record_data(data, field_kinds) -> dict` — pure, total,
never raises.

**Key design decision: field kinds are supplied by the caller, never
guessed from a value's shape.** A string is only URL-normalized
because the caller declared that key `FieldKind.URL`, never because it
happens to start with `"http"`. This keeps "do not silently replace
missing values with invented defaults" (item 8) honest at the
*kind-detection* level too — heuristic shape-guessing would risk
mis-normalizing a field that only coincidentally looks like a URL/
number/timestamp. Undeclared keys default to `FieldKind.TEXT` (the one
universally-safe transform: trim + NFC).

**Unicode: NFC only, never NFKC** — NFC unifies canonically-equivalent
representations of the same character (lossless); NFKC would fold
compatibility variants (™→TM, fullwidth→ASCII digits, ligatures split
apart), which changes actual content. This is the literal meaning of
item 2's "normalize Unicode **only where safe**."

**Every per-kind transform falls back to text-only cleanup (trim+NFC)
when the value doesn't match its declared kind's shape** — a non-
numeric string under `FieldKind.NUMBER`, an unparseable or
no-explicit-timezone timestamp, a malformed/non-absolute URL. Never
coerced, never dropped, never guessed. Numeric coercion is
deliberately narrow: only a strict `-?\d+(\.\d+)?` pattern converts
(no currency symbols, no thousand separators — those are
locale-specific and would require guessing a format). Timestamp
canonicalization only fires when the input has an *explicit* timezone
(offset or `Z`) — a naive timestamp is left untouched rather than
assuming a timezone that was never stated.

**Wired into the existing pipeline immediately, not left an orphaned
module**: `app/providers/google_maps/mapper.py`'s
`map_place_to_record_draft()` now runs its output through
`normalize_record_data()` before building `RecordDraft`, using a new
`FIELD_KINDS` constant declaring Google's own mapped field names'
kinds (`name`→TEXT, `website`→URL, `rating`/`user_rating_count`/
`latitude`/`longitude`→NUMBER, `business_status`/`primary_type`/
`types`/`price_level`→CATEGORY, ...). `normalize_place()` itself
(matching `ProviderAdapter.normalize()`'s Protocol exactly, T040) is
left untouched — Stage 3 normalization is a separate, explicit step,
not silently folded into the Protocol method. Existing T043 tests for
`map_place_to_record_draft()` still pass unchanged since the
`full_place.json` fixture's values were already "clean" (no extra
whitespace, already-lowercase enums, already-typed numbers) — verified
by re-running them, not just assumed.

**Found and worked around a real tool-level limitation while writing
the Unicode NFC/NFKC test**: typing two visually-identical accented
characters (one meant to be NFC-composed, one NFD-decomposed) as
literal source text is unreliable — the file-editing tool could not
reliably distinguish/match them once written, likely because *some*
layer in the write/read/match chain silently re-normalizes non-ASCII
text. Fixed by building both forms explicitly from code points via
`chr(0x0065) + chr(0x0301)` (NFD) vs `chr(0x00E9)` (NFC) instead of
typing either as a literal character — the test file is now pure
ASCII throughout. Worth remembering for any future test that needs a
*specific, exact* non-ASCII byte sequence: build it with `chr()`/
`\uXXXX` escapes, don't type it as a literal character and trust it
survives unchanged.

25 new tests (`tests/unit/test_pipeline_normalize.py`) — one section
per T050 IMPLEMENT item, plus a dedicated regression fixture
(`tests/fixtures/pipeline/normalize_regression.json`, item 10,
distinct from the inline per-transformation tests) covering every kind
in one realistic mixed record, and a literal determinism test (item
"Given the same input, output is identical").

Verified locally: 305 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (75 source files).

## Validation pipeline (T051) — current task now T052

`app/pipeline/validate.py`: `RecordQuality` (StrEnum:
VALID/WARNING/REJECTED), `FieldRule`, `FieldValidationError`,
`ValidationResult`, `validate_record_draft()` — Stage 2 ("Schema
validation") + Stage 4 ("Quality") of
`docs/08_DATA_PIPELINE_DEEP.md`, combined into one pass since a field
either passes or fails with a severity, and the record's overall
verdict is just the worst severity among its fields. Same
"caller-declares-the-rules" principle as T050's `FieldKind` — nothing
guessed from a field's name or value shape.

**Key design decision, directly matching docs/08's own two worked
examples**: "missing" is not the same knob as "present but invalid."
`FieldRule.missing_severity` (`None` = fine if absent) is what a
field's *absence* becomes; `FieldRule.severity` (for a type/range/
URL-syntax failure) is what a *present-but-wrong* value becomes. This
is exactly what lets `website` be a WARNING when missing but
REJECTED-severity type-checked when present, and lets `name` be
REJECTED when missing — a single `required: bool` flag couldn't
express both of docs/08's examples ("missing website → warning",
"invalid coordinate → rejected") with one field-rule shape.

Coordinate range validation (item 5) needed no dedicated mechanism —
it's just `min_value`/`max_value` applied to a coordinate-shaped
field, the same generic range check any other numeric field uses.
URL syntax validation (item 6) is syntax-only (`urllib.parse.urlsplit`,
checking scheme ∈ {http, https} + non-empty host) — never a real
request, which is what makes "does not make network calls" (T051's
literal acceptance criterion) trivially true. `_isinstance_strict()`
guards against `bool` silently passing a numeric type check (`bool`
is a subclass of `int` in Python).

**Wired into `app/providers/google_maps/mapper.py` immediately**:
`GOOGLE_FIELD_RULES` (name required/REJECTED-if-missing,
latitude/longitude range-checked, rating range-checked as WARNING,
website WARNING-if-missing + URL-syntax-checked) +
`validate_google_place_record()` — kept as an explicit, separately
callable step from `map_place_to_record_draft()`, not silently
chained into it, matching the composable-stages pattern established
since T041/T042 (config validation and the HTTP client stayed
separate calls, never merged).

28 new tests: `tests/unit/test_pipeline_validate.py` (one section per
T051 IMPLEMENT item, including the exact valid/warning/rejected
scenarios from docs/08's own examples) +
`tests/unit/test_google_maps_mapper.py` (3 new tests proving
`validate_google_place_record()` produces the right verdict through
the real Google field rules, not just `app.pipeline.validate` in
isolation).

Verified locally: 333 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (76 source files).

## Canonical identity (T052) — current task now T053

`app/pipeline/canonical_identity.py`: `compute_canonical_key()` — Stage
5 of `docs/08_DATA_PIPELINE_DEEP.md`. Fully generic (no Google-specific
wiring needed in `app/providers/google_maps/mapper.py`, unlike T050/
T051 — this function needs no per-field declarations, it works
directly on any `RecordDraft`).

**Resolved a real ambiguity between T000's conceptual decision and the
actual schema**: T000 (docs/16_MEMORY.md) said the canonical key
should be "project_scope + provider + provider_id" — but `records`'s
real unique constraint (T025) is the *composite*
`UniqueConstraint(project_id, canonical_key)`, which already scopes
uniqueness per-project structurally. So `project_id` does **not** need
to be textually embedded in the returned string (T025's own
cross-project-dedup test already proves the same literal key is
allowed to repeat across projects) — only `provider` needs embedding,
since the DB constraint has no separate `provider` dimension of its
own.

**Preference order, per T052 item 1 and the DO NOT list ("never use
business name alone")**: `RecordDraft.provider_record_id` (Google's
place `id`) always wins when present — `f"{provider}:{provider_record_id}"`.
Falls back to `name` + `formatted_address` **together** only when no
provider identifier exists.

**Fallback key is a SHA-256 hash of the normalized name+address pair,
not the raw text** — `canonical_key` is `String(512)`
(`app/db/models/record.py`); a raw long name/address could exceed
that, and truncating instead would risk two different long addresses
colliding on a shared prefix. The hash is computed over the
*normalized* input, so it's still fully deterministic.

**Identity normalization is deliberately more aggressive than T050's
`FieldKind.TEXT`**: lowercased + whitespace-collapsed (not just
trimmed + NFC) — this text is only ever compared, never displayed, so
"Example Cafe" / "example cafe" / "Example   Cafe" must all produce
the same key, which would be wrong behavior for T050's *display*
normalization but is exactly right here.

**Known collision limitations documented directly in the module
docstring (T052 item 9, not solved — no fallback heuristic can be
perfect)**: a false merge is possible if two different businesses
share both an identical name and address string (e.g. two same-named
shops in one plaza); a false split is possible if the same business's
address differs by more than whitespace/case (e.g. "St" vs. "Street",
a missing suite number) — only Unicode/whitespace/case differences are
normalized away, no abbreviation expansion or fuzzy matching. This is
exactly why the provider identifier path is always preferred when
available.

15 new tests (`tests/unit/test_pipeline_canonical_identity.py`):
provider-id preference (even when name/address also exist), provider
embedded so different providers never collide, fallback triggers only
when no id exists, bounded-length hash even for absurdly long input,
raises when insufficient data exists (missing id AND missing name/
address, or either alone), the DO NOT rule (same name + different
address never collide), repeated-identical-input determinism (both
paths), minor-formatting-difference insensitivity (case + whitespace),
and different-businesses non-collision (both name-differs and
address-differs cases).

Verified locally: 348 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (77 source files).

## Deduplication (T053) — current task now T054

`app/pipeline/deduplicate.py`: Stage 6 of the data pipeline, split into
two independently-testable composable steps (same pattern as every
prior pipeline stage this session): `deduplicate_within_batch()`
(pure, no DB — items 1-2, within-page and across-page dedup via one
streaming `seen` set) and `resolve_against_existing()` (DB-touching,
item 3 — uses `RecordRepository.get_by_canonical_key()`, which was
already added at T032 with a comment anticipating exactly this).
`deduplicate_batch()` composes both and accumulates `DedupSummary`
(item 6).

**New repository method needed and added**:
`RecordRepository.update_collected_data()` (Protocol + SQLAlchemy impl,
`app/repositories/records.py`) — T032 never added an update path since
nothing needed one until now. Refreshes `data`/`collected_at`/`job_id`
on an existing row; never touches `canonical_key`/`provider_record_id`/
`project_id` (identity doesn't change on an update).

**Update-vs-skip (item 5), a deliberate default**: `update_existing=True`
by default — a repeat collection refreshes the existing row's data
(ratings/hours/status genuinely go stale; a collection product whose
records never refresh has limited value). `job_id` moves to whichever
job most recently re-collected the record. `update_existing=False`
(skip) is fully supported too, not hypothetical — a real, equally
exercised code path, not a default assumed to be the only option.

**`deduplicate_within_batch()` yields every draft, not just first
occurrences** — `(draft, canonical_key, is_duplicate)` for all of
them, so `deduplicate_batch()` can tally duplicate counts (item 6) in
one pass without a second one just to count what got dropped. (First
draft of this function only yielded first-occurrences and silently
dropped the rest — caught immediately while wiring the summary
accumulator, since there was nowhere left to increment
`duplicates_in_batch` from.)

**Database constraint test (item 9)** proves the final safety net
independently of this module's own logic: two `RecordRow` inserts with
the same `(project_id, canonical_key)`, added directly (bypassing
`deduplicate_batch()` entirely), and the second `session.flush()`
raises `IntegrityError` — the DB-level `UniqueConstraint` from T025 is
what makes T053's acceptance criterion ("repeated collection does not
create uncontrolled duplicate rows") true even if application logic
had a bug, not just when it behaves correctly. Uses two separate
`session_scope()` blocks (matching `tests/unit/
test_project_and_config_models.py`'s established pattern) — asserting
an expected `IntegrityError` from inside an already-open `session_scope`
block would leave that session unable to commit afterward.

11 new tests: within-page dedup, across-page dedup (a generator
spanning two "pages"), create/update/skip against a real repository +
SQLite, `DedupSummary` counting every outcome kind in one batch (item
6), false-merge (two different businesses, both kept, item 7),
duplicate-batch (5 repeats of one record → exactly 1 row + 4 counted
duplicates, item 8), and the database-constraint test above (item 9).

Verified locally: 359 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (78 source files).

## Transactional persistence (T054) — current task now T055, Phase 5 nearly complete

`app/pipeline/persist.py`: `persist_batch()`/`_persist_one()` — Stage 7
of the data pipeline. Wraps each of T053's per-record dedup decisions
in its own SAVEPOINT (`session.begin_nested()`), so one record's
failure rolls back only that record, never siblings already
successfully written earlier in the same outer transaction. This is
the literal reading of "a failed transaction does not leave partial
inconsistent state" at *record* granularity, not batch-wide
all-or-nothing — matching docs/08's "never hide failures"/
`partially_completed` philosophy (a batch of 500 where 50 fail should
report 450 real successes, not discard them).

**A real correctness gap in T053, found and fixed while designing
this task, not hypothetical**: T053's `DedupSummary` incremented
counters right after `repository.create()`/`update_collected_data()`
returned — but those only `flush()`, not `commit()`. If a *later*
record in the same outer transaction had failed and the whole
`session_scope()` rolled back (T053 had no per-record isolation),
T053's counters would have already claimed successes the rollback then
silently undid. T054's SAVEPOINT wrapping is what makes each record's
own success durable *within* the still-open outer transaction,
independent of what happens to later records — counters (item 5) are
only incremented after a record's SAVEPOINT actually releases.

**Provenance (item 3)**: only recorded for an actual write (CREATED/
UPDATED) — nothing to attach it to for a skip. `provider_operation` is
caller-supplied (e.g. `app.providers.google_maps.mapper.
GOOGLE_MAPS_TEXT_SEARCH_OPERATION`, which T043 left specifically for
this) — this module has zero Google-specific imports, same
provider-agnostic principle as every `app.pipeline` module this
session.

**Constraint-conflict simulation (item 6), realistic, not a mock**:
tests use a `_StaleCheckRepository` wrapper whose `get_by_canonical_key`
always returns `None` (simulating a concurrent insert that slipped in
between another process's check and its write) around the REAL
repository — so the actual T025 `UniqueConstraint` is what raises
`IntegrityError`, not a fabricated exception. Proves the SAVEPOINT
recovery works against the genuine DB mechanism, not an assumption
about it.

**Tests placed in `tests/integration/`, not `tests/unit/`** — the
first deviation from this session's pipeline-test placement, deliberate:
T054 explicitly asks for "integration tests" (item 7) distinct from
unit tests, and these specifically exercise a full commit-at-the-end
`session_scope()` lifecycle (re-opening a fresh session after commit
to prove durability), not just mid-transaction state like the
SQLite-substitution unit tests elsewhere.

8 new tests: create, update-vs-skip (both policies), provenance stored
for writes only, the constraint-conflict-marked-FAILED-not-raised
case, the core "failed record doesn't roll back earlier successes"
proof (3-record batch: 2 real successes + 1 simulated conflict in the
middle, re-verified from a fresh post-commit session), and
summary-matches-committed-row-count.

Verified locally: 367 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (79 source files).

## Pipeline metrics (T055) — current task now T060, Phase 5 (Data pipeline) fully complete

`app/pipeline/metrics.py`: Stage 8 ("Metrics") — `compute_job_counters()`
aggregates T051's `ValidationResult`s and T054's `PersistOutcome`s into
`app.domain.jobs.JobCounters` (already existed, T024 — this task fills
it in for real, no schema change needed). `count_job_run_attempts()`
surfaces the "retries" metric from `JobRun.attempt` (T024). New
`JobRepository.update_counters()` (Protocol + SQLAlchemy impl) —
T032/T035 never needed a counters-write path before now.

**Bucket-mapping design decision (docs/08 names the 7 counters but not
how every outcome type maps onto them)**: every `validation_results`
item counts toward `total_units` once; `REJECTED` → `failed_units` +
`records_rejected` (never reaches persistence at all).
`CREATED`/`UPDATED` (T054) → `successful_units` +
`records_created`/`records_updated`. `PersistAction.FAILED` (a DB
constraint conflict) → `failed_units` **only**, deliberately NOT
`records_rejected` — a database write failure and a data-quality
rejection are different kinds of problem, and conflating them would
make `records_rejected` an inaccurate quality signal.
`SKIPPED_EXISTING`/`SKIPPED_DUPLICATE_IN_BATCH` → `skipped_units`. By
construction, `total_units == successful_units + failed_units +
skipped_units` always — verified directly with an invariant test.

**"Retries" is deliberately NOT a new counter or schema field** — this
codebase already has two distinct, already-tracked retry concepts:
`JobRun.attempt` (worker-level re-attempt of the *same* job after a
crash, T024/T062+) and `JobService.retry_job()` (T035 — an entirely
new `Job` row after a terminal FAILED job, tracked via the audit log's
`original_job_id`, not a counter). T055 surfaces the first (the one
directly queryable from what's already built) via
`count_job_run_attempts()`, rather than inventing a third concept or a
migration to link the second.

**Atomicity (T055's literal acceptance criterion: "counters never
claim success for uncommitted records")**: `JobRepository.
update_counters()` is always called from within the *same*
`session_scope()` transaction as `persist_batch()`'s own record
writes — proven directly by an integration test that commits both
together, then re-opens a fresh session afterward and checks the
persisted counters against the actual row count.

**A real mid-session tooling issue, fixed, not a design problem**: the
new `tests/integration/test_pipeline_metrics.py` collided at
collection time with `tests/unit/test_pipeline_metrics.py` — pytest
(no `__init__.py` in either directory, same known constraint noted in
this project since the `workers/queue.py` mypy collision) refuses two
test modules with the identical basename regardless of directory.
Renamed to `tests/integration/test_pipeline_metrics_transaction.py`.
Worth remembering for any future pipeline task that wants both a
`tests/unit/` and a `tests/integration/` file for the same module
name — they can't share a basename.

15 new tests total: 10 pure aggregation tests (`tests/unit/
test_pipeline_metrics.py`, one per T055 scenario — all-success,
partial-failure, retry, duplicate, rejected-record — plus the
`total_units` invariant and a no-negative-counters check) + 1
transactional-atomicity integration test.

Verified locally: 378 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (80 source files).

**Phase 5 (Data pipeline) is now fully complete** — T050 (normalize) →
T051 (validate) → T052 (canonical identity) → T053 (deduplicate) →
T054 (persist) → T055 (metrics). Every stage of
`docs/08_DATA_PIPELINE_DEEP.md` now has a real, tested, provider-
agnostic implementation, composable by whatever orchestrates a real
collection run — which is Phase 6 (Worker, T060+), not yet started.

## Redis queue (T060) — current task now T061, Phase 6 (Worker) started

`workers/queue.py` extended (not a new file — its own T015 docstring
said "this is NOT the job queue abstraction, that's T060", so this
task fills in the same file): `JobQueue` (Protocol, item 1) +
`RedisJobQueue` (real implementation, item 2). Redis is
coordination-only (docs/16_MEMORY.md's queue decision) — the ONLY
payload ever carried is a bare job ID (item 8); every durable job fact
lives in MySQL (`app.repositories.jobs`), which this module never
imports.

**Reliable-queue pattern (items 5-6, acknowledgement + worker
failure)**: `dequeue()` uses `BLMOVE` (Redis's non-deprecated
successor to `BRPOPLPUSH`) to atomically move a job ID from the main
queue list into a separate in-flight list, rather than just popping
it. If the worker that dequeued it crashes before calling
`acknowledge()`, the job ID sits visibly in the in-flight list
(`list_in_flight()`) instead of being silently lost. `requeue()` is
the explicit primitive that moves an abandoned in-flight job back onto
the main queue — deciding *when* to call it automatically (a stale-
heartbeat sweep) is T062/T065's job, not built here.

**T013 (Redis) is still not locally available — resolved with
`fakeredis`, a real decision made and verified before writing any
code, not assumed**: added `fakeredis>=2.20,<3.0` to the dev extras.
Sanity-checked directly (`LPUSH`/`BRPOP`/`SET NX EX`/`BLMOVE` all
behave correctly against a real Redis command implementation, not a
hand-rolled mock) before committing to it — same
"real-substitute-system, not a fake" philosophy as SQLite standing in
for MySQL throughout this whole project. One caveat found and
accepted, not hidden: `fakeredis`'s blocking commands (`BLMOVE`, etc.)
return immediately when the source list is empty rather than actually
waiting out the timeout — fine for this task's tests (which never
depend on real cross-thread blocking timing), but worth knowing if a
future test needs to prove genuine blocking behavior.

**Two real mypy findings from redis-py's type stubs, fixed, not
suppressed blindly**: (1) `blmove`'s `timeout` parameter is typed
`int` even though the real Redis `BLMOVE` command accepts a
fractional-second timeout (confirmed directly against `fakeredis`) —
a `# type: ignore[arg-type]` with an explanatory comment, not a
signature change that would have broken sub-second test timeouts.
(2) The sync `redis.Redis` client's methods are typed as returning
`X | Awaitable[X]` in redis-py's stubs (shared with the async client),
so `int(result)`/iterating a list result needs an explicit `cast()` to
the concrete sync-side type — a known, common redis-py mypy
awkwardness, not a bug in this code.

11 new tests (`tests/unit/test_queue.py`), one section per T060 item,
against `fakeredis`: enqueue, FIFO dequeue ordering, empty-queue
`None`, acknowledgement removing from in-flight, a safe-no-op
double-acknowledge, the "job stays visible in-flight until acked"
worker-failure proof, requeue redelivering (and not duplicating an
already-acknowledged job), payload-is-always-a-bare-int, and a
Redis-total-data-loss test proving nothing MySQL-durable is touched
(this module simply has no way to reach MySQL, the strongest possible
version of that proof).

Verified locally: 389 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (80 source files in
`apps/api`; 6 source files via the separate `workers/pyproject.toml`
mypy invocation documented in `workers/README.md`).

**Phase 6 (Worker) has started.** T061+ (job execution, heartbeat,
recovery, retry) will build the actual worker main-loop that calls
`RedisJobQueue` + the full Phase 5 pipeline (T050-T055) + the provider
adapter (T040-T045) together for the first time.

## Worker job execution (T061) — current task now T062, "first major vertical slice" done

`workers/jobs/execute_collection.py` (new subpackage,
`docs/25_WORKER_FILE_PLAN.md`): `process_next_job()` — composes every
piece built T038-T060 into the full dequeue-to-acknowledge workflow
for exactly one job. Uses only the generic `ProviderAdapter` interface
(T040) — zero Google-specific imports anywhere, so the exact same
function runs against `FakeProviderAdapter` (this task's own
acceptance test) or `GoogleMapsProvider` (T041-T045) interchangeably.
`field_rules`/`provider_operation` are caller-supplied for exactly
this reason (Google's own values live in
`app.providers.google_maps.mapper`, not here).

**Three new `JobRepository` methods, all genuinely required by T061's
own items, not scope creep**:

-   `claim_queued_job(job_id, *, started_at)` (item 2) — a REAL
    conditional `UPDATE jobs SET status='running' WHERE id=? AND
    status='queued'` (SQLAlchemy Core `update()`, not the ORM
    get-then-mutate pattern `update_status()` uses). This is the first
    genuinely atomic-under-concurrency write in the whole job-status
    codepath — `update_status()`'s read-then-write has no protection
    against two workers both observing `status=queued` before either
    commits. The `WHERE` clause hardcodes exactly the one transition
    this method performs, so it's exactly as safe as
    `app.domain.job_state_machine.transition()` for this specific
    case while also being atomic. Returns `None` (not an error) if
    another worker already claimed it.
-   `finalize_job(job_id, *, status, finished_at, error_code=None,
    error_message=None)` (items 14-15 combined in one write — a
    status can never show `FAILED` with no error detail yet, or vice
    versa, if the process died mid-way).
-   `finish_run(run_id, *, status, finished_at)` (item 16, "stop
    heartbeat" — a bookend touch of `heartbeat_at`, not continuous
    polling; that's T062's job, not built here since T061 doesn't
    depend on T062).

**Job-level status decision, a design decision this task had to
make**: `total_units == 0` or `failed_units == 0` → `COMPLETED`;
`failed_units > 0` and `successful_units == 0` → `FAILED` (nothing
survived); otherwise → `PARTIALLY_COMPLETED` — matching
`docs/08_DATA_PIPELINE_DEEP.md`'s own worked example exactly ("300
successful, 150 skipped, 50 failed → partially_completed"). Per-record
failure reasons stay on the individual `ValidationResult`/
`PersistOutcome` objects; `Job.error_code`/`error_message` is reserved
for a *whole-job* failure (config missing, config invalid, `collect()`
itself raised) where one `ProviderError` genuinely describes
everything — never condensed from many per-record failures.

**Real bug found and fixed while writing the test helper, not the
production code**: a test setup helper used `config_json or
{"query": "coffee shops"}` to substitute a default when no override
was given — but an explicitly-passed empty dict `{}` (needed for the
"invalid configuration" test) is falsy in Python, so `or` silently
replaced it with the valid default, making that test assert against
the wrong scenario entirely (it initially failed with `COMPLETED`
instead of the expected `FAILED`, which is exactly what caught this).
Fixed with an explicit `is not None` check — the same "`or` for
defaults is unsafe when a legitimate falsy value is a valid
argument" class of bug worth remembering generally.

**A second real mypy finding, fixed with a targeted cast, not
suppressed**: `Session.execute(update(...))`'s return type
(`Result[Any]`) doesn't statically expose `.rowcount` — cast to
`sqlalchemy.CursorResult` (what it actually is at runtime for a Core
DML statement) rather than adding a blanket `type: ignore`. Caught by
the *separate* `workers/pyproject.toml`-scoped mypy invocation before
the `apps/api`-scoped one flagged it too — both configs check
`app/repositories/jobs.py` (via `mypy_path`), and this time both
agreed once fixed.

Extended `tests/unit/factories.make_config()` with an optional
`config_json` parameter (backward-compatible — no prior caller existed
outside this file, verified before changing it) so tests could supply
a specific (valid or deliberately invalid) provider config.

8 new tests (`tests/integration/test_execute_collection.py`,
transactional-lifecycle placement matching T054/T055's precedent, with
`fakeredis`-backed `RedisJobQueue`, T060): the literal T061 acceptance
criterion (3 fake records → `COMPLETED` job + 3 `Record` rows, re-
verified from a fresh post-commit session), empty-queue no-op,
already-claimed-job skip-and-still-acknowledge (the race-handling
proof), invalid-config fails without ever calling `collect()`, a
`collect()`-level exception classified and recorded via the
provider's own `classify_error()`, partial failure →
`PARTIALLY_COMPLETED`, the `JobRun` created/finalized correctly, and
the queue message always acknowledged even on total failure.

Verified locally: 397 passed, 1 skipped (T012-gated), ruff clean
across all three Python trees, mypy clean (80 source files in
`apps/api`; 8 source files via the separate `workers/pyproject.toml`
mypy invocation).

**"The first major vertical slice" is done** — every layer built this
session (auth/authz, provider, data pipeline, queue) is now proven to
work together end-to-end for one real job, not just in isolated unit
tests. T062 (heartbeat), T063 (retry), T064 (?), T065 (recovery) will
build the operational robustness around this core loop — real
continuous heartbeat polling, stale-run detection, and wiring this
into `worker_main.py`'s actual `while True` loop (not done in T061 —
`process_next_job()` is a single-call primitive, deliberately not a
running loop, so it stays independently testable).

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

**T060 added `fakeredis` as a dev-only test substitute** (same role
SQLite plays for MySQL) so Redis-dependent code (the job queue) could
be built and genuinely tested without a live Redis — this does NOT
resolve T013 itself, which is specifically about the real local Redis
instance being reachable; `fakeredis` only unblocks writing/testing
code that talks to *a* Redis-compatible server, not verifying the
actual configured `REDIS_URL` works.

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

## Record database (T025)

Turned out T025's actual acceptance criteria (insert works, duplicate
constraint rejected, tests pass) were just as dialect-agnostic as
T022-T024's — the earlier flag that this "likely" needed real MySQL
was too cautious; always check the literal prompt before assuming.

`app/db/models/record.py`: `Record` (`canonical_key` unique
**per-project**, not globally — matches the T000 decision; explicit
docstring warning against deriving it from name alone, per T025's own
instruction) and `RecordProvenance`. Dedup-scope proven directly: a
test creates the *same* `canonical_key` in two different projects and
asserts both rows persist (allowed), alongside the existing
duplicate-within-one-project rejection test.

**Found a real gap, not a cross-dialect bug this time**: `tests/` had
never actually been linted — every `ruff format`/`ruff check` command
this project has run was scoped to `apps/api/` only (`.` from within
that directory), so the whole test suite silently accumulated 17 lint
issues (unsorted imports, nested `with` statements, one blind
`except Exception`, a few long lines) across 6 files before anyone
looked. Fixed all of them and **extended `.github/workflows/ci.yml`'s
backend job** to run `ruff format --check` / `ruff check` over `.
../../tests ../../workers` (not just `.`) — verified this correctly
picks up `apps/api/pyproject.toml`'s config for `tests/` (which has no
config of its own) while `workers/` still uses its own closer
`workers/pyproject.toml`, by running the exact CI command locally.
**`mypy` deliberately stays scoped to `apps/api` only** — `tests/`
hits the same module-name-collision issue `workers/queue.py` did
(`conftest.py` exists in both `tests/unit/` and `tests/integration/`),
and mypy-checking test files isn't standard practice anyway; not
treated as a gap needing a fix, unlike the ruff scope was.

Migration `589cf4259331_...` autogenerated. 6 new tests: insert,
FK rejection, duplicate-canonical-key-per-project rejection, the
cross-project dedup-scope proof, provenance-belongs-to-record, and
provenance FK rejection. Plus a migration-level table test.

Verified locally: 47 passed, 1 skipped (T012-gated), ruff clean across
`apps/api` + `tests` + `workers`, mypy clean for `apps/api`.

## Operations database (T026)

`app/db/models/export.py` (`Export`/`ExportStatus` — deliberately no
`job_id` anywhere, it's its own unit of work, not a side effect
logged onto a job), `app/db/models/schedule.py` (`Schedule` — the
scheduler service, T083, creates jobs from these; doesn't execute
providers directly), `app/db/models/audit_log.py` (`AuditLog` —
`user_id` nullable for system-initiated actions, `entity_id` nullable
+ deliberately NOT a foreign key since it's polymorphic across entity
types identified by `entity_type`).

All three tables/indexes match `docs/04_DATABASE_DESIGN.md` exactly.
Migration `bafe7b89931a_...` autogenerated. 6 new tests covering
export independence-from-jobs, full export lifecycle
(pending→running→completed with `file_path`/`completed_at` set),
schedule enable/disable, audit log actor+action+entity identification,
and system-initiated audit entries with no user.

Verified locally: 53 passed, 1 skipped (T012-gated), ruff clean across
all three Python trees, mypy clean for `apps/api`.

**All 8 database-schema tasks (T020-T026 + T027 next) are now either
done or the final one.** Every table in `docs/04_DATABASE_DESIGN.md`
now exists. T027 is index/constraint review against real query plans
— re-read its exact prompt, but this one really does need MySQL, not
a "check first, might be fine" situation like T025/T026 turned out to
be.

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
