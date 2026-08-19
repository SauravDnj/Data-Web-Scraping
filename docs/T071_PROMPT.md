# T071 --- Dashboard UI

## Task purpose

Build operational dashboard with API-backed metrics.

## Dependencies

T070,T035,T036

## Full Claude Code implementation prompt

You are implementing T071 --- Dashboard UI.

OBJECTIVE: Give the user an immediate operational overview.

IMPLEMENT: 1. Active jobs card. 2. Completed jobs card. 3. Failed jobs
card. 4. Records count. 5. Recent jobs list. 6. Recent failures. 7.
Loading states. 8. Empty states. 9. Error states. 10. Retry action where
appropriate.

Use backend metrics as authoritative data.

DO NOT: - calculate authoritative record counts from partial frontend
data.

ACCEPTANCE: Dashboard works with empty DB and populated test fixtures.

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
