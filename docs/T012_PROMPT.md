# T012 --- MySQL local setup

## Task purpose

Create the local database and least-privilege application account.

## Dependencies

T000

## Full Claude Code implementation prompt

You are implementing T012 --- MySQL Local Setup.

READ: - docs/04_DATABASE_DEEP.md - docs/10_LOCAL_SETUP.md -
docs/26_ENVIRONMENT_AND_CONFIG.md - docs/22_SECURITY_RULES.md

OBJECTIVE: Prepare a clean local MySQL environment for development.

IMPLEMENT: 1. Verify supported MySQL version. 2. Create development
database. 3. Create dedicated application user. 4. Grant only required
development permissions. 5. Do not use root in application
configuration. 6. Document commands for creating and resetting the
database. 7. Document how to verify connectivity. 8. Add no real
passwords to Git. 9. Add database connection configuration to
.env.example only as placeholders.

ACCEPTANCE: - dedicated user connects; - application can connect using
the dedicated user; - root is not required by application code; - setup
is reproducible.

TEST: Connect using the application account and execute a harmless test
query.

UPDATE tracking files.

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
