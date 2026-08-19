# T001 --- Coding standards

## Task purpose

Establish consistent coding, naming, testing, logging, and Git
conventions.

## Dependencies

T000

## Full Claude Code implementation prompt

You are implementing T001 --- Coding Standards.

READ: - docs/00_MASTER_README.md - docs/02_SYSTEM_ARCHITECTURE_DEEP.md -
docs/10_SECURITY_DEEP.md - docs/11_TESTING_DEEP.md - docs/16_MEMORY.md

OBJECTIVE: Create enforceable development conventions before application
code grows.

IMPLEMENT: 1. Define Python formatting and linting. 2. Define Python
type-checking expectations. 3. Define TypeScript strictness and linting.
4. Define React/Next.js component conventions. 5. Define API naming
conventions. 6. Define database naming conventions. 7. Define migration
rules. 8. Define test naming and placement. 9. Define structured logging
conventions. 10. Define Git branch and commit conventions. 11. Define
import ordering and unused-code rules. 12. Define error-handling
conventions. 13. Define rules for provider adapters. 14. Define rules
for secrets and environment variables.

CREATE OR UPDATE: - coding standards documentation; - tool configuration
where practical; - contributor/agent instructions.

DO NOT: - refactor nonexistent application code; - add unnecessary
dependencies; - create provider logic.

ACCEPTANCE: - A developer can determine how to format, lint, test, name,
and commit code. - Tooling is runnable locally. - Rules do not conflict
with architecture.

TEST: Run formatter/linter/type checks on the current minimal
repository.

UPDATE tracking files with exact evidence.

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
