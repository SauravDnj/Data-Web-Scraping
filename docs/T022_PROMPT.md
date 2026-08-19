# T022 --- Identity database

## Task purpose

Create users/authentication persistence tables and migrations.

## Dependencies

T021

## Full Claude Code implementation prompt

You are implementing T022 --- Identity Database.

READ: - docs/04_DATABASE_DEEP.md - docs/10_SECURITY_DEEP.md -
docs/05_API_DEEP.md

OBJECTIVE: Create the minimum durable identity model for V1.

IMPLEMENT: 1. Create users table. 2. Add unique normalized email. 3. Add
status. 4. Add timestamps. 5. Add password hash field only if the
selected V1 auth strategy uses passwords. 6. Never store plaintext
passwords. 7. Create migration. 8. Add model/repository tests. 9. Add
uniqueness tests. 10. Keep authentication service logic out of the
model.

ACCEPTANCE: - migration succeeds; - duplicate email is rejected; -
password hash is never plaintext; - tests pass.

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
