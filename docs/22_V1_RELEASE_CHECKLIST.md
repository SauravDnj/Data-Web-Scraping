# V1 Release Checklist

## Product

-   [ ] Project creation works
-   [ ] Configuration validation works
-   [ ] Job creation works
-   [ ] Job execution works
-   [ ] Records display correctly
-   [ ] Search/filter works
-   [ ] CSV export works
-   [ ] JSON export works
-   [ ] Retry works
-   [ ] Audit events exist

## Database

-   [ ] Fresh migration works
-   [ ] Upgrade migration works
-   [ ] Indexes verified
-   [ ] Backup tested
-   [ ] Restore tested

## Security

-   [ ] No secrets in Git
-   [ ] Provider keys protected
-   [ ] Authorization tested
-   [ ] Export authorization tested
-   [ ] Logs redacted
-   [ ] Dependencies reviewed

## Reliability

-   [ ] Worker crash recovery tested
-   [ ] Retry limits tested
-   [ ] Cancellation tested
-   [ ] Provider errors classified
-   [ ] Quota/usage guard tested

## Frontend

-   [ ] Loading states
-   [ ] Empty states
-   [ ] Error states
-   [ ] Form validation
-   [ ] Accessibility basics
-   [ ] No credential leakage

## Documentation

-   [ ] README
-   [ ] Local setup
-   [ ] Architecture
-   [ ] Database
-   [ ] API
-   [ ] Operations
-   [ ] Known limitations
-   [ ] Current provider compliance notes

## Release gate

V1 cannot be declared complete until all mandatory items above are
verified.
