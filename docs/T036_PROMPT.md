# T036 --- Record service

## Task purpose

Implement server-side record search, filtering, and detail retrieval.

## Dependencies

T032,T030

## Full Claude Code implementation prompt

You are implementing T036 --- Record Service.

READ: - docs/05_API_DEEP.md - docs/06_UI_DEEP.md -
docs/08_DATA_PIPELINE_DEEP.md

OBJECTIVE: Provide scalable record access.

IMPLEMENT: 1. Project-scoped record listing. 2. Cursor or safe
pagination. 3. Sorting. 4. Date filtering. 5. Provider filtering. 6.
Quality filtering. 7. Record detail. 8. Authorization checks. 9. Query
limits. 10. Tests with synthetic large datasets.

DO NOT: - load all records into memory; - authorize only in the
frontend.

ACCEPTANCE: - user can retrieve page-sized records; - unauthorized
project records are inaccessible; - filters are translated into
server-side queries.

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
