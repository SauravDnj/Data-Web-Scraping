# T083 --- Scheduler service

## Task purpose

Implement backend scheduling that creates jobs rather than executing
providers directly.

## Dependencies

T035,T026

## Full Claude Code implementation prompt

You are implementing T083 --- Scheduler Service.

OBJECTIVE: Turn enabled schedules into jobs.

IMPLEMENT: 1. Store schedule. 2. Calculate next run in configured
timezone. 3. Find due schedules. 4. Create job from current active
configuration. 5. Prevent duplicate job creation for same scheduled
occurrence. 6. Update last/next run. 7. Audit schedule execution. 8.
Respect project status. 9. Respect usage budgets.

ACCEPTANCE: A due schedule creates exactly one job for an occurrence.

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
