# T081 --- JSON export

## Task purpose

Implement authorized JSON export.

## Dependencies

T036,T026,T076

## Full Claude Code implementation prompt

You are implementing T081 --- JSON Export.

OBJECTIVE: Generate deterministic JSON exports.

IMPLEMENT: 1. Authorize project. 2. Validate filters/columns. 3.
Serialize normalized records. 4. Preserve types where appropriate. 5.
Enforce export size. 6. Track status. 7. Audit event. 8. Test Unicode,
nulls, numbers, nested JSON fields.

ACCEPTANCE: Export matches selected filters and is valid JSON.

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
