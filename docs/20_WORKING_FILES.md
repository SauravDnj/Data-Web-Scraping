# Working Files

## Purpose

This file tells the next coding session exactly which files are actively
being changed.

## Active task

T042 (T000-T002, T010, T011, T014, T015, T020-T026, T030-T041
complete; T027 PARTIAL — see database/INDEX_REVIEW.md; T012/T013
prepared but blocked on user action).

## Active files

``` text
None yet — T042 has not started.
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
