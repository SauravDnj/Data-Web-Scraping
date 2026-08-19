# Google Maps Data Platform --- Master Build Guide

## What this system is

This project is a local-first data collection platform. Its primary
business workflow is:

> User defines a Google Maps Platform collection job → system validates
> it → job is queued → worker executes the permitted provider operation
> → returned data is normalized and validated → records are deduplicated
> → MySQL stores the application's data → dashboard shows
> progress/results → user exports permitted data.

The application is NOT just a scraper script. It is a complete
job-management/data-platform product.

## What the application must eventually provide

1.  Project management.
2.  Provider configuration.
3.  Collection job creation.
4.  Job queue and worker execution.
5.  Progress tracking.
6.  Error classification and retries.
7.  Data normalization.
8.  Deduplication.
9.  MySQL persistence.
10. Record search/filtering.
11. CSV/JSON/Excel exports where allowed.
12. Scheduling.
13. Audit history.
14. Security and access control.
15. Provider usage/quota controls.
16. Tests and operational documentation.

## Core stack

  Layer                Technology
  -------------------- ------------------------------------------
  UI                   Next.js + TypeScript
  API                  Python + FastAPI
  Domain               Python services
  ORM                  SQLAlchemy
  Migration            Alembic
  Database             MySQL 8.x
  Queue                Redis
  Worker               Python worker
  Data processing      Python + Pandas where useful
  Browser automation   Playwright only for permitted use cases
  HTML parsing         BeautifulSoup/lxml for permitted sources
  Tests                Pytest + frontend test framework
  Version control      Git

## Important boundary

Google Maps Platform has its own product terms, API documentation, data
storage/use restrictions, quotas, and pricing. The implementation must
use the documented/approved Google product/API workflow selected for the
project.

Do not implement systems whose purpose is to defeat CAPTCHA, anti-bot
protections, authentication barriers, rate limits, or other access
controls. Do not collect private/restricted data.

## Development philosophy

Build in vertical slices:

``` text
foundation
  ↓
database
  ↓
backend
  ↓
provider adapter
  ↓
worker
  ↓
data pipeline
  ↓
frontend
  ↓
exports/scheduling
  ↓
security/testing
  ↓
release
```

Every phase must leave the application in a runnable state.

## Claude Code operating model

Claude Code should receive one task prompt at a time. Each prompt tells
Claude:

-   what documents to read;
-   what files to inspect;
-   what to implement;
-   what not to implement;
-   acceptance criteria;
-   tests;
-   documentation updates.

Do not ask Claude to "build the whole project" in one request.

## Source of truth hierarchy

1.  Current task prompt.
2.  Architecture Decision Records.
3.  System architecture/design.
4.  Requirements.
5.  Database/API/UI specifications.
6.  Existing code.
7.  Future roadmap.

If code conflicts with architecture, stop and resolve the conflict. Do
not silently create a second architecture.

## Completion rule

A task is complete only when:

-   implementation exists;
-   acceptance criteria are met;
-   relevant tests pass;
-   no known blocker remains;
-   documentation is updated;
-   Git diff has been reviewed.
