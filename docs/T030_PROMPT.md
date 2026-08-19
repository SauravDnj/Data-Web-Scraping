# T030 --- Domain models

## Task purpose

Create database-independent domain models and value objects.

## Dependencies

T023,T024,T025,T026

## Full Claude Code implementation prompt

You are implementing T030 --- Domain Models.

READ: - docs/02_SYSTEM_ARCHITECTURE_DEEP.md -
docs/03_PRODUCT_REQUIREMENTS_DEEP.md

OBJECTIVE: Separate business concepts from SQLAlchemy persistence
models.

IMPLEMENT: 1. Define Project domain object. 2. Define CollectionConfig.
3. Define Job. 4. Define JobRun. 5. Define Record. 6. Define Export. 7.
Define Schedule. 8. Define domain enums/status values. 9. Define
validation/value objects where useful. 10. Keep domain models
independent of HTTP and SQLAlchemy.

ACCEPTANCE: - domain logic can be unit-tested without MySQL; - status
values are centralized; - provider-specific details are not embedded in
generic domain objects.

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
