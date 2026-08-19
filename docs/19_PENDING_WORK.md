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
-   [x] T021 Alembic foundation (done without live MySQL, same
        reasoning as T020 — see docs/16_MEMORY.md)
-   [x] T022 Identity database (done without live MySQL; found/fixed a
        real BigInteger-vs-SQLite autoincrement bug along the way —
        see docs/16_MEMORY.md for the `BigIntegerPK` fix every future
        table must reuse)
-   [x] T023 Project database (found/fixed SQLite FK-enforcement gap
        too; sqlite_engine fixture centralized in tests/unit/conftest.py)
-   [x] T024 Job database (done without live MySQL, same pattern)
-   [x] T025 Record database (done without live MySQL; found tests/
        had never been linted — fixed 17 issues + extended CI)
-   [x] T026 Operations database (exports/schedules/audit_logs, done
        without live MySQL — all 8 schema tasks now done except T027)
-   [~] T027 indexes/constraints review — PARTIAL. Query-to-index
        mapping/FK review/uniqueness review done (see
        database/INDEX_REVIEW.md). EXPLAIN verification against real
        MySQL not done — genuinely blocked on T012.
-   [x] T030 Domain models (pure Python, centralized status enums —
        see docs/16_MEMORY.md)
-   [x] T031 Job state machine (pure Python, 20 tests covering full
        transition matrix)
-   [x] T032 Repository layer (7 repos, found/fixed a real domain/
        schema mismatch — see docs/16_MEMORY.md)
-   [x] T033 Project service (authz boundaries + audit events, no
        live MySQL needed)
-   [x] T034 Configuration service (versioning/activation/validation,
        resolved a circular task-graph dependency — see docs/16_MEMORY.md)
-   [x] T035 Job service (transactional creation, idempotency, gated
        retry — first ALTER-TABLE migration, needed Alembic batch mode
        for SQLite; see docs/16_MEMORY.md)
-   [x] T036 Record service (project-scoped search/filter/sort, safe
        pagination, synthetic-large-dataset test)
-   [x] T037 Audit service (centralized action names + secret
        redaction; added missing config audit calls; refactored
        Project/JobService to use it)
-   [x] T038 Authentication (password login + opaque session tokens,
        lockout, `/api/v1/auth/{login,logout,me}`; found/fixed a real
        naive/aware datetime comparison bug and a real pre-existing
        migration-test bug — see docs/16_MEMORY.md)
-   [x] T039 Authorization (confirmed ownership already correctly
        enforced across T033-T036's services; added centralized HTTP
        error mapping + 6 missing negative cross-user tests — see
        database/AUTHORIZATION_REVIEW.md)
-   [x] T040 Provider interface (`ProviderAdapter` Protocol +
        supporting domain value objects + `FakeProviderAdapter`; reused
        T034's `ConfigValidationResult` rather than duplicating — see
        docs/16_MEMORY.md)
-   [ ] T041--T045 provider (Google-specific)
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
