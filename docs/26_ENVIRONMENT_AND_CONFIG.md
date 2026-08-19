# Environment and Configuration

## Development variables

Conceptual variables:

``` text
APP_ENV=development
APP_SECRET=replace_me
DATABASE_URL=mysql+pymysql://app_user:password@localhost:3306/google_data_platform
REDIS_URL=redis://localhost:6379/0
GOOGLE_MAPS_API_KEY=replace_me
FRONTEND_ORIGIN=http://localhost:3000
LOG_LEVEL=INFO
```

Use the exact provider credential variables required by the selected
Google Maps Platform SDK/API.

## Rules

-   `.env` is local only.
-   `.env.example` contains placeholders.
-   Production secrets belong in a secret manager/environment
    configuration.
-   Never print configuration wholesale.
-   Never log API keys.

## Configuration validation

Startup should fail clearly when mandatory infrastructure variables are
missing.

Provider credentials should be validated without exposing the secret in
error messages.
