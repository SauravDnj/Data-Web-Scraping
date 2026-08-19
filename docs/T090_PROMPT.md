# T090 --- Security review

## Task purpose

Perform application security review and fix discovered defects.

## Dependencies

T038,T039,T076,T085

## Full Claude Code implementation prompt

You are implementing T090 --- Security Review.

OBJECTIVE: Audit the application as if it were about to be exposed to
untrusted users.

CHECK: 1. Authentication. 2. Authorization. 3. Project isolation. 4.
Export isolation. 5. Input validation. 6. SQL injection resistance. 7.
XSS risks. 8. CSRF/session strategy where relevant. 9. Secret storage.
10. Log redaction. 11. Dependency vulnerabilities. 12. Rate/abuse
controls.

IMPLEMENT: - security regression tests; - fixes for discovered issues; -
documented residual risks.

DO NOT merely write a report if the issue can be fixed in code.

ACCEPTANCE: Critical/high issues are fixed or explicitly blocked with a
documented decision.

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
