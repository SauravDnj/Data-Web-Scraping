# T044 --- Provider error mapping

## Task purpose

Classify provider failures and determine retryability.

## Dependencies

T042

## Full Claude Code implementation prompt

You are implementing T044 --- Provider Error Mapping.

READ: - docs/09_JOB_QUEUE_WORKER_DEEP.md -
docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md

OBJECTIVE: Turn provider-specific errors into stable application error
categories.

IMPLEMENT: 1. Map authentication errors. 2. Map invalid requests. 3. Map
quota/usage errors. 4. Map rate errors. 5. Map transient network/service
errors. 6. Map permanent errors. 7. Preserve safe diagnostic context. 8.
Mark retryability explicitly. 9. Add tests for every mapping.

DO NOT: - retry policy/authorization failures automatically; - hide
provider errors as generic internal errors.

ACCEPTANCE: Worker can make a deterministic retry/no-retry decision from
the classified error.

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
