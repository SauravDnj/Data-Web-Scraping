# Detailed Claude Code Prompts --- Operations, Quality, Release

## T080 --- CSV export

``` text
Implement T080.

Requirements:
- server-side query;
- project authorization;
- filters;
- selected columns;
- safe filename;
- bounded export size;
- audit event;
- export status.

Do not expose records from another project.
```

## T082 --- Excel export

``` text
Implement T082 after CSV/JSON are stable.

Use the project's approved spreadsheet library.

Keep export formatting simple and reliable.

Test large-but-reasonable synthetic exports.
```

## T083 --- Scheduler

``` text
Implement T083.

Schedules create jobs; they do not directly run providers.

Requirements:
- timezone;
- enabled/disabled;
- next run;
- last run;
- duplicate prevention;
- usage budget check.

Test daylight-saving/timezone edge cases where applicable.
```

## T084 --- Usage budget

``` text
Implement T084.

Create application-side usage limits.

Before creating/executing a job:
- estimate expected usage where supported;
- compare against configured budget;
- reject or require confirmation when limits are exceeded.

Never attempt to bypass provider quotas.
```

## T085 --- Observability

``` text
Implement T085.

Add:
- structured logs;
- request IDs;
- job IDs;
- provider error metrics;
- worker metrics;
- health/readiness diagnostics.

Redact credentials.
```

## T090 --- Security review

``` text
Perform T090.

Audit:
- authentication;
- authorization;
- project isolation;
- secrets;
- export access;
- input validation;
- logs;
- dependencies.

Write tests for every discovered security boundary.

Fix issues, do not merely list them.
```

## T091 --- Reliability review

``` text
Perform T091.

Simulate:
- worker crash;
- duplicate job delivery;
- provider timeout;
- provider quota;
- DB failure;
- Redis unavailable;
- cancellation.

Verify that state remains understandable and recoverable.
```

## T092 --- Performance

``` text
Perform T092.

Inspect:
- record queries;
- job queries;
- indexes;
- N+1 queries;
- export queries.

Use realistic synthetic data.

Do not optimize based only on intuition.
```

## T093 --- E2E

``` text
Perform T093.

Use a fake provider.

Scenario:
login
→ create project
→ config
→ validate
→ create job
→ queue
→ worker
→ fake provider
→ normalize
→ DB
→ records
→ export

Test both success and partial failure.
```

## T100 --- Backup

``` text
Implement T100.

Document MySQL backup and restore.

Perform an actual restore test into a separate database.

Record:
- command;
- expected result;
- verification query.
```

## T102 --- Release gate

``` text
Perform T102.

Read docs/28_V1_DEFINITION_OF_DONE.md.

Run all tests.

Review:
- Git status;
- migrations;
- environment docs;
- security;
- provider configuration;
- logs;
- exports;
- worker recovery.

Do not declare V1 complete if any mandatory acceptance criterion is unverified.
```
