# T038 --- Authentication

## Task purpose

Implement secure V1 authentication.

## Dependencies

T022,T033

## Full Claude Code implementation prompt

You are implementing T038 --- Authentication.

READ: - docs/10_SECURITY_DEEP.md - docs/05_API_DEEP.md

OBJECTIVE: Implement secure user authentication appropriate for the
local-first V1.

IMPLEMENT: 1. Select one simple documented strategy. 2. Implement
registration only if required by V1. 3. Implement login. 4. Store
passwords only as strong password hashes if password auth is used. 5.
Implement secure session/token handling. 6. Protect API routes. 7. Add
logout/revocation behavior where applicable. 8. Add rate/abuse controls
appropriate for local V1. 9. Add tests for success/failure/expired
credentials.

DO NOT: - put secrets in frontend bundles; - log tokens; - invent
insecure home-grown encryption.

ACCEPTANCE: Unauthenticated protected requests fail; authenticated
requests succeed.

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
