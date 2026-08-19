# First Vertical Slice

The first meaningful milestone should be:

``` text
Create project
 ↓
Create config
 ↓
Create job
 ↓
Queue job
 ↓
Fake worker
 ↓
Fake provider returns 3 records
 ↓
Normalize
 ↓
Deduplicate
 ↓
Save MySQL
 ↓
Job completed
 ↓
Dashboard displays 3 records
```

## Why this is important

This proves that the architecture works end-to-end before
Google-specific complexity is introduced.

## Acceptance

The developer should be able to run one command sequence and observe:

``` text
Project created
Job queued
Job running
3 records created
Job completed
Records visible in UI
```

Only after this works should the real provider integration become the
next major focus.
