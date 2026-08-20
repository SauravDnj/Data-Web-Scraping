# Working Files

## Purpose

This file tells the next coding session exactly which files are actively
being changed.

## Active task

T072 (T000-T002, T010, T011, T014, T015, T020-T026, T030-T045,
T050-T055, T060-T065, T070, T071 complete; T027 PARTIAL — see
database/INDEX_REVIEW.md; T012/T013 prepared but blocked on user
action; T013's local-testing gap mitigated via `fakeredis`). Phases 4
(Provider), 5 (Data pipeline), and 6 (Worker) are all fully complete.
Phase 7 (Frontend) has the app shell and dashboard.

## Active files

``` text
None yet — T072 has not started.
```

## T071 files (complete — for reference)

``` text
apps/api/app/api/pagination.py                      (new — PagedResponse[T])
apps/api/app/api/v1/jobs.py                          (new — GET /jobs, GET /jobs/summary)
apps/api/app/api/v1/records.py                       (new — GET /records/count)
apps/api/app/api/v1/__init__.py                      (modified — routers wired in)
apps/api/app/api/dependencies.py                     (modified — get_audit_service/get_project_service/get_configuration_service/get_job_service/get_record_service added)
apps/api/app/domain/jobs.py                          (modified — JobStatusSummary added)
apps/api/app/repositories/jobs.py                    (modified — list_for_user/count_by_status_for_user added)
apps/api/app/repositories/records.py                 (modified — count_for_user added)
apps/api/app/services/jobs.py                        (modified — list_for_user/summarize_for_user added)
apps/api/app/services/records.py                     (modified — count_for_user added)
apps/web/lib/api/dashboard.ts                        (new)
apps/web/components/dashboard/StatCard.tsx            (new)
apps/web/components/dashboard/RecentJobsTable.tsx     (new)
apps/web/components/jobs/JobStatusBadge.tsx           (new)
apps/web/app/(app)/dashboard/page.tsx                 (modified — real dashboard replacing the T070 placeholder)
tests/unit/test_repositories.py                       (modified — 4 new tests)
tests/unit/test_job_service.py                        (modified — 2 new tests)
tests/unit/test_record_service.py                     (modified — 1 new test)
tests/integration/test_dashboard_api.py                (new — 6 tests)
apps/web/__tests__/components/DashboardPage.test.tsx  (new — 4 tests)
```

## T070 files (complete — for reference)

``` text
apps/web/lib/auth/storage.ts                        (new)
apps/web/lib/auth/AuthContext.tsx                    (new)
apps/web/lib/api/client.ts                           (modified — 204 response handling fixed)
apps/web/components/ui/Button.tsx                    (new)
apps/web/components/feedback/EmptyState.tsx          (new)
apps/web/components/feedback/ErrorState.tsx          (new)
apps/web/components/feedback/Toast.tsx               (new)
apps/web/components/layout/nav-items.ts              (new)
apps/web/components/layout/Sidebar.tsx               (new)
apps/web/components/layout/TopNav.tsx                (new)
apps/web/components/auth/LoginForm.tsx                (new)
apps/web/app/layout.tsx                              (modified — AuthProvider/ToastProvider wired in)
apps/web/app/page.tsx                                (modified — redirects to /dashboard)
apps/web/app/login/page.tsx                           (new)
apps/web/app/(app)/layout.tsx                         (new — auth-guarded shell)
apps/web/app/(app)/dashboard/page.tsx                 (new, placeholder)
apps/web/app/(app)/projects/page.tsx                  (new, placeholder)
apps/web/app/(app)/jobs/page.tsx                      (new, placeholder)
apps/web/app/(app)/records/page.tsx                   (new, placeholder)
apps/web/app/(app)/schedules/page.tsx                 (new, placeholder)
apps/web/app/(app)/settings/page.tsx                  (new)
apps/web/vitest.setup.ts                              (modified — RTL auto-cleanup registered)
apps/web/__tests__/page.test.tsx                      (modified — new redirect behavior)
apps/web/__tests__/api-client.test.ts                 (new)
apps/web/__tests__/components/EmptyState.test.tsx     (new)
apps/web/__tests__/components/ErrorState.test.tsx     (new)
apps/web/__tests__/components/Toast.test.tsx          (new)
apps/web/__tests__/components/Sidebar.test.tsx        (new)
apps/web/__tests__/components/LoginForm.test.tsx      (new)
```

## T065 files (complete — for reference)

``` text
workers/jobs/recovery.py                         (new)
apps/api/app/repositories/jobs.py                  (modified — close_stale_run added)
apps/api/app/domain/job_errors.py                  (modified — PERSISTENCE_ERROR_CODE/WORKER_CRASHED_ERROR_CODE)
apps/api/app/domain/audit_actions.py               (modified — JOB_RECOVERED added)
tests/unit/test_recovery.py                        (new)
```

## T064 files (complete — for reference)

``` text
database/migrations/versions/ee8f2297969d_add_cancel_requested_fields_to_jobs.py  (new)
apps/api/app/domain/jobs.py                     (modified — cancel_requested/cancel_requested_at added to Job)
apps/api/app/db/models/job.py                   (modified — matching columns)
apps/api/app/repositories/jobs.py                (modified — request_cancellation/is_cancellation_requested added)
apps/api/app/services/jobs.py                    (modified — cancel_job() reconciled: immediate vs. cooperative)
workers/jobs/execute_collection.py               (modified — cancellation checked between items, safe-boundary stop)
tests/unit/test_job_service.py                   (modified — 6 new tests)
tests/integration/test_execute_collection.py     (modified — 2 new tests)
```

## T063 files (complete — for reference)

``` text
workers/jobs/retry.py           (new)
tests/unit/test_retry.py        (new)
```

## T062 files (complete — for reference)

``` text
workers/jobs/heartbeat.py                      (new)
workers/jobs/execute_collection.py              (modified — HeartbeatUpdater wired into the collect loop)
apps/api/app/repositories/jobs.py               (modified — touch_heartbeat/list_stale_running_runs added)
tests/unit/test_heartbeat.py                    (new)
```

## T061 files (complete — for reference)

``` text
workers/jobs/__init__.py                            (new)
workers/jobs/execute_collection.py                   (new)
apps/api/app/repositories/jobs.py                     (modified — claim_queued_job/finalize_job/finish_run added)
tests/unit/factories.py                               (modified — make_config gained an optional config_json param)
tests/integration/test_execute_collection.py          (new)
```

## T060 files (complete — for reference)

``` text
workers/queue.py                (modified — JobQueue/RedisJobQueue added)
apps/api/pyproject.toml         (modified — fakeredis added to dev extras)
tests/unit/test_queue.py        (new)
```

## T055 files (complete — for reference)

``` text
apps/api/app/pipeline/metrics.py                          (new)
apps/api/app/repositories/jobs.py                          (modified — update_counters added)
tests/unit/test_pipeline_metrics.py                        (new)
tests/integration/test_pipeline_metrics_transaction.py     (new)
```

## T054 files (complete — for reference)

``` text
apps/api/app/pipeline/persist.py               (new)
tests/integration/test_pipeline_persist.py     (new)
```

## T053 files (complete — for reference)

``` text
apps/api/app/pipeline/deduplicate.py           (new)
apps/api/app/repositories/records.py           (modified — update_collected_data added)
tests/unit/test_pipeline_deduplicate.py        (new)
```

## T052 files (complete — for reference)

``` text
apps/api/app/pipeline/canonical_identity.py    (new)
tests/unit/test_pipeline_canonical_identity.py (new)
```

## T051 files (complete — for reference)

``` text
apps/api/app/pipeline/validate.py                    (new)
apps/api/app/providers/google_maps/mapper.py          (modified — GOOGLE_FIELD_RULES + validate_google_place_record added)
tests/unit/test_pipeline_validate.py                  (new)
tests/unit/test_google_maps_mapper.py                 (modified — 3 new tests)
```

## T050 files (complete — for reference)

``` text
apps/api/app/pipeline/__init__.py                        (new)
apps/api/app/pipeline/normalize.py                        (new)
apps/api/app/providers/google_maps/mapper.py              (modified — wired in normalize_record_data)
tests/fixtures/pipeline/normalize_regression.json         (new)
tests/unit/test_pipeline_normalize.py                     (new)
```

## T045 files (complete — for reference)

``` text
apps/api/app/providers/google_maps/provider.py              (new)
apps/api/app/providers/google_maps/client.py                (modified — malformed-response robustness fix)
tests/fixtures/google_maps/text_search_response_valid.json  (new)
tests/fixtures/google_maps/text_search_response_empty.json  (new)
tests/fixtures/google_maps/text_search_response_malformed.json (new)
tests/fixtures/google_maps/text_search_response_page1.json  (new)
tests/fixtures/google_maps/text_search_response_page2.json  (new)
tests/fixtures/google_maps/error_quota.json                 (new)
tests/fixtures/google_maps/error_authentication.json        (new)
tests/fixtures/google_maps/error_transient.json             (new)
tests/unit/test_google_maps_provider_contract.py            (new)
```

## T044 files (complete — for reference)

``` text
apps/api/app/providers/google_maps/errors.py    (new)
apps/api/app/domain/provider_contracts.py       (modified — ProviderError extended, default_retryable_for_category added)
apps/api/app/domain/job_errors.py               (modified — reconciled with ProviderErrorCategory)
apps/api/app/services/jobs.py                   (modified — docstring only)
tests/unit/fakes.py                             (modified — FakeProviderAdapter.classify_error updated)
tests/unit/test_job_service.py                  (modified — "transient_network" -> "temporary")
tests/unit/test_google_maps_errors.py           (new)
```

## T043 files (complete — for reference)

``` text
apps/api/app/providers/google_maps/mapper.py       (new)
apps/api/app/domain/records.py                     (modified — RecordDraft added)
tests/fixtures/google_maps/full_place.json         (new)
tests/fixtures/google_maps/minimal_place.json       (new)
tests/fixtures/google_maps/malformed_place.json     (new)
tests/unit/test_google_maps_mapper.py               (new)
```

## T042 files (complete — for reference)

``` text
apps/api/app/providers/google_maps/client.py   (new)
apps/api/pyproject.toml                        (modified — httpx moved to real deps)
tests/unit/test_google_maps_client.py          (new)
```

## T041 files (complete — for reference)

``` text
apps/api/app/providers/google_maps/__init__.py   (new)
apps/api/app/providers/google_maps/config.py     (new)
tests/unit/test_google_maps_config.py            (new)
```

## T040 files (complete — for reference)

``` text
apps/api/app/domain/provider_contracts.py    (new)
apps/api/app/providers/__init__.py           (new)
apps/api/app/providers/base.py               (new)
tests/unit/fakes.py                          (modified — FakeProviderAdapter added)
tests/unit/test_provider_interface.py        (new)
```

## T039 files (complete — for reference)

``` text
apps/api/app/api/service_errors.py                (new)
apps/api/app/main.py                               (modified)
database/AUTHORIZATION_REVIEW.md                   (new)
tests/integration/test_service_error_handlers.py   (new)
tests/unit/test_project_service.py                 (modified)
tests/unit/test_configuration_service.py           (modified)
tests/unit/test_job_service.py                     (modified)
```

## T038 files (complete — for reference)

``` text
apps/api/app/domain/users.py                       (new)
apps/api/app/domain/auth.py                        (new)
apps/api/app/db/models/session.py                  (new)
apps/api/app/db/models/user.py                     (modified)
apps/api/app/db/models/__init__.py                 (modified)
apps/api/app/repositories/users.py                 (new)
apps/api/app/repositories/sessions.py              (new)
apps/api/app/services/auth.py                      (new)
apps/api/app/api/envelope.py                       (new)
apps/api/app/api/dependencies.py                   (new)
apps/api/app/api/v1/auth.py                        (new)
apps/api/app/api/v1/__init__.py                    (modified)
database/migrations/versions/9e753afdce70_...py     (new)
tests/conftest.py                                   (new)
tests/unit/conftest.py                              (modified — pointer only)
tests/unit/test_auth_service.py                     (new)
tests/integration/test_auth_api.py                  (new)
tests/integration/test_migrations.py                (modified — fixed a
    real pre-existing bug in the T035 migration round-trip test)
```

## Rule

When Claude starts a task, list files it expects to change.

When the task is completed, remove them and record the final files in
COMPLETED_WORK.md.

## Example

``` text
Task: T032
Status: IN_PROGRESS

Files:
- backend/app/repositories/jobs.py
- backend/app/services/jobs.py
- tests/unit/test_jobs.py

Blocker:
None
```
