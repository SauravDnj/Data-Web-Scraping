# Jobs, Queue, and Worker --- Deep

## Why a queue

HTTP requests are short-lived.

Collection can take minutes.

Therefore:

``` text
HTTP request
  -> create job
  -> enqueue
  -> return
```

Worker:

``` text
dequeue
  -> execute
  -> update DB
```

## Job state machine

Allowed:

``` text
draft → queued
queued → running
queued → cancelled
running → paused
running → completed
running → partially_completed
running → failed
running → cancelled
paused → running
paused → cancelled
```

Invalid transitions are rejected.

## Claiming a job

A worker must atomically claim a queued job.

Conceptually:

``` text
UPDATE jobs
SET status='running'
WHERE id=? AND status='queued'
```

Only the worker that successfully changes one row owns the job.

## Heartbeat

Worker updates:

``` text
heartbeat_at
```

at a regular interval.

A recovery process detects stale jobs.

## Retry

Use bounded retry.

Example policy:

``` text
attempt 1 → immediate/short delay
attempt 2 → longer delay
attempt 3 → longer delay
then permanent failure
```

Do not retry:

-   invalid configuration;
-   invalid credentials;
-   forbidden operation;
-   provider policy rejection.

Retry only explicitly retryable errors.

## Cancellation

Cancellation should be cooperative.

``` text
job.cancel_requested = true
```

Worker checks between safe units of work.

## Metrics

Track:

``` text
duration
work units
success
failure
retry count
records created
records updated
records rejected
```

## Worker logs

Use structured logs:

``` json
{
  "event": "job_completed",
  "job_id": 123,
  "duration_seconds": 42,
  "records_created": 100
}
```
