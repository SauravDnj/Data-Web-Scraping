# Google Provider Workflow

## Purpose

This document defines how the application should integrate Google Maps
Platform as a provider without mixing provider code into the core
application.

## Provider interface

Conceptually:

``` python
class GoogleMapsProvider:
    def validate(self, config): ...
    def estimate(self, config): ...
    def collect(self, config): ...
    def normalize(self, response): ...
    def classify_error(self, error): ...
```

## Configuration

Provider configuration must be explicit.

Example conceptual configuration:

``` json
{
  "query": "restaurants",
  "location": {
    "latitude": 21.1702,
    "longitude": 72.8311
  },
  "radius_meters": 10000,
  "fields": [
    "name",
    "address",
    "rating"
  ],
  "max_results": 100
}
```

The exact fields and limits must be implemented according to the
selected current Google Maps Platform product/API.

## Provider call lifecycle

``` text
config
 ↓
validate
 ↓
estimate usage
 ↓
check application budget
 ↓
send approved request
 ↓
receive response
 ↓
classify response
 ↓
normalize
```

## Errors

Provider errors should be mapped into application categories:

``` text
authentication
quota
rate
invalid_request
temporary
permanent
unknown
```

## Important rule

If a provider denies a request because of a quota, rate, authorization,
or policy condition, the worker must not attempt to bypass that
restriction.

It should:

``` text
stop/backoff
 ↓
record reason
 ↓
update job
 ↓
tell user
```

## Browser automation

Playwright must not be the default mechanism for Google Maps Platform
access.

Use the documented API/product integration where the selected Google
product requires it.

If browser automation is used for another permitted source, it must live
in a separate provider adapter.

## Future provider support

Later:

``` text
ProviderRegistry
  ├── GoogleMapsProvider
  ├── GoogleSearchProvider
  └── OtherProvider
```

The job service chooses a provider by configuration.
