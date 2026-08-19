# T015 --- Worker skeleton

## Task purpose

Create the worker process with configuration and graceful lifecycle
handling.

## Dependencies

T010,T013

## Full Claude Code implementation prompt

You are implementing T015 --- Worker Skeleton.

READ: - docs/09_JOB_QUEUE_WORKER_DEEP.md - docs/25_WORKER_FILE_PLAN.md -
docs/27_OBSERVABILITY_OPERATIONS.md

OBJECTIVE: Create the worker process without implementing collection
execution.

IMPLEMENT: 1. Create worker entry point. 2. Load environment
configuration. 3. Initialize structured logging. 4. Connect to Redis. 5.
Implement startup checks. 6. Implement graceful shutdown. 7. Handle
SIGINT/SIGTERM appropriately for the platform. 8. Add worker ID
generation/configuration. 9. Add a placeholder queue loop that does not
process real jobs. 10. Add smoke tests.

DO NOT: - implement provider calls; - modify job state; - add scraping.

ACCEPTANCE: - worker starts; - worker connects to Redis; - worker shuts
down cleanly; - no orphaned process remains after normal shutdown.

Update tracking files.

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
