# T074 --- Job UI

## Task purpose

Build job list/detail/progress/action screens.

## Dependencies

T035,T061,T071

## Full Claude Code implementation prompt

You are implementing T074 --- Job UI.

OBJECTIVE: Make long-running work transparent.

IMPLEMENT: 1. Job list with status. 2. Job detail. 3. Progress bar. 4.
Metrics. 5. timestamps/duration. 6. error details. 7. log view. 8.
pause/resume/cancel buttons according to state. 9. retry button only
when backend says retryable. 10. polling or event refresh strategy. 11.
Loading/error states.

Do not trust frontend state to authorize actions.

ACCEPTANCE: UI accurately reflects backend state transitions and cannot
present invalid actions as executable.

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
