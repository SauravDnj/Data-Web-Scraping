# T023 --- Project database

## Task purpose

Create projects and configuration-version persistence.

## Dependencies

T022,T021

## Full Claude Code implementation prompt

You are implementing T023 --- Project Database.

READ: - docs/03_PRODUCT_REQUIREMENTS_DEEP.md -
docs/04_DATABASE_DEEP.md - docs/05_API_DEEP.md

OBJECTIVE: Create project persistence and immutable configuration
versioning.

IMPLEMENT: 1. Create projects table. 2. Add owner/user foreign key. 3.
Add project status. 4. Create collection_configs table. 5. Store
provider and config JSON. 6. Add configuration version. 7. Add active
flag. 8. Ensure historical versions are not mutated. 9. Add foreign keys
and indexes. 10. Create migration. 11. Write repository tests.

ACCEPTANCE: - project belongs to user; - configuration belongs to
project; - historical configuration can be retained; - active version
can be selected deterministically.

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
