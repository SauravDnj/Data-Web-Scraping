# T021 --- Alembic foundation

## Task purpose

Configure migrations and verify clean database migration.

## Dependencies

T020

## Full Claude Code implementation prompt

You are implementing T021 --- Alembic Foundation.

READ: - docs/04_DATABASE_DEEP.md - docs/22_SECURITY_RULES.md

OBJECTIVE: Create reliable schema migration infrastructure.

IMPLEMENT: 1. Configure Alembic. 2. Connect Alembic to SQLAlchemy
metadata. 3. Create initial migration workflow. 4. Document
upgrade/downgrade commands. 5. Ensure environment-driven DB URL. 6.
Ensure migration files contain no credentials. 7. Add migration smoke
test from empty database.

DO NOT: - create unrelated schema changes; - manually mutate
production-like schema outside migrations.

ACCEPTANCE: - alembic upgrade head works from empty DB; - migration
state is inspectable; - tests verify migration startup.

Update tracking files.

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
