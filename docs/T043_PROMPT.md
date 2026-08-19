# T043 --- Google response mapper

## Task purpose

Map Google provider responses into internal records and provenance.

## Dependencies

T042,T025

## Full Claude Code implementation prompt

You are implementing T043 --- Google Response Mapper.

READ: - docs/08_DATA_PIPELINE_DEEP.md - docs/04_DATABASE_DEEP.md -
docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md

OBJECTIVE: Convert provider-specific responses into the platform's
normalized internal record representation.

IMPLEMENT: 1. Map each supported field explicitly. 2. Preserve provider
identifier when permitted. 3. Preserve provider/source reference when
permitted. 4. Normalize types. 5. Handle missing fields. 6. Never invent
fields. 7. Attach collection timestamp. 8. Attach project/job context.
9. Write fixture-based tests. 10. Test malformed responses.

ACCEPTANCE: Same fixture always produces deterministic internal records.

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
