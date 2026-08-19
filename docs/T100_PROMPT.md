# T100 --- Database backup

## Task purpose

Create and test MySQL backup/restore procedure.

## Dependencies

T094

## Full Claude Code implementation prompt

You are implementing T100 --- Database Backup.

OBJECTIVE: Prove that the database can be recovered.

IMPLEMENT: 1. Document backup command. 2. Create backup of synthetic
development data. 3. Create clean restore database. 4. Restore backup.
5. Verify row counts and critical relationships. 6. Document restore
command. 7. Document retention recommendation. 8. Never commit backup
files containing data.

ACCEPTANCE: Backup and restore are both executed successfully and
documented.

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
