# T082 --- Excel export

## Task purpose

Add Excel export after stable CSV/JSON.

## Dependencies

T080,T081

## Full Claude Code implementation prompt

You are implementing T082 --- Excel Export.

OBJECTIVE: Provide practical spreadsheet output without making Excel the
internal data model.

IMPLEMENT: 1. Use approved spreadsheet library. 2. Export authorized
records. 3. Add readable headers. 4. Keep formatting simple. 5. Handle
large but reasonable datasets. 6. Track export status. 7. Add tests. 8.
Document limitations.

ACCEPTANCE: Generated workbook opens successfully and matches requested
data.

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
