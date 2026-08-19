# Pending Work

## Immediate

-   [x] T000 repository bootstrap
-   [x] T001 coding standards
-   [x] T002 CI baseline
-   [x] T010 Python environment
-   [x] T011 Node environment
-   [ ] T012 MySQL (prepared, blocked on user running the setup script)
-   [ ] T013 Redis (prepared, blocked on Memurai-vs-skip decision)
-   [x] T014 FastAPI (done out of order — readiness checks are
        dependency-injected and fully testable without live
        MySQL/Redis; see docs/16_MEMORY.md)
-   [x] T015 worker skeleton (done out of order, same reasoning)

## Next

-   [x] T020 SQLAlchemy foundation (done without live MySQL — see
        docs/16_MEMORY.md; verified against SQLite + a deterministic
        connection-error test)
-   [ ] T021--T027 database (T021 needs a real MySQL connection to run
        an actual migration — likely blocked on T012)
-   [ ] T030--T039 backend
-   [ ] T040--T045 provider
-   [ ] T050--T055 pipeline
-   [ ] T060--T065 worker
-   [ ] T070--T078 frontend
-   [ ] T080--T085 operations
-   [ ] T090--T094 quality
-   [ ] T100--T103 release

## Deferred

-   advanced AI extraction;
-   multi-tenant billing;
-   distributed deployment;
-   additional provider ecosystem;
-   advanced analytics.

Do not start deferred work unless the current milestone is stable.
