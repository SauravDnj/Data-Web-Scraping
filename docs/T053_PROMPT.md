# T053 --- Deduplication

## Task purpose

Implement batch and database deduplication.

## Dependencies

T052,T032

## Full Claude Code implementation prompt

You are implementing T053 --- Deduplication.

OBJECTIVE: Prevent duplicate records without incorrectly merging
distinct entities.

IMPLEMENT: 1. Deduplicate within a provider response batch. 2.
Deduplicate across pages. 3. Compare against existing project records.
4. Use canonical identity. 5. Define update-vs-skip behavior. 6. Track
duplicate counts. 7. Add false-merge tests. 8. Add duplicate-batch
tests. 9. Add database constraint tests.

ACCEPTANCE: Repeated collection does not create uncontrolled duplicate
rows.

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
