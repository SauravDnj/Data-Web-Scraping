"""Stage 5 ("Canonical identity") of docs/08_DATA_PIPELINE_DEEP.md
(T052) — computes `Record.canonical_key` for a `RecordDraft`
(T043/T050/T051's output). Pure, deterministic, no I/O.

**Project scope is deliberately NOT embedded in the returned string.**
T000's resolved design decision (docs/16_MEMORY.md) was "canonical key
= project_scope + provider + provider_id" as a *concept* — but the
actual schema (`records`, T025) already scopes uniqueness with a
*composite* constraint, `UniqueConstraint(project_id, canonical_key)`
(`app/db/models/record.py`), so `project_id` doesn't need to be part
of this string too; the same literal `canonical_key` is intentionally
allowed to repeat across different projects (T025's own
cross-project-dedup-scope test proves this). **`provider` IS embedded
here**, precisely because the DB constraint has no separate `provider`
dimension — without it, two different providers coincidentally
producing the same raw identifier would collide within one project.

**Preference order (T052 item 1, DO NOT list: "never use business
name alone as identity")**:

1.  The provider's own stable identifier (`RecordDraft.
    provider_record_id` — Google's place `id`, storage/reuse
    explicitly permitted per `database/DATABASE_DEEP.md`'s "prefer it
    if permitted" guidance) — used whenever present, no exceptions.
2.  A fallback built from `data["name"]` + `data["formatted_address"]`
    together (never name alone) — **only** when no provider identifier
    exists at all.

**Known collision limitations of the fallback (T052 item 9,
documented rather than solved — no fallback heuristic can be
perfect)**:

-   **False merge**: two genuinely different businesses sharing one
    building's address (e.g. two shops in the same mall/plaza with an
    address that resolves to the same string, and coincidentally
    identical names) would collide onto the same key. Rare in
    practice since names usually differ, but not impossible.
-   **False split**: the same real business, collected with an address
    string that differs by more than whitespace/case (e.g. "St" vs.
    "Street", a suite/unit number present in one collection and absent
    in another) will NOT be recognized as identical and will get a
    different key, appearing as two separate records. Only
    whitespace/case/Unicode-composition differences are normalized
    away here — no abbreviation expansion, no fuzzy matching.
-   This is exactly why the provider identifier is always preferred
    when available: it has none of these failure modes."""

import hashlib
import re
import unicodedata

from app.domain.records import RecordDraft


class CanonicalIdentityError(ValueError):
    """Raised when a record has no provider identifier AND no usable
    name/address pair to fall back to — by the time Stage 5 runs, a
    record this incomplete should already have been REJECTED at Stage
    4 (T051) and never reached here; this is a defensive guard against
    a pipeline-ordering bug, not an expected runtime path."""


def compute_canonical_key(record: RecordDraft) -> str:
    if record.provider_record_id:
        return f"{record.provider}:{record.provider_record_id}"
    return _fallback_canonical_key(record)


def _fallback_canonical_key(record: RecordDraft) -> str:
    name = record.data.get("name")
    address = record.data.get("formatted_address")
    if (
        not isinstance(name, str)
        or not name.strip()
        or not isinstance(address, str)
        or not address.strip()
    ):
        raise CanonicalIdentityError(
            "Cannot compute a fallback canonical key: record has no "
            "provider_record_id and is missing a usable name/"
            "formatted_address pair."
        )

    identity_input = (
        f"{_normalize_identity_text(name)}|{_normalize_identity_text(address)}"
    )
    # Hashed, not embedded verbatim: canonical_key is String(512)
    # (app/db/models/record.py) and a raw long name+address pair could
    # exceed that; truncating the text instead would risk two
    # different long addresses colliding on a shared prefix. A
    # fixed-length hash of the *normalized* input is still fully
    # deterministic (same input -> same key) and collision-free for
    # all practical purposes.
    digest = hashlib.sha256(identity_input.encode("utf-8")).hexdigest()
    return f"{record.provider}:fallback:{digest}"


def _normalize_identity_text(text: str) -> str:
    """More aggressive than T050's `FieldKind.TEXT` (trim + NFC only,
    case preserved) on purpose — this is never shown to a user, only
    compared, so case and internal whitespace differences that would
    matter for *display* must NOT matter for *identity*."""
    composed = unicodedata.normalize("NFC", text).strip().lower()
    return re.sub(r"\s+", " ", composed)
