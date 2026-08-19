# Observability and Operations

## Logs

Use structured logs.

Important events:

``` text
application_started
job_created
job_claimed
provider_request_started
provider_request_failed
record_batch_processed
job_completed
job_failed
export_created
```

## Metrics

Track:

-   API request count;
-   API latency;
-   worker jobs;
-   job duration;
-   provider errors;
-   records created;
-   records updated;
-   records rejected;
-   export duration;
-   queue depth.

## Health

``` text
/health
```

means process is alive.

``` text
/ready
```

means required dependencies are available.

## Troubleshooting flow

If a job fails:

``` text
job ID
 ↓
job status
 ↓
job run
 ↓
error code
 ↓
structured logs
 ↓
provider response category
```

Do not ask the user to inspect raw stack traces first.

## Backup

MySQL backup/restore must be tested before production release.
