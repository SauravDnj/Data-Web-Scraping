# T051 --- Validation pipeline

## Task purpose

Validate record quality and produce structured warnings/rejections.

## Dependencies

T050

## Full Claude Code implementation prompt

You are implementing T051 --- Validation Pipeline.

OBJECTIVE: Create a field-level data quality system.

IMPLEMENT: 1. Define valid/warning/rejected states. 2. Validate types.
3. Validate ranges. 4. Validate required fields. 5. Validate coordinate
ranges where applicable. 6. Validate URL syntax where applicable. 7.
Produce field-level error objects. 8. Preserve the original job context.
9. Test valid, warning, and rejected records.

ACCEPTANCE: Validation is deterministic and does not make network calls.

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
