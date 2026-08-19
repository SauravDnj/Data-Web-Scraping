# T024 --- Job database

## Task purpose

Create jobs and job_runs with metrics and lifecycle fields.

## Dependencies

T023

## Full Claude Code implementation prompt

You are implementing T024 --- Job Database.

READ: - docs/09_JOB_QUEUE_WORKER_DEEP.md - docs/04_DATABASE_DEEP.md

OBJECTIVE: Create durable job state and execution history.

IMPLEMENT: 1. Create jobs table. 2. Add project/config foreign keys. 3.
Add status. 4. Add requested/started/finished timestamps. 5. Add
work-unit counters. 6. Add created/updated/rejected counters. 7. Add
error code/message. 8. Create job_runs table. 9. Add worker ID, attempt,
heartbeat. 10. Add indexes for queued/running jobs. 11. Add migration
and tests.

ACCEPTANCE: - job can reference exact configuration version; - job run
records an execution attempt; - counters have safe defaults; -
timestamps support lifecycle tracking.

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
