# Claude Code Task Prompts

## How to use this file

Give Claude Code one task at a time. Before implementation, ask it to
inspect the repository and relevant docs. Do not allow it to invent
architecture that contradicts the source-of-truth documents.

After each task, run tests and update the project tracking files.

------------------------------------------------------------------------

## T000 --- Repository bootstrap

### Prompt

You are working on the Google Maps Data Platform project.

Read: - docs/00_README.md - docs/01_SYSTEM_DESIGN.md -
docs/02_SYSTEM_ARCHITECTURE.md - docs/03_REQUIREMENTS.md -
docs/11_TASKS.md - docs/14_WORKING_FILES.md - docs/15_MEMORY.md

Create the repository skeleton only. Do not implement business logic
yet.

Requirements: 1. Create the documented folder structure. 2. Add
README.md. 3. Add .gitignore suitable for Python, Node, MySQL local
development, IDE files, logs, exports, and secrets. 4. Add .env.example
with placeholders only. 5. Add basic project metadata. 6. Do not commit
real credentials. 7. Do not change the architecture without documenting
the change first.

At the end: - list created files; - run basic structural checks; -
update docs/13_COMPLETED_WORK.md; - update docs/14_WORKING_FILES.md; -
update docs/15_MEMORY.md; - update docs/16_PENDING_WORK.md.

Do not mark unrelated tasks complete.

------------------------------------------------------------------------

## T010--T019 --- Local foundation

### Prompt

Implement the local development foundation described in
docs/10_LOCAL_SETUP.md.

Requirements: - verify the required runtime versions; - create the
Python virtual environment instructions; - bootstrap FastAPI; -
bootstrap Next.js; - add health/readiness endpoints; - add structured
logging; - add formatting/linting configuration; - keep frontend and
backend independently runnable.

Do not add scraping logic yet.

Acceptance: - backend starts; - frontend starts; - health endpoint
returns success; - readiness fails clearly when required dependencies
are unavailable; - tests pass.

Update tracking files.

------------------------------------------------------------------------

## T020--T033 --- MySQL schema

### Prompt

Implement the database described in docs/04_DATABASE_DESIGN.md.

Requirements: - SQLAlchemy models; - Alembic; - migrations for all
required tables; - foreign keys; - indexes; - timestamps; - JSON
fields; - deterministic naming conventions; - repository tests.

Test from an empty database and from a migrated database.

Do not put provider-specific business logic into SQLAlchemy models.

Update tracking files only for work actually completed.

------------------------------------------------------------------------

## T040--T050 --- Backend domain

### Prompt

Implement the backend domain layer.

Read docs/03_REQUIREMENTS.md and docs/05_API_DESIGN.md.

Build: - project service; - collection configuration service; - job
service; - record service; - audit service; - job state machine; -
repositories; - REST routers; - authentication and authorization
boundaries.

Rules: - routers stay thin; - business rules live in services/domain
code; - database access lives in repositories; - provider calls are
forbidden in route handlers; - return consistent API error envelopes; -
add unit and integration tests.

Do not implement provider collection yet.

------------------------------------------------------------------------

## T060--T066 --- Google provider adapter

### Prompt

Implement the Google provider adapter according to
docs/07_DATA_PIPELINE.md and docs/08_SECURITY_COMPLIANCE.md.

Important: - use only documented/approved Google Maps Platform/API
operations selected for the product; - do not implement CAPTCHA
solving; - do not implement anti-bot bypass; - do not implement stealth
fingerprinting; - do not implement proxy rotation to evade
restrictions; - do not collect private/restricted information.

Build: - provider configuration validation; - provider client
abstraction; - request/response mapping; - internal normalized record
model; - quota/error classification; - provider health diagnostics; -
mock-based contract tests.

Keep provider-specific code isolated.

Before coding, identify any data field whose storage/export may have
provider restrictions and document the decision.

------------------------------------------------------------------------

## T070--T078 --- Worker system

### Prompt

Implement Redis-backed background jobs.

Requirements: - queue interface; - worker process; - job execution; -
heartbeat; - cancellation; - bounded retries; - failure
classification; - metrics; - safe logging; - idempotent persistence.

A worker crash must leave the job recoverable and must not silently mark
it completed.

Add tests for: - success; - transient failure; - permanent failure; -
cancellation; - duplicate execution.

------------------------------------------------------------------------

## T080--T085 --- Data pipeline

### Prompt

Implement normalization, validation, canonicalization, deduplication,
and persistence.

Requirements: - pure functions where possible; - deterministic
transformations; - no silent data loss; - quality status; - structured
rejection reasons; - database uniqueness where appropriate; -
false-merge tests.

Do not use name-only deduplication.

------------------------------------------------------------------------

## T090--T102 --- Frontend

### Prompt

Implement the Next.js dashboard from docs/06_UI_DESIGN.md.

Build: - app shell; - dashboard; - projects; - project configuration; -
jobs; - job detail; - records; - record detail; - exports; -
schedules; - settings.

Every screen must include loading, empty, error, and success states.

Use typed API clients. Do not duplicate backend business rules in the
frontend.

Do not expose provider credentials.

Add component and end-to-end tests for the primary workflow.

------------------------------------------------------------------------

## T110--T115 --- Export and scheduling

### Prompt

Implement CSV and JSON exports first, then Excel if dependencies are
already approved.

Implement scheduling only after job execution is stable.

Requirements: - export authorization; - server-side filtering; - safe
filenames; - bounded export size; - export status; - schedule timezone
handling; - usage-budget checks.

Do not create schedules that blindly execute when the provider budget or
configuration does not allow it.

------------------------------------------------------------------------

## T120--T136 --- Hardening/release

### Prompt

Perform a V1 production-readiness pass.

Inspect: - authentication; - authorization; - secrets; - database
migrations; - indexes; - worker recovery; - retry behavior; - export
security; - logs; - dependency versions; - tests; - documentation.

Fix defects rather than merely documenting them.

Run all test suites.

Create: - deployment guide; - backup/restore procedure; - monitoring
guide; - release checklist; - known limitations.

Only mark V1 complete when all acceptance criteria in
docs/03_REQUIREMENTS.md are satisfied.
