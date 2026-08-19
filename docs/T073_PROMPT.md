# T073 --- Configuration wizard

## Task purpose

Build the multi-step collection configuration workflow.

## Dependencies

T034,T041,T072

## Full Claude Code implementation prompt

You are implementing T073 --- Configuration Wizard.

OBJECTIVE: Make collection configuration safe and understandable.

STEPS: 1. Project basics. 2. Provider. 3. Search/query/location. 4.
Fields. 5. Limits. 6. Schedule option. 7. Review. 8. Confirm.

IMPLEMENT: 1. Client-side validation for immediate feedback. 2.
Server-side validation remains authoritative. 3. Show provider-specific
help. 4. Show usage/limit warnings. 5. Show exact review summary before
submission. 6. Prevent invalid submission. 7. Handle validation response
from API. 8. Save as versioned configuration. 9. Do not store provider
secrets in browser state longer than necessary. 10. Add tests.

ACCEPTANCE: Invalid configuration cannot be activated; review screen
accurately represents submitted data.

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
