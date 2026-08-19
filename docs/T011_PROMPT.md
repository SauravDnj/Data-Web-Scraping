# T011 --- Next.js environment

## Task purpose

Bootstrap the frontend application with strict TypeScript and shared
configuration.

## Dependencies

T000,T001

## Full Claude Code implementation prompt

You are implementing T011 --- Next.js Environment.

READ: - docs/06_UI_DEEP.md - docs/23_UI_FILE_PLAN.md -
docs/26_ENVIRONMENT_AND_CONFIG.md

OBJECTIVE: Create the frontend foundation without implementing business
screens.

IMPLEMENT: 1. Create Next.js + TypeScript under apps/web. 2. Enable
strict TypeScript. 3. Configure linting. 4. Create the root layout. 5.
Create a minimal landing/dashboard placeholder. 6. Configure API base
URL through a safe client configuration. 7. Separate server-only
configuration from browser-exposed variables. 8. Add a reusable error
boundary/error UI strategy. 9. Add a loading UI strategy. 10. Add a test
setup.

DO NOT: - expose provider credentials; - connect directly to MySQL; -
implement collection logic.

ACCEPTANCE: - npm install succeeds; - development server starts; -
production build succeeds; - TypeScript check passes.

TEST: Run lint, type check, unit/component test setup, and build.

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
