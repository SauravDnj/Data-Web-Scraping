# Google Maps Data Platform

A local-first data collection platform for Google Maps Platform data. This is a
full job-management data product, not a scraper script:

> A user defines a Google Maps Platform collection job → the system validates
> it → the job is queued → a worker executes the permitted provider operation
> → returned data is normalized, validated, and deduplicated → MySQL stores
> the data → a dashboard shows progress and results → the user exports
> permitted data.

Full specification, architecture, database/API/UI design, and the task-by-task
build plan live in [`docs/`](docs/00_MASTER_README.md). Start there. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`docs/CODING_STANDARDS.md`](docs/CODING_STANDARDS.md) before making changes.

## Repository layout

```text
apps/
  web/       Next.js + TypeScript frontend
  api/       FastAPI backend (control plane: auth, validation, job creation, record query)
workers/     Python worker process (queue consumer, provider orchestration, pipeline)
database/    Migrations and seed data (Alembic)
tests/       Unit, integration, and end-to-end tests
scripts/     Local development and operational scripts
docs/        Specification, architecture, and task documentation (source of truth)
```

## Core stack

| Layer              | Technology                     |
| ------------------ | ------------------------------- |
| UI                  | Next.js + TypeScript            |
| API                 | Python + FastAPI                |
| ORM / migrations    | SQLAlchemy + Alembic            |
| Database            | MySQL 8.x                       |
| Queue               | Redis                           |
| Worker              | Python                          |
| Data processing     | Python + Pandas                 |
| Browser automation  | Playwright (only where permitted) |
| Tests               | Pytest + frontend test framework |

## Important boundary

This project only uses the documented, approved Google Maps Platform API
workflow. It does not implement CAPTCHA solving, anti-bot/stealth evasion,
authentication bypass, rate-limit circumvention, or collection of
private/restricted data. See `docs/08_SECURITY_COMPLIANCE.md` and
`docs/22_SECURITY_RULES.md`.

## Status

Pre-implementation. No application code has been written yet. Work proceeds
task-by-task per `docs/00_TASK_INDEX.md` (T000–T103). See
`docs/17_CURRENT_WORK.md` for the current task.

## Development

- Backend (Python): see [`apps/api/README.md`](apps/api/README.md) (T010).
- Frontend (Next.js), MySQL, Redis, worker: established in tasks
  T011–T015; see `docs/10_LOCAL_SETUP.md` for the full local
  environment guide. Until those tasks land, only the backend has
  install/run commands.
