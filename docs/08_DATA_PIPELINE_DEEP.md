# Data Pipeline --- Deep

## Pipeline stages

### Stage 1: Raw response

Keep only data that the provider contract allows the application to
retain.

### Stage 2: Schema validation

Check types and required fields.

Example:

``` text
rating must be numeric
latitude must be numeric
longitude must be numeric
```

### Stage 3: Normalization

Normalize:

-   whitespace;
-   Unicode;
-   URLs;
-   numeric fields;
-   timestamps;
-   category values.

### Stage 4: Quality

Quality rules can produce:

``` text
valid
warning
rejected
```

Example:

``` text
missing website → warning
invalid coordinate → rejected
```

### Stage 5: Canonical identity

Create a deterministic key.

Example:

``` text
provider + provider_record_id
```

If provider ID is unavailable and use of alternative identifiers is
appropriate:

``` text
provider + normalized(name) + normalized(address)
```

This is only a fallback.

### Stage 6: Deduplication

Within a batch:

``` text
A
A
B
```

becomes:

``` text
A
B
```

Against MySQL:

``` text
existing A → update/skip according to policy
new B → insert
```

### Stage 7: Persistence

Use transaction-safe upsert logic.

### Stage 8: Metrics

Increment:

``` text
records_created
records_updated
records_rejected
```

## Never hide failures

Bad:

``` text
500 records requested
300 saved
system says completed
```

Good:

``` text
500 work units
300 successful
150 skipped
50 failed
status = partially_completed
```
