# Real Provider Integration Gate

The real Google Maps Platform provider must not become the first
integration test.

Before enabling it, the following must already work:

-   database migrations;
-   project CRUD;
-   configuration versioning;
-   job state machine;
-   Redis queue;
-   worker;
-   fake provider;
-   normalization;
-   validation;
-   deduplication;
-   persistence;
-   dashboard;
-   job monitoring;
-   export;
-   authorization;
-   audit.

Then verify the selected current Google Maps Platform API/product
documentation and implement only its documented workflow.

Do not implement CAPTCHA bypass, anti-bot evasion, rate-limit evasion,
authentication bypass, or private-data collection.
