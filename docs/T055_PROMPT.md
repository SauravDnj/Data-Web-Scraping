# T055 --- Pipeline metrics

## Task purpose

Implement accurate pipeline/job metrics.

## Dependencies

T054,T024

## Full Claude Code implementation prompt

You are implementing T055 --- Pipeline Metrics.

OBJECTIVE: Ensure the dashboard's numbers represent actual processing.

IMPLEMENT: Track: - work units; - successful units; - failed units; -
skipped units; - records created; - records updated; - records
rejected; - retries.

Ensure counters are atomic/transactionally consistent where needed.

Test: - all-success job; - partial failure; - retry; - duplicate; -
rejected record.

ACCEPTANCE: Job status and counters never claim success for uncommitted
records.

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
