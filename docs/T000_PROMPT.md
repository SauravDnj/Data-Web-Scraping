# T000 --- Repository bootstrap

## Task purpose

Create the repository skeleton and initial documentation controls.

## Dependencies

None

## Full Claude Code implementation prompt

You are implementing T000 --- Repository Bootstrap for the Google Maps
Data Platform.

READ FIRST: - docs/00_MASTER_README.md - docs/01_SYSTEM_EXPLANATION.md -
docs/02_SYSTEM_ARCHITECTURE_DEEP.md - docs/12_TASKS_MASTER_DETAILED.md -
docs/15_PROGRESS.md - docs/16_MEMORY.md - docs/17_CURRENT_WORK.md

OBJECTIVE: Create only the initial repository foundation. Do not
implement application business logic.

IMPLEMENT: 1. Inspect the existing directory and Git status before
changing anything. 2. Create the agreed repository layout: apps/web,
apps/api, workers, tests, database, scripts, docs. 3. Create root
README.md explaining the product at a high level. 4. Create .gitignore
covering Python, Node, IDE files, .env files, logs, local databases,
build output, and generated exports. 5. Create .env.example containing
placeholders only. 6. Create basic package/project metadata. 7. Create a
minimal development command guide. 8. Do not create provider
credentials. 9. Do not add scraping implementation. 10. Do not add
database schema yet.

ARCHITECTURE RULES: - Do not change the architecture because a shortcut
is convenient. - Keep frontend, backend, worker, and database
responsibilities separated. - Never commit secrets. - Do not add
anti-bot or access-control bypass tooling.

VALIDATION: - Repository tree matches the architecture. - Git status
contains only intentional files. - No secret-like values exist. - README
can explain how the project will be built.

TESTS: Run repository structure checks and any configured lint/format
checks.

DONE WHEN: All files exist, no business logic has been added, checks
pass, and the tracking documents are updated with evidence.

UPDATE: docs/18_COMPLETED_WORK.md docs/20_WORKING_FILES.md
docs/16_MEMORY.md docs/19_PENDING_WORK.md docs/15_PROGRESS.md
docs/17_CURRENT_WORK.md

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
