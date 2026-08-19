"""Data pipeline stages (docs/08_DATA_PIPELINE_DEEP.md), applied after
a provider's own response mapping (e.g.
app.providers.google_maps.mapper) — provider-agnostic, reusable by any
current or future provider's output. `normalize.py` is Stage 3
(T050); `validate.py` (Stage 2/4, T051) and `deduplicate.py`
(Stage 6, T053) land in later tasks."""
