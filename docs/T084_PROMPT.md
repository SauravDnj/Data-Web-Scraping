# T084 --- Usage budget

## Task purpose

Implement application-side collection limits and guardrails.

## Dependencies

T041,T083,T035

## Full Claude Code implementation prompt

You are implementing T084 --- Usage Budget.

OBJECTIVE: Prevent accidental large or uncontrolled provider usage.

IMPLEMENT: 1. Define per-job maximum. 2. Define project budget. 3.
Estimate usage where provider supports it. 4. Check budget before
execution. 5. Block or require explicit confirmation according to
product design. 6. Track usage. 7. Handle provider quota responses. 8.
Add tests for under-limit and over-limit cases.

Never attempt to bypass provider quotas.

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
