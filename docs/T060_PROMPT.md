# T060 --- Redis queue

## Task purpose

Implement queue abstraction and Redis-backed job transport.

## Dependencies

T015,T035

## Full Claude Code implementation prompt

You are implementing T060 --- Redis Queue.

READ: - docs/09_JOB_QUEUE_WORKER_DEEP.md

OBJECTIVE: Queue job IDs without moving system-of-record state into
Redis.

IMPLEMENT: 1. Define queue interface. 2. Implement Redis queue. 3.
Enqueue job ID. 4. Dequeue job ID. 5. Handle acknowledgement. 6. Handle
worker failure. 7. Add queue tests. 8. Keep queue payload minimal. 9.
Ensure job details remain in MySQL.

ACCEPTANCE: A queued job can be delivered to a worker; Redis loss does
not erase the durable job record.

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
