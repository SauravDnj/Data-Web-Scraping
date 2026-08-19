# Data Pipeline

## Pipeline

``` text
Provider response
      ↓
Raw validation
      ↓
Normalization
      ↓
Field validation
      ↓
Canonicalization
      ↓
Deduplication
      ↓
Persistence
      ↓
Metrics
```

## Normalization

Examples:

-   trim whitespace;
-   normalize Unicode;
-   normalize URLs;
-   standardize phone representation when lawful and useful;
-   normalize category text;
-   normalize coordinates to decimal numbers;
-   parse ratings as bounded decimals;
-   preserve original values when required by the provider/data
    contract.

Do not aggressively transform data in a way that changes its meaning.

## Deduplication

Use a stable identity strategy.

Preferred order:

1.  provider record identifier when provided and permitted;
2.  canonical source reference;
3.  carefully constructed canonical key.

Never use name alone as a unique identifier.

Example canonical key concept:

``` text
project_scope + provider + normalized_provider_id
```

or, where no provider ID exists:

``` text
project_scope + normalized(name) + normalized(address)
```

The exact strategy must be tested against false merges.

## Data quality states

``` text
valid
warning
rejected
```

Warnings should not automatically delete records.

## Error handling

Each rejected record gets:

-   error code;
-   human-readable message;
-   job ID;
-   timestamp;
-   field if applicable.

Avoid storing secrets or sensitive request payloads in logs.

## Provider abstraction

Example interface:

``` python
class ProviderAdapter:
    def validate_config(self, config): ...
    def collect(self, config, context): ...
    def normalize(self, item): ...
```

Provider-specific SDK calls belong inside the adapter.

## Rate and quota handling

The system must know the provider's published limits and enforce
application-side budgets.

When a provider returns a usage/rate error:

-   stop or back off according to policy;
-   mark the job appropriately;
-   do not attempt to bypass the restriction.
