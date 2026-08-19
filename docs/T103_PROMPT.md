# T103 --- V1 release

## Task purpose

Prepare the first stable release.

## Dependencies

T102

## Full Claude Code implementation prompt

You are implementing T103 --- V1 Release.

OBJECTIVE: Create the first stable, reproducible release.

IMPLEMENT: 1. Ensure Git working tree is clean except intentional
release metadata. 2. Update changelog. 3. Record version. 4. Record
known limitations. 5. Record provider configuration assumptions. 6.
Verify migrations. 7. Verify tests. 8. Verify setup documentation. 9.
Create release tag only after approval. 10. Create rollback notes.

ACCEPTANCE: Another developer can check out the release and reproduce
the documented environment.

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
