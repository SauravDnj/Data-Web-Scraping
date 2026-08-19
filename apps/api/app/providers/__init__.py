"""Provider adapters — external provider communication (T040+). See
app.providers.base.ProviderAdapter for the generic contract every
concrete adapter (e.g. a future GoogleMapsProvider, T041-T044) must
satisfy. Nothing in this package may import a provider SDK or browser
automation library at the base-contract level — those belong only
inside a concrete adapter's own subpackage
(docs/24_BACKEND_FILE_PLAN.md: app/providers/google_maps/)."""
