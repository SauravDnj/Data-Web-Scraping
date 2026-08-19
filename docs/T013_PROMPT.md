# T013 --- Redis local setup

## Task purpose

Prepare Redis for queue coordination and verify connectivity.

## Dependencies

T000

## Full Claude Code implementation prompt

You are implementing T013 --- Redis Local Setup.

READ: - docs/09_JOB_QUEUE_WORKER_DEEP.md - docs/10_LOCAL_SETUP.md -
docs/26_ENVIRONMENT_AND_CONFIG.md

OBJECTIVE: Prepare Redis as a queue/coordination dependency.

IMPLEMENT: 1. Verify supported Redis installation. 2. Document
start/stop commands. 3. Configure REDIS_URL. 4. Create a minimal
connection check. 5. Confirm Redis is treated as temporary coordination,
not the system of record. 6. Do not implement the job queue yet.

ACCEPTANCE: - Redis responds; - connection check passes; - configuration
does not contain credentials in source.

TEST: Run ping/connectivity test.

UPDATE tracking files.

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
