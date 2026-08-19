# Current Work

## Active task

T012 --- MySQL local setup.

## Previous task

T011 --- Next.js environment. COMPLETE. See
`docs/18_COMPLETED_WORK.md` and `apps/web/`.

## Goal

Document and verify local MySQL setup: development database,
application user with least-privilege permissions. Do not use root in
application configuration.

## Not yet in scope

-   database schema/migrations (T020/T021);
-   Google provider calls;
-   scraping;
-   worker execution;
-   frontend business screens.

## Handoff

After T012:

T013 → T014 → T015

## Known upcoming blocker

T012 (MySQL) and T013 (Redis) need real local services. MySQL has a
native Windows install; Redis does not (no official Windows build) —
this needs a decision (WSL, Memurai, or another Redis-compatible
option) before T013, flagged to the user per the earlier agreement.
