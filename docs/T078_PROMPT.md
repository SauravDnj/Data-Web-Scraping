# T078 --- Settings UI

## Task purpose

Build account/provider/application settings.

## Dependencies

T038,T041,T070

## Full Claude Code implementation prompt

You are implementing T078 --- Settings UI.

OBJECTIVE: Provide safe settings management.

IMPLEMENT: 1. Account settings. 2. Provider connection status. 3.
Non-secret provider configuration metadata. 4. Usage limits. 5.
Application preferences. 6. Security/session controls if applicable.

Never display full provider API keys.

ACCEPTANCE: User can verify provider configuration status without
exposing secrets.

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
