# V1 Definition of Done

V1 is complete only when the following end-to-end scenario works:

``` text
User logs in
 ↓
Creates Google Maps project
 ↓
Creates valid provider configuration
 ↓
Validation succeeds
 ↓
Creates job
 ↓
Job appears queued
 ↓
Worker claims job
 ↓
Approved provider operation executes
 ↓
Records normalize
 ↓
Records validate
 ↓
Records deduplicate
 ↓
Records persist in MySQL
 ↓
Job completes with accurate metrics
 ↓
Dashboard displays results
 ↓
User filters records
 ↓
User creates authorized export
 ↓
Audit event is recorded
```

Additional requirements:

-   worker recovery tested;
-   retry tested;
-   cancellation tested;
-   authorization tested;
-   no secrets in Git;
-   migrations tested;
-   documentation updated;
-   known limitations documented.
