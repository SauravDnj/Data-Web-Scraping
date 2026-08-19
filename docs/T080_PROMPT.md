# T080 --- CSV export

## Task purpose

Implement authorized server-side CSV generation.

## Dependencies

T036,T026,T076

## Full Claude Code implementation prompt

You are implementing T080 --- CSV Export.

OBJECTIVE: Generate reliable CSV exports from authorized server-side
queries.

IMPLEMENT: 1. Validate project authorization. 2. Validate filters. 3.
Validate columns. 4. Stream/batch query where appropriate. 5. Escape CSV
safely. 6. Generate safe filename. 7. Enforce maximum export size. 8.
Track export status. 9. Record audit event. 10. Test special characters
and large synthetic data.

ACCEPTANCE: CSV opens correctly and contains exactly the requested
authorized records.

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
