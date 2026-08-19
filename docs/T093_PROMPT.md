# T093 --- End-to-end test

## Task purpose

Prove the complete product workflow using a fake provider.

## Dependencies

T070,T073,T074,T075,T076,T061

## Full Claude Code implementation prompt

You are implementing T093 --- End-to-End Test.

OBJECTIVE: Prove the full architecture before relying on a live
provider.

SCENARIO: 1. Authenticate. 2. Create project. 3. Create configuration.
4. Validate configuration. 5. Create job. 6. Queue job. 7. Worker claims
job. 8. Fake provider returns records. 9. Normalize. 10. Validate. 11.
Deduplicate. 12. Persist. 13. Complete job. 14. Display records. 15.
Export records. 16. Verify audit event.

Also test partial failure.

ACCEPTANCE: The entire workflow passes from UI/API through MySQL without
a live external provider.

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
