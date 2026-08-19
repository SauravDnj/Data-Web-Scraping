# Working Files

## Purpose

This file tells the next coding session exactly which files are actively
being changed.

## Active task

T027 PARTIAL — genuinely blocked on T012 (EXPLAIN verification needs
real MySQL). T000-T002, T010, T011, T014, T015, T020-T026 fully
complete. See docs/18_COMPLETED_WORK.md and database/INDEX_REVIEW.md.

Paused here to check in with the user — this is a natural milestone
(all local-foundation and DB-schema work that doesn't need live MySQL
is done) and further tasks (T030+) increasingly benefit from T012/T013
being resolved.

## Active files

``` text
None — awaiting user input on T012/T013 before resuming.
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
