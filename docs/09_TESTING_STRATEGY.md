# Testing Strategy

## Test layers

### Unit tests

Test:

-   normalization;
-   canonical key generation;
-   validation;
-   state transitions;
-   retry classification;
-   pagination helpers;
-   configuration parsing.

No external network calls.

### Integration tests

Test:

-   API + MySQL;
-   migrations;
-   repositories;
-   job persistence;
-   Redis queue integration.

Use isolated test databases.

### Provider contract tests

Mock provider responses and verify the adapter produces the internal
normalized model.

Do not make production provider calls in automated tests unless an
explicitly controlled manual test is required.

### End-to-end tests

Test:

``` text
Login
 -> create project
 -> configure
 -> validate
 -> create job
 -> run test provider fixture
 -> inspect records
 -> export
```

## Required regression tests

Every bug fix must add a regression test when practical.

## Test data

Use synthetic fixtures. Do not commit real people's personal
information.

## Definition of done

A feature is not done until:

-   implementation exists;
-   tests exist;
-   error states are handled;
-   logs are safe;
-   documentation is updated;
-   migrations are included if schema changed;
-   lint/type checks pass.
