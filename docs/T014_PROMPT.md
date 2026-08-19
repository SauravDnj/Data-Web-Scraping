# T014 --- FastAPI skeleton

## Task purpose

Create the backend application, settings, logging, health, and readiness
endpoints.

## Dependencies

T010,T012,T013

## Full Claude Code implementation prompt

You are implementing T014 --- FastAPI Skeleton.

READ: - docs/02_SYSTEM_ARCHITECTURE_DEEP.md - docs/05_API_DEEP.md -
docs/26_ENVIRONMENT_AND_CONFIG.md - docs/27_OBSERVABILITY_OPERATIONS.md

OBJECTIVE: Create a clean backend application that can start reliably
before business logic exists.

IMPLEMENT: 1. Create app/main.py. 2. Create settings/config module. 3.
Create dependency injection foundation. 4. Configure structured logging.
5. Create GET /health. 6. Create GET /ready. 7. Add /api/v1 routing
container. 8. Configure CORS only for known development frontend origin.
9. Add request ID middleware or equivalent. 10. Add exception handling
foundation. 11. Add startup/shutdown lifecycle. 12. Keep database and
Redis readiness checks separate and understandable.

DO NOT: - add provider calls; - add authentication business logic yet; -
put SQL in route handlers.

ACCEPTANCE: - /health returns process health; - /ready reports
dependency health; - startup logs are structured; - tests cover healthy
and dependency-failure readiness.

TEST: Run API tests and manually verify endpoints.

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
