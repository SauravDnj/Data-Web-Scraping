# T027 --- Database indexes and constraints

## Task purpose

Review query patterns and add only justified indexes/constraints.

## Dependencies

T026

## Full Claude Code implementation prompt

You are implementing T027 --- Database Index Review.

READ: - docs/04_DATABASE_DEEP.md - docs/05_API_DEEP.md

OBJECTIVE: Ensure the schema supports expected queries without
indiscriminate indexing.

IMPLEMENT: 1. List all common queries from requirements. 2. Map each
query to indexes. 3. Add project/status indexes. 4. Add job lifecycle
indexes. 5. Add record project/time/canonical indexes. 6. Add export and
schedule indexes. 7. Review foreign-key indexes. 8. Review uniqueness
constraints. 9. Use EXPLAIN on representative synthetic queries. 10.
Document why each non-obvious index exists.

DO NOT: - create an index for every column; - optimize without query
evidence.

ACCEPTANCE: - critical queries use expected indexes; - no obviously
redundant indexes; - migration is tested.

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
