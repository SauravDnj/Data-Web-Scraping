# T061 --- Worker job execution

## Task purpose

Implement end-to-end worker orchestration using the fake provider first.

## Dependencies

T060,T035,T040,T050,T054

## Full Claude Code implementation prompt

You are implementing T061 --- Worker Job Execution.

OBJECTIVE: Build the complete worker workflow using the fake provider
before enabling live provider execution.

IMPLEMENT: 1. Dequeue job ID. 2. Atomically claim queued job. 3. Create
job_run. 4. Update status to running. 5. Start heartbeat. 6. Load exact
configuration version. 7. Validate configuration. 8. Call provider
adapter. 9. Normalize items. 10. Validate items. 11. Deduplicate. 12.
Persist transactionally. 13. Update metrics. 14. Finalize status. 15.
Record errors. 16. Stop heartbeat. 17. Acknowledge queue message.

ACCEPTANCE: Fake provider with 3 records produces a completed job and 3
records in MySQL.

This is the first major vertical slice.

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
