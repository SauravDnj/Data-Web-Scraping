# T091 --- Reliability review

## Task purpose

Test worker crash, duplicate delivery, provider failure, DB failure, and
cancellation.

## Dependencies

T061,T062,T063,T064,T065

## Full Claude Code implementation prompt

You are implementing T091 --- Reliability Review.

OBJECTIVE: Prove that jobs remain understandable under failure.

SIMULATE: 1. Worker process crash. 2. Duplicate queue delivery. 3.
Provider timeout. 4. Provider quota error. 5. Redis unavailable. 6.
MySQL transaction failure. 7. Cancellation during processing. 8. Stale
heartbeat. 9. Retry exhaustion.

VERIFY: - no false completed state; - no uncontrolled duplicates; -
retry limits; - clear failure reason; - recoverability.

Add regression tests for every discovered defect.

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
