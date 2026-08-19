# Master Task Backlog

## Phase 0 --- Project governance

-   [ ] T000 Create repository
-   [ ] T001 Create documentation structure
-   [ ] T002 Define coding conventions
-   [ ] T003 Define branch/commit conventions
-   [ ] T004 Create `.env.example`
-   [ ] T005 Create initial CI checks

## Phase 1 --- Local foundation

-   [ ] T010 Install/verify Python
-   [ ] T011 Install/verify Node.js
-   [ ] T012 Install/verify MySQL
-   [ ] T013 Install/verify Redis
-   [ ] T014 Create Python environment
-   [ ] T015 Bootstrap Next.js
-   [ ] T016 Bootstrap FastAPI
-   [ ] T017 Configure formatting/linting
-   [ ] T018 Configure logging
-   [ ] T019 Health/readiness endpoints

## Phase 2 --- Database

-   [ ] T020 Create SQLAlchemy base
-   [ ] T021 Configure Alembic
-   [ ] T022 Create users migration
-   [ ] T023 Create projects migration
-   [ ] T024 Create collection_configs migration
-   [ ] T025 Create jobs migration
-   [ ] T026 Create job_runs migration
-   [ ] T027 Create records migration
-   [ ] T028 Create provenance migration
-   [ ] T029 Create exports migration
-   [ ] T030 Create schedules migration
-   [ ] T031 Create audit_logs migration
-   [ ] T032 Add indexes
-   [ ] T033 Add migration tests

## Phase 3 --- Domain/backend

-   [ ] T040 Define domain models
-   [ ] T041 Define job state machine
-   [ ] T042 Build repositories
-   [ ] T043 Build project service
-   [ ] T044 Build configuration service
-   [ ] T045 Build job service
-   [ ] T046 Build record service
-   [ ] T047 Build audit service
-   [ ] T048 Build API routers
-   [ ] T049 Add authentication
-   [ ] T050 Add authorization

## Phase 4 --- Provider integration

-   [ ] T060 Define provider adapter interface
-   [ ] T061 Implement Google provider configuration validation
-   [ ] T062 Implement permitted Google Maps Platform collection
    operation(s)
-   [ ] T063 Map provider response to internal model
-   [ ] T064 Implement quota/error classification
-   [ ] T065 Implement provider health diagnostics
-   [ ] T066 Add provider contract tests

## Phase 5 --- Worker/jobs

-   [ ] T070 Configure Redis
-   [ ] T071 Build queue interface
-   [ ] T072 Build worker process
-   [ ] T073 Implement job execution
-   [ ] T074 Implement heartbeat
-   [ ] T075 Implement cancellation
-   [ ] T076 Implement bounded retries
-   [ ] T077 Implement dead/failure handling
-   [ ] T078 Implement job metrics

## Phase 6 --- Data processing

-   [ ] T080 Normalization pipeline
-   [ ] T081 Validation pipeline
-   [ ] T082 Canonical identity
-   [ ] T083 Deduplication
-   [ ] T084 Data quality status
-   [ ] T085 Persistence pipeline

## Phase 7 --- Frontend

-   [ ] T090 App shell
-   [ ] T091 Dashboard
-   [ ] T092 Project list
-   [ ] T093 Project create/edit
-   [ ] T094 Configuration form
-   [ ] T095 Job list
-   [ ] T096 Job detail
-   [ ] T097 Records table
-   [ ] T098 Record detail
-   [ ] T099 Export UI
-   [ ] T100 Schedule UI
-   [ ] T101 Settings UI
-   [ ] T102 Loading/empty/error states

## Phase 8 --- Exports/scheduling

-   [ ] T110 CSV export
-   [ ] T111 JSON export
-   [ ] T112 Excel export
-   [ ] T113 Schedule service
-   [ ] T114 Scheduler worker
-   [ ] T115 Usage-budget guard

## Phase 9 --- Security/testing

-   [ ] T120 Authentication tests
-   [ ] T121 Authorization tests
-   [ ] T122 API validation tests
-   [ ] T123 SQL/injection regression tests
-   [ ] T124 Export authorization tests
-   [ ] T125 E2E happy path
-   [ ] T126 E2E failure path
-   [ ] T127 Dependency/security review

## Phase 10 --- Release

-   [ ] T130 Production configuration
-   [ ] T131 Database backup plan
-   [ ] T132 Logging/monitoring
-   [ ] T133 Error alerting
-   [ ] T134 Deployment documentation
-   [ ] T135 Disaster recovery procedure
-   [ ] T136 V1 release checklist
