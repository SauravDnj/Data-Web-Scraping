# T025 --- Record database

## Task purpose

Create records and provenance tables with deduplication support.

## Dependencies

T024

## Full Claude Code implementation prompt

You are implementing T025 --- Record Database.

READ: - docs/04_DATABASE_DEEP.md - docs/08_DATA_PIPELINE_DEEP.md

OBJECTIVE: Create durable record storage with provenance.

IMPLEMENT: 1. Create records table. 2. Add project/job/provider fields.
3. Add provider_record_id nullable. 4. Add canonical_key. 5. Add data
JSON. 6. Add collected_at and timestamps. 7. Create record_provenance
table. 8. Add indexes for project/canonical key and collection time. 9.
Define an appropriate uniqueness strategy. 10. Add migration. 11. Add
tests for insert and duplicate constraints.

Do not assume name alone is a unique business identifier.

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
