# T026 --- Operations database

## Task purpose

Create exports, schedules, and audit log tables.

## Dependencies

T025

## Full Claude Code implementation prompt

You are implementing T026 --- Operations Database.

READ: - docs/03_PRODUCT_REQUIREMENTS_DEEP.md -
docs/27_OBSERVABILITY_OPERATIONS.md - docs/10_SECURITY_DEEP.md

OBJECTIVE: Persist operational actions and future jobs.

IMPLEMENT: 1. Create exports table. 2. Create schedules table. 3. Create
audit_logs table. 4. Add ownership/project relationships. 5. Add export
status fields. 6. Add schedule timezone and next-run fields. 7. Add
audit actor/action/entity/details. 8. Create indexes. 9. Create
migration. 10. Add tests.

ACCEPTANCE: - exports can be tracked independently; - schedules can be
enabled/disabled; - audit records identify actor/action/entity.

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
