# Detailed Claude Code Prompts --- Phase 0 and 1

## T000 --- Repository bootstrap

``` text
You are implementing T000.

Read:
docs/00_MASTER_README.md
docs/01_SYSTEM_EXPLANATION.md
docs/02_SYSTEM_ARCHITECTURE_DEEP.md
docs/12_TASKS_MASTER_DETAILED.md
docs/15_PROGRESS.md
docs/16_MEMORY.md

Goal:
Create the repository foundation only.

Steps:
1. Inspect the current directory.
2. Show the proposed repository tree.
3. Create the repository structure.
4. Create root README.md.
5. Create .gitignore.
6. Create .env.example.
7. Create docs/ if missing.
8. Add basic Git-safe development configuration.
9. Do not implement provider calls.
10. Do not implement database models.
11. Do not implement UI business pages.
12. Run structural checks.

Acceptance:
- repository tree matches architecture;
- no secrets;
- no unrelated dependencies;
- README explains how the project is organized.

After success update:
docs/18_COMPLETED_WORK.md
docs/20_WORKING_FILES.md
docs/16_MEMORY.md
docs/19_PENDING_WORK.md
docs/15_PROGRESS.md
docs/17_CURRENT_WORK.md
```

## T001 --- Coding standards

``` text
Implement T001.

Read the architecture and existing repository.

Create:
- backend Python style rules;
- TypeScript/Next.js style rules;
- SQL conventions;
- testing conventions;
- commit conventions.

Add tooling configuration where practical.

Do not refactor application code yet.

Acceptance:
- lint/format commands are documented;
- team conventions are explicit;
- CI can later consume the same commands.
```

## T002 --- CI baseline

``` text
Implement T002.

Create CI that runs:
- Python lint/format check;
- Python tests;
- TypeScript type check;
- frontend lint/test where configured.

Keep CI deterministic.

Do not add deployment.

Acceptance:
- CI config exists;
- commands work locally;
- failures are clear.
```

## T010 --- Python environment

``` text
Implement T010.

Create backend Python dependency management.

Requirements:
- pinned or lockable dependencies;
- FastAPI;
- SQLAlchemy;
- Alembic;
- MySQL driver;
- Redis client;
- Pytest;
- lint/type tooling.

Do not add scraping packages until their task requires them.

Acceptance:
- clean environment installs;
- FastAPI can start.
```

## T011 --- Next.js

``` text
Implement T011.

Create Next.js + TypeScript application under apps/web.

Requirements:
- strict TypeScript;
- basic layout;
- API base URL configuration;
- no secrets in client-side variables.

Acceptance:
- npm install works;
- development server starts;
- page renders.
```

## T012 --- MySQL

``` text
Implement T012.

Document and verify local MySQL setup.

Create:
- development database;
- application user;
- least-privilege permissions required for development.

Do not use root in application configuration.

Acceptance:
- application user can connect;
- root credentials are not in project files.
```

## T013 --- Redis

``` text
Implement T013.

Verify local Redis.

Create a minimal connectivity test.

Do not implement worker logic yet.

Acceptance:
- Redis responds;
- backend/worker can read configuration.
```

## T014 --- FastAPI skeleton

``` text
Implement T014.

Create:
- app entry point;
- settings;
- logging;
- health endpoint;
- readiness endpoint;
- API version prefix.

Readiness should verify required infrastructure without exposing secrets.

Add tests.

Acceptance:
GET /health succeeds.
GET /ready reports dependency failures clearly.
```

## T015 --- Worker skeleton

``` text
Implement T015.

Create worker entry point with:
- configuration loading;
- Redis connection;
- graceful shutdown;
- structured logging.

Do not execute provider work.

Acceptance:
worker starts and shuts down cleanly.
```
