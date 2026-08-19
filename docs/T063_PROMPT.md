# T063 --- Retry system

## Task purpose

Implement bounded, classified retry behavior.

## Dependencies

T044,T061

## Full Claude Code implementation prompt

You are implementing T063 --- Retry System.

OBJECTIVE: Retry only errors that are explicitly retryable.

IMPLEMENT: 1. Define maximum attempts. 2. Define exponential backoff. 3.
Add jitter if useful. 4. Classify errors before retry. 5. Persist
attempt count. 6. Requeue retryable jobs. 7. Mark permanent failures. 8.
Prevent retry storms. 9. Test every error class.

DO NOT: - retry provider policy/authorization failures automatically; -
retry indefinitely; - bypass quotas.

ACCEPTANCE: Retryable failures recover within configured limits;
permanent failures stop.

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
