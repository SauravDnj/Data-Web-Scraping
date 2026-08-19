# T042 --- Google client

## Task purpose

Implement the documented Google Maps Platform API client boundary.

## Dependencies

T041,T040

## Full Claude Code implementation prompt

You are implementing T042 --- Google Client.

READ: - docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md -
docs/10_SECURITY_DEEP.md - current official Google Maps Platform API
documentation

OBJECTIVE: Implement provider communication using the selected
documented Google Maps Platform API/SDK.

IMPLEMENT: 1. Add server-side credential loading. 2. Configure request
timeout. 3. Configure safe retry for documented transient errors. 4.
Implement request construction. 5. Implement response parsing. 6.
Implement pagination if the selected API supports it. 7. Implement
usage/quota metadata handling where available. 8. Implement structured
provider errors. 9. Redact credentials from logs. 10. Add dependency
injection for tests.

DO NOT: - bypass CAPTCHA; - evade quotas; - rotate proxies to evade
controls; - use fake credentials; - collect private data.

ACCEPTANCE: Mock tests verify request construction and response
handling; no real credentials are committed.

## Task completion record

Claude Code must not mark this task complete until: - implementation is
present; - acceptance criteria are verified; - relevant tests pass; -
Git diff is reviewed; - project tracking documents are updated.

## Required tracking updates

-   `docs/15_PROGRESS.md`
-   `docs/16_MEMORY.md`
-   `docs/17_CURRENT_WORK.md`
-   `docs/18_COMPLETED_WORK.md`
-   `docs/19_PENDING_WORK.md`
-   `docs/20_WORKING_FILES.md`
