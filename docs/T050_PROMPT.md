# T050 --- Normalization pipeline

## Task purpose

Implement deterministic record normalization.

## Dependencies

T030,T043

## Full Claude Code implementation prompt

You are implementing T050 --- Normalization Pipeline.

READ: - docs/08_DATA_PIPELINE_DEEP.md

OBJECTIVE: Create pure, deterministic transformations from provider
output to normalized records.

IMPLEMENT: 1. Trim whitespace. 2. Normalize Unicode only where safe. 3.
Normalize URLs. 4. Normalize numeric fields. 5. Normalize timestamps. 6.
Normalize categories. 7. Preserve source semantics. 8. Do not silently
replace missing values with invented defaults. 9. Create unit tests for
each transformation. 10. Create regression fixtures.

ACCEPTANCE: Given the same input, output is identical.

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
