# Security and Compliance

## Security baseline

-   keep secrets in environment variables or a proper secret manager;
-   hash user passwords with a modern password hashing algorithm;
-   use HTTPS in production;
-   validate all API inputs;
-   use parameterized database operations through the ORM;
-   apply authorization checks to every project resource;
-   protect exports;
-   limit log access;
-   rotate credentials;
-   keep dependencies updated.

## Google-specific safety

Do not implement:

-   CAPTCHA solving to defeat access controls;
-   fingerprint/stealth evasion;
-   proxy rotation intended to circumvent restrictions;
-   fake accounts;
-   automated bypass of authentication;
-   hidden rate-limit evasion.

Use official APIs/products where required and follow their current terms
and documentation.

## Privacy

The platform should minimize personal data.

Avoid collecting:

-   private contact information;
-   authentication credentials;
-   sensitive personal information;
-   data from restricted/private pages.

Provide retention controls and deletion capabilities.

## Audit

Audit:

-   login events;
-   project creation/change;
-   configuration changes;
-   job actions;
-   exports;
-   credential changes;
-   administrative actions.

## Threat model

Consider:

-   stolen provider key;
-   malicious project configuration;
-   SQL injection;
-   XSS;
-   CSRF where relevant;
-   unauthorized record access;
-   export abuse;
-   job flooding;
-   worker compromise;
-   dependency vulnerabilities.

## Secret redaction

Logs must redact:

``` text
API keys
Authorization headers
Passwords
Cookies
Session tokens
Database passwords
```

## Compliance gate

Every new collector must document:

1.  source;
2.  access method;
3.  allowed use;
4.  data fields;
5.  retention;
6.  export/distribution policy;
7.  rate/usage limits;
8.  failure behavior.
