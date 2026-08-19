# T031 --- Job state machine

## Task purpose

Implement explicit legal job state transitions.

## Dependencies

T030,T024

## Full Claude Code implementation prompt

You are implementing T031 --- Job State Machine.

READ: - docs/09_JOB_QUEUE_WORKER_DEEP.md - docs/04_DATABASE_DEEP.md

OBJECTIVE: Prevent invalid job state transitions.

IMPLEMENT: 1. Define every allowed status. 2. Define every legal
transition. 3. Implement transition function. 4. Reject invalid
transitions with a typed domain error. 5. Add tests for every allowed
transition. 6. Add tests for representative invalid transitions. 7.
Ensure database/service code uses this state machine rather than
arbitrary status assignment.

ACCEPTANCE: - completed cannot become running; - failed cannot silently
become completed; - pause/resume rules are explicit; - tests cover
transition matrix.

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
