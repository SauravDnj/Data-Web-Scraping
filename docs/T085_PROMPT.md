# T085 --- Observability

## Task purpose

Implement logs, metrics, request IDs, and diagnostics.

## Dependencies

T014,T061,T065

## Full Claude Code implementation prompt

You are implementing T085 --- Observability.

OBJECTIVE: Make failures diagnosable.

IMPLEMENT: 1. Structured API logs. 2. Worker logs. 3. Request IDs. 4.
Job IDs. 5. Provider operation IDs where safe. 6. Metrics for job
duration and outcomes. 7. Queue depth metric. 8. Error counters. 9.
Secret redaction. 10. Health/readiness diagnostics.

ACCEPTANCE: A failed test job can be diagnosed from job ID + structured
logs without reading raw source code.

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
