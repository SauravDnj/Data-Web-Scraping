# Detailed Claude Code Prompts --- Pipeline, Worker, UI

## T050 --- Normalization

``` text
Implement T050.

Create pure normalization functions.

Normalize:
- whitespace;
- Unicode where safe;
- URL format;
- numeric fields;
- timestamps;
- categories.

Requirements:
- deterministic;
- unit tested;
- no provider calls;
- no destructive transformations.
```

## T051 --- Validation

``` text
Implement T051.

Create data quality validation.

Each item returns:
- valid;
- warning;
- rejected.

Include structured field errors.

Do not delete rejected input silently; attach rejection information to the job pipeline.
```

## T052 --- Canonical identity

``` text
Implement T052.

Design deterministic record identity.

Prefer permitted stable provider identifiers.

Fallback only when appropriate.

Write tests showing:
- same entity produces same key;
- clearly different entities do not collide in normal cases.
```

## T053 --- Deduplication

``` text
Implement T053.

Deduplicate:
1. within a response batch;
2. against existing project records.

Use canonical identity.

Do not deduplicate by name alone.

Add false-merge regression tests.
```

## T054 --- Persistence

``` text
Implement T054.

Implement transactional record upsert.

Requirements:
- new record;
- existing record;
- rejected record;
- transaction rollback;
- accurate counters.

Do not increment success counters before commit.
```

## T060 --- Queue

``` text
Implement T060.

Create queue abstraction.

Requirements:
- enqueue job ID;
- dequeue;
- acknowledgement;
- failure handling;
- tests.

Redis is transport only. MySQL remains the source of truth.
```

## T061 --- Job execution

``` text
Implement T061.

Worker flow:

claim
→ heartbeat
→ load config
→ provider validate
→ provider collect
→ normalize
→ validate
→ deduplicate
→ persist
→ metrics
→ finalize

Handle exceptions at each boundary.

Do not hide partial failures.
```

## T062 --- Heartbeat

``` text
Implement T062.

Worker updates heartbeat during active jobs.

Create stale-job detection.

Acceptance:
- healthy worker stays current;
- stopped worker becomes stale;
- stale job can enter recovery path.
```

## T063 --- Retry

``` text
Implement T063.

Implement bounded exponential backoff.

Only retry errors explicitly classified as retryable.

Do not retry:
- invalid config;
- forbidden;
- authentication failure requiring user action;
- policy rejection.

Test attempt limits.
```

## T064 --- Cancellation

``` text
Implement T064.

Use cooperative cancellation.

API requests cancellation.
Worker checks cancellation between work units.

Do not kill a process in a way that leaves transactions half-open.
```

## T070 --- App shell

``` text
Implement T070.

Create navigation and shared layout.

Pages:
Dashboard
Projects
Jobs
Records
Schedules
Settings

Implement loading/error/empty components.

No provider business logic.
```

## T071 --- Dashboard

``` text
Implement T071.

Display:
- active jobs;
- completed jobs;
- failed jobs;
- record count;
- recent activity.

Use API data.

Do not calculate authoritative metrics in the browser.
```

## T073 --- Configuration wizard

``` text
Implement T073.

Build a multi-step form:
1. project;
2. provider;
3. query/location;
4. fields;
5. limits;
6. review.

The review screen must show the exact configuration that will be submitted.

Prevent submission when validation fails.
```

## T074 --- Job UI

``` text
Implement T074.

Show job:
- state;
- progress;
- metrics;
- timestamps;
- error;
- actions.

Actions must respect backend permissions and current job state.

Do not assume an action is valid just because a button was clicked.
```

## T075 --- Records

``` text
Implement T075.

Use server-side pagination.

Provide:
- filters;
- sorting;
- record detail;
- loading state;
- empty state;
- error state.

Never fetch the entire dataset to the browser.
```
