# T045 --- Provider contract tests

## Task purpose

Create a complete fake-provider contract suite.

## Dependencies

T040,T041,T042,T043,T044

## Full Claude Code implementation prompt

You are implementing T045 --- Provider Contract Tests.

OBJECTIVE: Make provider integration testable without live external
requests.

IMPLEMENT: 1. Create synthetic provider fixtures. 2. Test valid
collection response. 3. Test empty response. 4. Test malformed response.
5. Test pagination fixture. 6. Test quota error. 7. Test authentication
error. 8. Test transient error. 9. Test normalization. 10. Test
provenance. 11. Test deterministic mapping.

ACCEPTANCE: Provider adapter behavior is covered without requiring live
Google credentials.

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
