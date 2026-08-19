# T035 --- Job service

## Task purpose

Implement job creation and lifecycle commands.

## Dependencies

T031,T032,T034

## Full Claude Code implementation prompt

You are implementing T035 --- Job Service.

READ: - docs/05_API_DEEP.md - docs/09_JOB_QUEUE_WORKER_DEEP.md

OBJECTIVE: Implement the control-plane operations for jobs.

IMPLEMENT: 1. Create job from an active validated configuration. 2.
Enforce project authorization. 3. Create queued state. 4. Support
cancel. 5. Support pause/resume according to state machine. 6. Support
retry only when error class allows it. 7. Add idempotency key support.
8. Create audit events. 9. Return job DTOs. 10. Do not call provider
from this service.

ACCEPTANCE: - job creation is transactional; - duplicate idempotency
request does not create duplicate jobs; - invalid lifecycle actions are
rejected.

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
