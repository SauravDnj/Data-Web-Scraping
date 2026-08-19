# T032 --- Repository layer

## Task purpose

Create repository interfaces and MySQL implementations.

## Dependencies

T020,T023,T024,T025,T026,T030

## Full Claude Code implementation prompt

You are implementing T032 --- Repository Layer.

READ: - docs/02_SYSTEM_ARCHITECTURE_DEEP.md - docs/04_DATABASE_DEEP.md

OBJECTIVE: Centralize persistence access.

IMPLEMENT: 1. Create repository interfaces/protocols. 2. Implement
project repository. 3. Implement configuration repository. 4. Implement
job repository. 5. Implement record repository. 6. Implement export
repository. 7. Implement schedule repository. 8. Implement audit
repository. 9. Add transaction-aware methods. 10. Add pagination query
support. 11. Add tests.

DO NOT: - place provider calls in repositories; - put business policy
into SQL query functions.

ACCEPTANCE: Services can use repositories without knowing SQLAlchemy
implementation details.

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
