# T002 --- CI baseline

## Task purpose

Create automated checks for formatting, linting, typing, and tests.

## Dependencies

T001

## Full Claude Code implementation prompt

You are implementing T002 --- CI Baseline.

READ: - docs/00_MASTER_README.md - docs/02_SYSTEM_ARCHITECTURE_DEEP.md -
docs/11_TESTING_DEEP.md - docs/16_MEMORY.md

OBJECTIVE: Create a minimal CI pipeline that prevents obviously broken
code from being merged.

IMPLEMENT: 1. Configure CI for the repository's supported runtime. 2.
Install backend dependencies. 3. Run Python formatter check. 4. Run
Python lint. 5. Run Python type check if configured. 6. Run Python
tests. 7. Install frontend dependencies. 8. Run frontend lint. 9. Run
frontend type check. 10. Run frontend tests if present. 11. Make CI fail
on any required check failure. 12. Cache dependencies only when it is
reliable.

DO NOT: - deploy; - connect to production databases; - call live Google
APIs; - store credentials in CI.

ACCEPTANCE: - CI starts from a clean checkout. - CI is deterministic. -
A deliberately failing test causes failure. - A passing repository
produces a green build.

TEST LOCALLY: Run every CI command locally before declaring complete.

UPDATE: progress, memory, completed work, current work, pending work.

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
