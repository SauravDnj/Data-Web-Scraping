# T065 --- Worker recovery

## Task purpose

Recover jobs after worker crashes.

## Dependencies

T062,T063,T064

## Full Claude Code implementation prompt

You are implementing T065 --- Worker Recovery.

OBJECTIVE: Recover stale jobs without duplicate corruption.

IMPLEMENT: 1. Detect stale job runs. 2. Decide whether the job is
retryable. 3. Increment attempt safely. 4. Requeue eligible jobs. 5.
Mark exhausted jobs failed. 6. Ensure only one active execution owner
exists. 7. Test simulated worker crash. 8. Test duplicate queue
delivery. 9. Test recovery after heartbeat loss.

ACCEPTANCE: A worker crash results in either safe retry or clear
failure, never silent completion.

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
