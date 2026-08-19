# Complete Task-by-Task Build Plan

This pack contains implementation prompts for every planned V1 task.

## T000 — Repository bootstrap
**Depends on:** None
**Goal:** Create the repository skeleton and initial documentation controls.

See `T000_PROMPT.md` for the full Claude Code prompt.

## T001 — Coding standards
**Depends on:** T000
**Goal:** Establish consistent coding, naming, testing, logging, and Git conventions.

See `T001_PROMPT.md` for the full Claude Code prompt.

## T002 — CI baseline
**Depends on:** T001
**Goal:** Create automated checks for formatting, linting, typing, and tests.

See `T002_PROMPT.md` for the full Claude Code prompt.

## T010 — Python environment
**Depends on:** T000,T001
**Goal:** Set up backend dependency management and runtime configuration.

See `T010_PROMPT.md` for the full Claude Code prompt.

## T011 — Next.js environment
**Depends on:** T000,T001
**Goal:** Bootstrap the frontend application with strict TypeScript and shared configuration.

See `T011_PROMPT.md` for the full Claude Code prompt.

## T012 — MySQL local setup
**Depends on:** T000
**Goal:** Create the local database and least-privilege application account.

See `T012_PROMPT.md` for the full Claude Code prompt.

## T013 — Redis local setup
**Depends on:** T000
**Goal:** Prepare Redis for queue coordination and verify connectivity.

See `T013_PROMPT.md` for the full Claude Code prompt.

## T014 — FastAPI skeleton
**Depends on:** T010,T012,T013
**Goal:** Create the backend application, settings, logging, health, and readiness endpoints.

See `T014_PROMPT.md` for the full Claude Code prompt.

## T015 — Worker skeleton
**Depends on:** T010,T013
**Goal:** Create the worker process with configuration and graceful lifecycle handling.

See `T015_PROMPT.md` for the full Claude Code prompt.

## T020 — SQLAlchemy foundation
**Depends on:** T012,T010
**Goal:** Create database engine, sessions, base model, and conventions.

See `T020_PROMPT.md` for the full Claude Code prompt.

## T021 — Alembic foundation
**Depends on:** T020
**Goal:** Configure migrations and verify clean database migration.

See `T021_PROMPT.md` for the full Claude Code prompt.

## T022 — Identity database
**Depends on:** T021
**Goal:** Create users/authentication persistence tables and migrations.

See `T022_PROMPT.md` for the full Claude Code prompt.

## T023 — Project database
**Depends on:** T022,T021
**Goal:** Create projects and configuration-version persistence.

See `T023_PROMPT.md` for the full Claude Code prompt.

## T024 — Job database
**Depends on:** T023
**Goal:** Create jobs and job_runs with metrics and lifecycle fields.

See `T024_PROMPT.md` for the full Claude Code prompt.

## T025 — Record database
**Depends on:** T024
**Goal:** Create records and provenance tables with deduplication support.

See `T025_PROMPT.md` for the full Claude Code prompt.

## T026 — Operations database
**Depends on:** T025
**Goal:** Create exports, schedules, and audit log tables.

See `T026_PROMPT.md` for the full Claude Code prompt.

## T027 — Database indexes and constraints
**Depends on:** T026
**Goal:** Review query patterns and add only justified indexes/constraints.

See `T027_PROMPT.md` for the full Claude Code prompt.

## T030 — Domain models
**Depends on:** T023,T024,T025,T026
**Goal:** Create database-independent domain models and value objects.

See `T030_PROMPT.md` for the full Claude Code prompt.

## T031 — Job state machine
**Depends on:** T030,T024
**Goal:** Implement explicit legal job state transitions.

See `T031_PROMPT.md` for the full Claude Code prompt.

## T032 — Repository layer
**Depends on:** T020,T023,T024,T025,T026,T030
**Goal:** Create repository interfaces and MySQL implementations.

See `T032_PROMPT.md` for the full Claude Code prompt.

## T033 — Project service
**Depends on:** T030,T032,T022
**Goal:** Implement project business rules and authorization boundaries.

See `T033_PROMPT.md` for the full Claude Code prompt.

## T034 — Configuration service
**Depends on:** T033,T032,T040
**Goal:** Implement versioned provider configuration and validation workflow.

See `T034_PROMPT.md` for the full Claude Code prompt.

## T035 — Job service
**Depends on:** T031,T032,T034
**Goal:** Implement job creation and lifecycle commands.

See `T035_PROMPT.md` for the full Claude Code prompt.

## T036 — Record service
**Depends on:** T032,T030
**Goal:** Implement server-side record search, filtering, and detail retrieval.

See `T036_PROMPT.md` for the full Claude Code prompt.

## T037 — Audit service
**Depends on:** T032,T030
**Goal:** Implement structured audit events.

See `T037_PROMPT.md` for the full Claude Code prompt.

## T038 — Authentication
**Depends on:** T022,T033
**Goal:** Implement secure V1 authentication.

See `T038_PROMPT.md` for the full Claude Code prompt.

## T039 — Authorization
**Depends on:** T038,T033,T035,T036
**Goal:** Implement project-level authorization and resource isolation.

See `T039_PROMPT.md` for the full Claude Code prompt.

## T040 — Provider interface
**Depends on:** T030,T034
**Goal:** Create the generic provider contract.

See `T040_PROMPT.md` for the full Claude Code prompt.

## T041 — Google configuration
**Depends on:** T040,T034
**Goal:** Implement configuration validation for the selected Google Maps Platform product/API.

See `T041_PROMPT.md` for the full Claude Code prompt.

## T042 — Google client
**Depends on:** T041,T040
**Goal:** Implement the documented Google Maps Platform API client boundary.

See `T042_PROMPT.md` for the full Claude Code prompt.

## T043 — Google response mapper
**Depends on:** T042,T025
**Goal:** Map Google provider responses into internal records and provenance.

See `T043_PROMPT.md` for the full Claude Code prompt.

## T044 — Provider error mapping
**Depends on:** T042
**Goal:** Classify provider failures and determine retryability.

See `T044_PROMPT.md` for the full Claude Code prompt.

## T045 — Provider contract tests
**Depends on:** T040,T041,T042,T043,T044
**Goal:** Create a complete fake-provider contract suite.

See `T045_PROMPT.md` for the full Claude Code prompt.

## T050 — Normalization pipeline
**Depends on:** T030,T043
**Goal:** Implement deterministic record normalization.

See `T050_PROMPT.md` for the full Claude Code prompt.

## T051 — Validation pipeline
**Depends on:** T050
**Goal:** Validate record quality and produce structured warnings/rejections.

See `T051_PROMPT.md` for the full Claude Code prompt.

## T052 — Canonical identity
**Depends on:** T050,T051
**Goal:** Create deterministic record identity and collision tests.

See `T052_PROMPT.md` for the full Claude Code prompt.

## T053 — Deduplication
**Depends on:** T052,T032
**Goal:** Implement batch and database deduplication.

See `T053_PROMPT.md` for the full Claude Code prompt.

## T054 — Transactional persistence
**Depends on:** T053,T025
**Goal:** Persist normalized records atomically and accurately update metrics.

See `T054_PROMPT.md` for the full Claude Code prompt.

## T055 — Pipeline metrics
**Depends on:** T054,T024
**Goal:** Implement accurate pipeline/job metrics.

See `T055_PROMPT.md` for the full Claude Code prompt.

## T060 — Redis queue
**Depends on:** T015,T035
**Goal:** Implement queue abstraction and Redis-backed job transport.

See `T060_PROMPT.md` for the full Claude Code prompt.

## T061 — Worker job execution
**Depends on:** T060,T035,T040,T050,T054
**Goal:** Implement end-to-end worker orchestration using the fake provider first.

See `T061_PROMPT.md` for the full Claude Code prompt.

## T062 — Worker heartbeat
**Depends on:** T061,T024
**Goal:** Implement active-job heartbeat and stale detection.

See `T062_PROMPT.md` for the full Claude Code prompt.

## T063 — Retry system
**Depends on:** T044,T061
**Goal:** Implement bounded, classified retry behavior.

See `T063_PROMPT.md` for the full Claude Code prompt.

## T064 — Cancellation
**Depends on:** T035,T061
**Goal:** Implement cooperative job cancellation.

See `T064_PROMPT.md` for the full Claude Code prompt.

## T065 — Worker recovery
**Depends on:** T062,T063,T064
**Goal:** Recover jobs after worker crashes.

See `T065_PROMPT.md` for the full Claude Code prompt.

## T070 — Next.js app shell
**Depends on:** T011,T039
**Goal:** Build the dashboard shell and navigation.

See `T070_PROMPT.md` for the full Claude Code prompt.

## T071 — Dashboard UI
**Depends on:** T070,T035,T036
**Goal:** Build operational dashboard with API-backed metrics.

See `T071_PROMPT.md` for the full Claude Code prompt.

## T072 — Project UI
**Depends on:** T033,T070
**Goal:** Build project list, creation, detail, and archive flows.

See `T072_PROMPT.md` for the full Claude Code prompt.

## T073 — Configuration wizard
**Depends on:** T034,T041,T072
**Goal:** Build the multi-step collection configuration workflow.

See `T073_PROMPT.md` for the full Claude Code prompt.

## T074 — Job UI
**Depends on:** T035,T061,T071
**Goal:** Build job list/detail/progress/action screens.

See `T074_PROMPT.md` for the full Claude Code prompt.

## T075 — Records UI
**Depends on:** T036,T054,T074
**Goal:** Build scalable records table, filtering, and detail view.

See `T075_PROMPT.md` for the full Claude Code prompt.

## T076 — Export UI
**Depends on:** T036,T026
**Goal:** Build export creation/status/download interface.

See `T076_PROMPT.md` for the full Claude Code prompt.

## T077 — Schedule UI
**Depends on:** T026,T083
**Goal:** Build schedule creation and management screens.

See `T077_PROMPT.md` for the full Claude Code prompt.

## T078 — Settings UI
**Depends on:** T038,T041,T070
**Goal:** Build account/provider/application settings.

See `T078_PROMPT.md` for the full Claude Code prompt.

## T080 — CSV export
**Depends on:** T036,T026,T076
**Goal:** Implement authorized server-side CSV generation.

See `T080_PROMPT.md` for the full Claude Code prompt.

## T081 — JSON export
**Depends on:** T036,T026,T076
**Goal:** Implement authorized JSON export.

See `T081_PROMPT.md` for the full Claude Code prompt.

## T082 — Excel export
**Depends on:** T080,T081
**Goal:** Add Excel export after stable CSV/JSON.

See `T082_PROMPT.md` for the full Claude Code prompt.

## T083 — Scheduler service
**Depends on:** T035,T026
**Goal:** Implement backend scheduling that creates jobs rather than executing providers directly.

See `T083_PROMPT.md` for the full Claude Code prompt.

## T084 — Usage budget
**Depends on:** T041,T083,T035
**Goal:** Implement application-side collection limits and guardrails.

See `T084_PROMPT.md` for the full Claude Code prompt.

## T085 — Observability
**Depends on:** T014,T061,T065
**Goal:** Implement logs, metrics, request IDs, and diagnostics.

See `T085_PROMPT.md` for the full Claude Code prompt.

## T090 — Security review
**Depends on:** T038,T039,T076,T085
**Goal:** Perform application security review and fix discovered defects.

See `T090_PROMPT.md` for the full Claude Code prompt.

## T091 — Reliability review
**Depends on:** T061,T062,T063,T064,T065
**Goal:** Test worker crash, duplicate delivery, provider failure, DB failure, and cancellation.

See `T091_PROMPT.md` for the full Claude Code prompt.

## T092 — Performance review
**Depends on:** T027,T036,T080,T081
**Goal:** Measure query and job performance using realistic synthetic data.

See `T092_PROMPT.md` for the full Claude Code prompt.

## T093 — End-to-end test
**Depends on:** T070,T073,T074,T075,T076,T061
**Goal:** Prove the complete product workflow using a fake provider.

See `T093_PROMPT.md` for the full Claude Code prompt.

## T094 — Documentation finalization
**Depends on:** T093
**Goal:** Complete developer, operator, and user documentation.

See `T094_PROMPT.md` for the full Claude Code prompt.

## T100 — Database backup
**Depends on:** T094
**Goal:** Create and test MySQL backup/restore procedure.

See `T100_PROMPT.md` for the full Claude Code prompt.

## T101 — Deployment documentation
**Depends on:** T094,T100
**Goal:** Document production deployment without prematurely forcing Docker.

See `T101_PROMPT.md` for the full Claude Code prompt.

## T102 — Release gate
**Depends on:** T090,T091,T092,T093,T094,T100,T101
**Goal:** Run the V1 definition-of-done checklist and resolve failures.

See `T102_PROMPT.md` for the full Claude Code prompt.

## T103 — V1 release
**Depends on:** T102
**Goal:** Prepare the first stable release.

See `T103_PROMPT.md` for the full Claude Code prompt.
