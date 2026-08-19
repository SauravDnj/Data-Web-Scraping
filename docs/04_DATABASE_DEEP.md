# MySQL Database --- Deep Design

## Entity relationship overview

``` text
users
  |
  +---- projects
          |
          +---- collection_configs
          |
          +---- jobs
                  |
                  +---- job_runs
                  |
                  +---- records
                          |
                          +---- record_provenance
          |
          +---- exports
          |
          +---- schedules

users
  |
  +---- audit_logs
```

## Why records belong to projects

A record may be returned by multiple projects/configurations.

The project scope provides:

-   authorization boundary;
-   filtering;
-   export boundary;
-   deduplication scope.

## JSON strategy

Use JSON for provider-specific or evolving fields.

Do NOT put every field in JSON.

Stable operational fields should remain relational:

``` text
project_id
job_id
provider
canonical_key
collected_at
```

This gives good indexing and predictable queries.

## Data lifecycle

``` text
created
 ↓
updated by later collection
 ↓
possibly marked stale
 ↓
retained/deleted according to policy
```

Do not silently delete records because a later provider response does
not contain them.

Absence from one collection is not proof that the real-world entity
disappeared.

## Uniqueness

The exact unique constraint depends on the provider's stable identifier.

If a provider gives a stable place/reference identifier and its
use/storage is permitted, prefer it.

If not, use a carefully designed canonical key and accept that it is
imperfect.

## Transactions

Record upsert should be transactional.

A job should not report a record as persisted until the transaction
commits.

## Migration discipline

Never modify a model and forget the migration.

Workflow:

``` text
change model
 ↓
generate migration
 ↓
review migration
 ↓
run migration
 ↓
test upgrade
 ↓
test downgrade where supported
```
