# T041 --- Google configuration

## Task purpose

Implement configuration validation for the selected Google Maps Platform
product/API.

## Dependencies

T040,T034

## Full Claude Code implementation prompt

You are implementing T041 --- Google Configuration.

READ: - docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md -
docs/10_SECURITY_DEEP.md - current Google Maps Platform documentation
applicable to the selected API/product

OBJECTIVE: Validate Google-specific configuration before execution.

IMPLEMENT: 1. Define supported operation(s). 2. Define allowed request
fields. 3. Validate query/location parameters. 4. Validate numeric
ranges. 5. Validate max work/usage limits. 6. Validate provider
credential presence server-side. 7. Validate configuration against
documented API requirements. 8. Produce actionable validation errors. 9.
Add tests for valid and invalid configurations. 10. Document provider
assumptions and revisit them before release.

DO NOT: - implement CAPTCHA solving; - bypass rate limits; - use
unauthorized browser scraping as a fallback.

ACCEPTANCE: Invalid requests never reach provider execution.

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
