# T092 --- Performance review

## Task purpose

Measure query and job performance using realistic synthetic data.

## Dependencies

T027,T036,T080,T081

## Full Claude Code implementation prompt

You are implementing T092 --- Performance Review.

OBJECTIVE: Find actual bottlenecks before optimizing.

IMPLEMENT: 1. Generate synthetic dataset representative of expected
size. 2. Profile record listing. 3. Profile job queries. 4. Profile
exports. 5. Check N+1 queries. 6. Run EXPLAIN for critical SQL. 7.
Review indexes. 8. Measure API latency. 9. Measure worker throughput
with fake provider. 10. Fix only measured bottlenecks.

ACCEPTANCE: Critical paths have documented baseline and no obvious
unbounded query behavior.

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
