# T077 --- Schedule UI

## Task purpose

Build schedule creation and management screens.

## Dependencies

T026,T083

## Full Claude Code implementation prompt

You are implementing T077 --- Schedule UI.

OBJECTIVE: Allow controlled recurring jobs.

IMPLEMENT: 1. Schedule list. 2. Create schedule. 3. Edit schedule. 4.
Enable/disable. 5. Timezone selection. 6. Next-run preview. 7. Usage
warning. 8. Confirmation. 9. Error states.

Do not directly trigger provider calls from the UI.

ACCEPTANCE: Schedule changes are persisted and next-run information
comes from backend.

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
