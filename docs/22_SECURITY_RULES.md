# Security Rules for Every Task

Before accepting code, check:

## Secrets

-   [ ] no API keys in source;
-   [ ] no passwords in source;
-   [ ] no credentials in logs;
-   [ ] `.env` ignored.

## API

-   [ ] authentication required where appropriate;
-   [ ] authorization checked;
-   [ ] request validation exists;
-   [ ] errors do not expose stack traces.

## Database

-   [ ] parameterized/ORM queries;
-   [ ] migrations reviewed;
-   [ ] no root DB account from application.

## Worker

-   [ ] job ownership enforced;
-   [ ] retry bounded;
-   [ ] cancellation safe;
-   [ ] logs redacted.

## Provider

-   [ ] documented access method;
-   [ ] no CAPTCHA bypass;
-   [ ] no anti-bot evasion;
-   [ ] no rate-limit evasion.

## Data

-   [ ] only necessary data collected;
-   [ ] provenance retained where permitted;
-   [ ] export authorization enforced.
