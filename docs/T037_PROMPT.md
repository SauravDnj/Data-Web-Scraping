# T037 --- Audit service

## Task purpose

Implement structured audit events.

## Dependencies

T032,T030

## Full Claude Code implementation prompt

You are implementing T037 --- Audit Service.

READ: - docs/10_SECURITY_DEEP.md - docs/27_OBSERVABILITY_OPERATIONS.md

OBJECTIVE: Record important security and operational actions.

IMPLEMENT: 1. Define action names. 2. Record actor. 3. Record entity
type/id. 4. Store structured details without secrets. 5. Create audit
repository/service. 6. Add audit calls for project/config/job/export
actions. 7. Add tests ensuring sensitive values are redacted.

ACCEPTANCE: - audit events are queryable; - secrets never enter audit
details; - events identify actor and entity.

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
