# T034 --- Configuration service

## Task purpose

Implement versioned provider configuration and validation workflow.

## Dependencies

T033,T032,T040

## Full Claude Code implementation prompt

You are implementing T034 --- Configuration Service.

READ: - docs/03_PRODUCT_REQUIREMENTS_DEEP.md -
docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md

OBJECTIVE: Create immutable configuration versions and a validation
pipeline.

IMPLEMENT: 1. Create configuration version. 2. Increment version
deterministically. 3. Mark only one version active. 4. Validate generic
fields. 5. Delegate provider-specific validation to provider adapter. 6.
Store validation result. 7. Prevent historical config mutation. 8. Add
tests for versioning and activation. 9. Add authorization checks.

ACCEPTANCE: - job references a stable config version; - changing active
config does not rewrite old job configuration; - invalid configuration
cannot become active.

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
