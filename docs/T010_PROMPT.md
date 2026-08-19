# T010 --- Python environment

## Task purpose

Set up backend dependency management and runtime configuration.

## Dependencies

T000,T001

## Full Claude Code implementation prompt

You are implementing T010 --- Python Environment.

READ: - docs/10_SECURITY_DEEP.md - docs/24_BACKEND_FILE_PLAN.md -
docs/26_ENVIRONMENT_AND_CONFIG.md

OBJECTIVE: Create a reproducible Python environment for FastAPI,
database access, Redis, testing, and future provider adapters.

IMPLEMENT: 1. Create the backend Python project metadata. 2. Use a
virtual environment workflow suitable for local development. 3. Add
FastAPI. 4. Add an ASGI server. 5. Add SQLAlchemy. 6. Add Alembic. 7.
Add a MySQL driver. 8. Add Redis client support. 9. Add Pytest. 10. Add
formatter/linter/type tooling. 11. Pin or lock versions according to the
project's chosen dependency strategy. 12. Create a documented install
command. 13. Create a minimal Python smoke test. 14. Do not install
every scraping framework at this stage.

DO NOT: - add browser automation unless a later task requires it; - add
Google credentials; - implement scraping.

ACCEPTANCE: - clean environment installs successfully; - Python test
command works; - dependency file is committed; - no secrets are required
for installation.

TEST: Build a clean environment and run the smoke test.

UPDATE tracking files.

## Task completion record

Claude Code must not mark this task complete until: - implementation is
present; - acceptance criteria are verified; - relevant tests pass; -
Git diff is reviewed; - project tracking documents are updated.

## Required tracking updates

-   `docs/15_PROGRESS.md`
-   `docs/16_MEMORY.md`
-   `docs/17_CURRENT_WORK.md`
-   `docs/18_COMPLETED_WORK.md`
-   `docs/19_PENDING_WORK.md`
-   `docs/20_WORKING_FILES.md`
