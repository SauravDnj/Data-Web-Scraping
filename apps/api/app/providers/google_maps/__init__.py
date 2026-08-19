"""Google Maps Platform provider adapter (T041+). Only
`app.providers.google_maps.config` exists so far (T041 — configuration
validation only, no network call). The full `ProviderAdapter`
(estimate/collect/normalize/classify_error/health_check) needs the
HTTP client T042 builds; assembling a class that satisfies the whole
Protocol belongs there, not here — see
`app.providers.google_maps.config`'s module docstring."""
