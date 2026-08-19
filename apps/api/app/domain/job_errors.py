"""Interim job failure-class retryability rules.

T044 ("Provider error mapping") will define the authoritative failure
taxonomy and retryability classification for real provider errors —
this is deliberately a small, clearly-provisional set (matching the
class names from docs/01_SYSTEM_EXPLANATION.md's taxonomy) so T035's
retry command has something concrete to gate on now. T044 should
reconcile with or replace this, not silently diverge from it."""

RETRYABLE_ERROR_CLASSES = frozenset({"transient_network", "rate_limit", "persistence"})


def is_retryable(error_code: str | None) -> bool:
    return error_code in RETRYABLE_ERROR_CLASSES
