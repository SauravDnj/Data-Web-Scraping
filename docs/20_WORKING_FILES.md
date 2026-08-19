# Working Files

## Purpose

This file tells the next coding session exactly which files are actively
being changed.

## Active task

T022 (T000-T002, T010, T011, T014, T015, T020, T021 complete; T012/T013
prepared but blocked on user action — see docs/18_COMPLETED_WORK.md).
T022 (first real business table) likely needs T012 to fully verify.

## Active files

``` text
None yet — T022 has not started.
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
