# Master Task Plan --- Detailed

## PHASE 0 --- Governance

### T000 Repository and documentation foundation

Create the repository, docs folder, Git ignore rules, environment
template, and project instructions.

Depends on: none.

Output: - clean repository; - documentation source of truth; - task
tracking.

### T001 Coding standards

Define Python, TypeScript, SQL, Git, naming, logging, error-handling,
and testing conventions.

### T002 CI baseline

Run formatting, linting, type checks, backend tests, frontend tests.

------------------------------------------------------------------------

## PHASE 1 --- Local Development

### T010 Python environment

Create virtual environment and dependency management.

### T011 Node environment

Create Next.js application.

### T012 MySQL

Create development DB and application user.

### T013 Redis

Install and verify Redis.

### T014 FastAPI skeleton

Create API application with configuration and health endpoints.

### T015 Worker skeleton

Create worker entry point with graceful shutdown.

------------------------------------------------------------------------

## PHASE 2 --- Database

### T020 SQLAlchemy setup

Create base, engine, sessions.

### T021 Alembic

Create migrations.

### T022 Identity tables

Users/auth data.

### T023 Project tables

Projects and configs.

### T024 Job tables

Jobs and runs.

### T025 Record tables

Records and provenance.

### T026 Operations tables

Exports, schedules, audit logs.

### T027 Index review

Add and verify indexes.

------------------------------------------------------------------------

## PHASE 3 --- Backend

### T030 Domain models

Define stable internal models.

### T031 Job state machine

Define legal transitions.

### T032 Repositories

Persistence abstractions.

### T033 Project service

Project CRUD/business rules.

### T034 Configuration service

Configuration versioning and validation.

### T035 Job service

Job creation/cancel/pause/resume/retry.

### T036 Record service

Search/filter/detail.

### T037 Audit service

Audit events.

### T038 Authentication

Secure login/session strategy.

### T039 Authorization

Project-level authorization.

------------------------------------------------------------------------

## PHASE 4 --- Provider

### T040 Provider interface

Generic provider contract.

### T041 Google configuration

Provider-specific configuration validation.

### T042 Google client

Implement documented provider API client.

### T043 Response mapper

Map provider responses to internal records.

### T044 Provider error mapper

Map quota/rate/auth/request errors.

### T045 Provider tests

Mock provider responses.

------------------------------------------------------------------------

## PHASE 5 --- Data Pipeline

### T050 normalization

Normalize fields.

### T051 validation

Quality rules.

### T052 canonical identity

Stable record identity.

### T053 deduplication

Batch + database deduplication.

### T054 persistence

Transactional upsert.

### T055 metrics

Accurate counters.

------------------------------------------------------------------------

## PHASE 6 --- Worker

### T060 Redis queue

Queue interface.

### T061 job execution

Worker orchestration.

### T062 heartbeat

Stale detection.

### T063 retry

Bounded retries.

### T064 cancellation

Cooperative cancellation.

### T065 recovery

Worker crash recovery.

------------------------------------------------------------------------

## PHASE 7 --- Frontend

### T070 app shell

Navigation/layout.

### T071 dashboard

KPIs and recent activity.

### T072 projects

Project list/create/edit.

### T073 configuration wizard

Provider/query/fields/limits/review.

### T074 jobs

List/status/actions.

### T075 records

Table/filter/detail.

### T076 exports

Create/view/download.

### T077 schedules

Schedule management.

### T078 settings

Account/provider settings.

------------------------------------------------------------------------

## PHASE 8 --- Operations

### T080 CSV

Server-side export.

### T081 JSON

Server-side export.

### T082 Excel

Optional after CSV/JSON.

### T083 scheduler

Create future jobs.

### T084 usage budget

Prevent accidental overuse.

### T085 observability

Logs/metrics/diagnostics.

------------------------------------------------------------------------

## PHASE 9 --- Quality

### T090 security review

Auth, authz, secrets.

### T091 reliability review

Worker failures/retries.

### T092 performance review

Indexes/query plans.

### T093 E2E

Full fake-provider workflow.

### T094 documentation

Setup/operations/release.

------------------------------------------------------------------------

## PHASE 10 --- Release

### T100 backup

MySQL backup/restore.

### T101 deployment

Production deployment documentation.

### T102 release gate

All V1 acceptance criteria.

### T103 V1 release

Tag and changelog.
