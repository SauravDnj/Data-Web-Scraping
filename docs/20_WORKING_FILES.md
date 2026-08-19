# Working Files

## Purpose

This file tells the next coding session exactly which files are actively
being changed.

## Active task

T035 (T000-T002, T010, T011, T014, T015, T020-T026, T030-T034
complete; T027 PARTIAL — see database/INDEX_REVIEW.md; T012/T013
prepared but blocked on user action).

## Active files

``` text
None yet — T034 has not started.
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
