# T020 --- SQLAlchemy foundation

## Task purpose

Create database engine, sessions, base model, and conventions.

## Dependencies

T012,T010

## Full Claude Code implementation prompt

You are implementing T020 --- SQLAlchemy Foundation.

READ: - docs/04_DATABASE_DEEP.md - docs/24_BACKEND_FILE_PLAN.md -
docs/22_SECURITY_RULES.md

OBJECTIVE: Create safe, testable SQLAlchemy infrastructure.

IMPLEMENT: 1. Create database engine factory. 2. Configure connection
pooling appropriately for local development. 3. Create session factory.
4. Create declarative base. 5. Establish naming conventions for
constraints/indexes. 6. Add transaction helper/dependency. 7. Ensure
request-scoped sessions are closed. 8. Add test database configuration.
9. Add connection error handling. 10. Keep database credentials in
environment configuration.

DO NOT: - create all business models in one task; - add provider code.

ACCEPTANCE: - API can acquire and close a DB session; - test can create
a temporary schema; - connection errors are understandable.

TEST: Repository/database integration tests.

Update tracking files.

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
