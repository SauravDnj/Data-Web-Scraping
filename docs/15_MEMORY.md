# Project Memory

This is persistent project context for future coding sessions.

## Product

Local-first data collection platform focused primarily on Google Maps
Platform data workflows.

## Architecture

``` text
Next.js
  -> FastAPI
  -> services/domain
  -> MySQL

FastAPI
  -> Redis
  -> worker
  -> provider adapter
```

## Core principles

1.  Provider isolation.
2.  MySQL is the system of record.
3.  Redis is not the system of record.
4.  Long-running work belongs in workers.
5.  Provider credentials never enter frontend code.
6.  No anti-bot/CAPTCHA/access-control bypass.
7.  Every record needs provenance where permitted.
8.  Every job has explicit state.
9.  Tests are required for completed tasks.
10. Documentation is updated with implementation.

## Technology

-   Next.js
-   TypeScript
-   FastAPI
-   Python
-   SQLAlchemy
-   Alembic
-   MySQL
-   Redis
-   Playwright only where an approved use case requires browser
    automation
-   BeautifulSoup/lxml for permitted HTML sources
-   Pandas for data processing

## Current phase

Phase 0 --- documentation and repository planning.

## Current implementation status

No production code has been implemented yet.

## Decisions

-   Start without Docker.
-   Start with one primary provider integration.
-   Add other scraper engines only after the core workflow is stable.
-   Avoid a generic "scrape everything" abstraction until the first
    provider workflow is working.

## Session handoff rule

At the end of every coding session: 1. update this file; 2. update
progress; 3. update completed work; 4. update pending work; 5. update
working files; 6. record blockers and exact next task.
