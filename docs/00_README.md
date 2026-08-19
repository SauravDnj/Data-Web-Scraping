# Google Maps Data Platform --- Build Documentation Pack

## Purpose

This documentation pack is the source of truth for building a
local-first data collection platform whose primary use case is Google
Maps/Google Maps Platform data collection, with a future path to other
web data sources.

The build is intentionally staged. The first version should be small,
testable, and maintainable rather than attempting to implement every
scraping framework at once.

## Core technology direction

-   Frontend: Next.js + TypeScript
-   Backend: Python + FastAPI
-   Database: MySQL
-   ORM/migrations: SQLAlchemy + Alembic
-   Background jobs: Redis + worker layer
-   Browser automation where permitted/needed: Playwright
-   HTML parsing for permitted sources: BeautifulSoup + lxml
-   Data processing: Pandas
-   API/data-source integration: provider adapter layer
-   Testing: Pytest + frontend test tooling
-   Local development: no Docker required for V1
-   Version control: Git

## Important Google Maps boundary

This project must not be designed around bypassing CAPTCHAs, anti-bot
controls, authentication barriers, rate limits, or other technical
access controls. Do not implement stealth/evasion systems.

Google Maps Platform data must be collected and stored/used according to
the current Google Maps Platform terms, applicable API documentation,
licensing rules, privacy obligations, and any other applicable law. If a
desired field or workflow is not permitted through the selected Google
product/API, the product must not quietly substitute an unauthorized
collection method.

## Documentation workflow

1.  Read `01_SYSTEM_DESIGN.md`.
2.  Read `02_SYSTEM_ARCHITECTURE.md`.
3.  Read `03_REQUIREMENTS.md`.
4.  Read `04_DATABASE_DESIGN.md`.
5.  Read `05_API_DESIGN.md`.
6.  Read `06_UI_DESIGN.md`.
7.  Read `07_DATA_PIPELINE.md`.
8.  Read `08_SECURITY_COMPLIANCE.md`.
9.  Use `TASKS.md` as the execution backlog.
10. Use `TASK_PROMPTS.md` to give implementation work to Claude Code.
11. Keep `PROGRESS.md`, `MEMORY.md`, `COMPLETED_WORK.md`,
    `PENDING_WORK.md`, and `CURRENT_WORK.md` updated after every
    meaningful milestone.
12. Do not skip tests to move faster.

## V1 definition

V1 is complete when a user can:

-   create a collection project;
-   configure a permitted Google Maps Platform data workflow;
-   validate configuration;
-   create and run a job;
-   observe job status and logs;
-   normalize and deduplicate returned records;
-   store permitted records in MySQL;
-   search/filter records;
-   export permitted data;
-   retry recoverable failures;
-   view a basic audit trail.

V1 is not required to include every scraper framework, AI extraction,
multi-tenant billing, distributed deployment, or advanced automation.

## Source of truth rule

When code and documentation disagree, stop and reconcile them. Do not
silently continue with two competing designs.
