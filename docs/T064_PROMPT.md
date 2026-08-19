# T064 --- Cancellation

## Task purpose

Implement cooperative job cancellation.

## Dependencies

T035,T061

## Full Claude Code implementation prompt

You are implementing T064 --- Cancellation.

OBJECTIVE: Allow users to stop jobs safely.

IMPLEMENT: 1. Add cancellation request state. 2. API records
cancellation request. 3. Worker checks cancellation between safe units.
4. Worker stops provider work at a safe boundary. 5. Finalize job as
cancelled. 6. Prevent cancellation of already completed jobs. 7. Test
cancellation during active processing. 8. Ensure DB transactions finish
cleanly.

ACCEPTANCE: Cancelled jobs do not continue indefinitely and do not leave
the database in an ambiguous state.

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
