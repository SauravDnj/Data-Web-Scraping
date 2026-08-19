# T033 --- Project service

## Task purpose

Implement project business rules and authorization boundaries.

## Dependencies

T030,T032,T022

## Full Claude Code implementation prompt

You are implementing T033 --- Project Service.

READ: - docs/03_PRODUCT_REQUIREMENTS_DEEP.md - docs/05_API_DEEP.md -
docs/10_SECURITY_DEEP.md

OBJECTIVE: Implement project creation, update, archive, and retrieval.

IMPLEMENT: 1. Validate project name. 2. Enforce user ownership. 3.
Create project. 4. Update editable fields. 5. Archive rather than
destructive delete where appropriate. 6. Record audit events for
important changes. 7. Add service-level tests. 8. Keep API transport out
of service code.

ACCEPTANCE: - user cannot access another user's project; - archived
project cannot start new jobs; - audit event exists for project changes.

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
