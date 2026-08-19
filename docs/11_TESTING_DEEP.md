# Testing --- Deep

## Unit tests

Target pure logic first.

Examples:

``` text
test_job_state_transition()
test_invalid_job_transition()
test_normalize_phone()
test_normalize_url()
test_canonical_key()
test_deduplicate_batch()
test_retry_classification()
```

## Repository tests

Test:

``` text
create project
create job
save record
upsert record
query records
create export
audit event
```

## API tests

Test:

``` text
200 success
400 validation
401 unauthenticated
403 unauthorized
404 missing
409 conflict
provider error mapping
```

## Worker tests

Simulate:

``` text
success
temporary provider error
permanent provider error
worker crash
duplicate delivery
cancel request
```

## Frontend tests

Test:

``` text
form validation
loading state
error state
job progress
record filters
export initiation
```

## E2E

Use a fake provider fixture.

Do not make the automated test suite depend on live external provider
calls.

## Definition of done

No task is complete if the implementation works only manually and there
is no automated coverage for its critical logic.
