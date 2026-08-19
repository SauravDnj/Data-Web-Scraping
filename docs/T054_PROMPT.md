# T054 --- Transactional persistence

## Task purpose

Persist normalized records atomically and accurately update metrics.

## Dependencies

T053,T025

## Full Claude Code implementation prompt

You are implementing T054 --- Transactional Persistence.

OBJECTIVE: Make database writes reliable.

IMPLEMENT: 1. Insert new records. 2. Update existing records according
to policy. 3. Store provenance. 4. Roll back failed transactions. 5.
Increment created/updated/rejected counters only after successful
operations. 6. Handle database constraint conflicts. 7. Add integration
tests. 8. Test rollback behavior.

ACCEPTANCE: A failed transaction does not leave partial inconsistent
state.

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
