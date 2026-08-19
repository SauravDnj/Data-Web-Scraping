# T040 --- Provider interface

## Task purpose

Create the generic provider contract.

## Dependencies

T030,T034

## Full Claude Code implementation prompt

You are implementing T040 --- Provider Interface.

READ: - docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md -
docs/02_SYSTEM_ARCHITECTURE_DEEP.md

OBJECTIVE: Create a provider boundary that the application can depend on
without knowing Google SDK details.

IMPLEMENT: 1. Define ProviderAdapter protocol/interface. 2. Define
configuration validation result. 3. Define usage estimate result. 4.
Define collection result/iterator. 5. Define provider error abstraction.
6. Define normalized provider item contract. 7. Define health/diagnostic
contract. 8. Add a fake provider implementation for tests. 9. Add
interface contract tests.

DO NOT: - mention browser automation in generic interface; - call
Google.

ACCEPTANCE: Fake provider can satisfy the interface and run through
tests.

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
