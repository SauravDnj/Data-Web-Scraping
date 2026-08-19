# T062 --- Worker heartbeat

## Task purpose

Implement active-job heartbeat and stale detection.

## Dependencies

T061,T024

## Full Claude Code implementation prompt

You are implementing T062 --- Worker Heartbeat.

OBJECTIVE: Make worker liveness observable and recoverable.

IMPLEMENT: 1. Update heartbeat during execution. 2. Define heartbeat
interval. 3. Define stale threshold. 4. Detect stale job runs. 5.
Prevent healthy workers from being marked stale. 6. Add tests with
controlled time. 7. Ensure heartbeat failures are logged and handled.

ACCEPTANCE: A stopped worker becomes detectable as stale without
incorrectly recovering healthy jobs.

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
