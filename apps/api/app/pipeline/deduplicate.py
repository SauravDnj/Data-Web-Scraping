"""Stage 6 ("Deduplication") of docs/08_DATA_PIPELINE_DEEP.md (T053).
Two composable steps, kept separate rather than one large function
(matching every prior pipeline/provider task this session — T041/T042
config-validation-vs-HTTP-client, T050/T051 normalize-vs-validate):

1.  `deduplicate_within_batch()` — pure, no DB. Drops repeats *within*
    one collection run (items 1-2: within a page, and across pages —
    the same function handles both, since it consumes whatever
    `Iterable[RecordDraft]` the caller passes, and
    `GoogleMapsClient.search_text()`'s pagination is already one
    continuous lazy generator by the time it reaches here, not
    materialized per page).
2.  `resolve_against_existing()` — DB-touching (item 3: compare
    against existing project records, via `RecordRepository.
    get_by_canonical_key`, T032). One record in, one decision out.

`deduplicate_batch()` composes both plus tracks duplicate counts
(item 6)."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import StrEnum

from app.domain.records import Record, RecordDraft
from app.pipeline.canonical_identity import compute_canonical_key
from app.repositories.records import RecordRepository


class DedupAction(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    SKIPPED_EXISTING = "skipped_existing"
    SKIPPED_DUPLICATE_IN_BATCH = "skipped_duplicate_in_batch"


@dataclass(frozen=True)
class DedupOutcome:
    canonical_key: str
    action: DedupAction
    record: Record | None = None  # set for CREATED/UPDATED only


@dataclass
class DedupSummary:
    """Duplicate counts (T053 item 6) — a plain mutable accumulator,
    not a domain object; the worker (T060+) is expected to fold these
    into `Job`/`JobRun` metrics (`docs/09_JOB_QUEUE_WORKER_DEEP.md`'s
    `records_created`/`records_updated`, plus the two counts that doc
    doesn't name but T053 needs: duplicates seen within one batch, and
    existing records left untouched by a skip policy)."""

    created: int = 0
    updated: int = 0
    skipped_existing: int = 0
    duplicates_in_batch: int = 0

    def record(self, action: DedupAction) -> None:
        match action:
            case DedupAction.CREATED:
                self.created += 1
            case DedupAction.UPDATED:
                self.updated += 1
            case DedupAction.SKIPPED_EXISTING:
                self.skipped_existing += 1
            case DedupAction.SKIPPED_DUPLICATE_IN_BATCH:
                self.duplicates_in_batch += 1


def deduplicate_within_batch(
    drafts: Iterable[RecordDraft],
) -> Iterator[tuple[RecordDraft, str, bool]]:
    """Yields `(draft, canonical_key, is_duplicate)` for EVERY draft,
    in order — `is_duplicate=True` for the second and later occurrence
    of a canonical key (same page or a later one; streaming, a `seen`
    set that lives for the whole call, not reset per page, so this
    dedups across however many pages the caller's iterable spans).
    Yielding every item (not just first-occurrences) lets a caller
    tally duplicate counts (item 6) in one pass, without needing a
    second one just to count what got dropped."""
    seen: set[str] = set()
    for draft in drafts:
        key = compute_canonical_key(draft)
        is_duplicate = key in seen
        if not is_duplicate:
            seen.add(key)
        yield draft, key, is_duplicate


def resolve_against_existing(
    draft: RecordDraft,
    canonical_key: str,
    repository: RecordRepository,
    *,
    update_existing: bool,
) -> DedupOutcome:
    """One record's create/update/skip decision (item 3: compare
    against existing project records; item 5: update-vs-skip policy).

    **Update-vs-skip, a deliberate default**: `update_existing=True`
    means a repeat collection of the same real-world entity refreshes
    its `data`/`collected_at` — chosen as the default because
    provider data genuinely goes stale (ratings, hours, business
    status change), and a data *collection* product whose records
    never refresh would be of limited use. `update_existing=False`
    (skip) is equally supported, not hypothetical — a caller that
    wants "first collection wins, never touched again" passes it
    explicitly; this function doesn't hardcode one policy as the only
    option."""
    existing = repository.get_by_canonical_key(draft.project_id, canonical_key)

    if existing is None:
        record = repository.create(
            Record(
                id=None,
                project_id=draft.project_id,
                job_id=draft.job_id,
                provider=draft.provider,
                canonical_key=canonical_key,
                data=draft.data,
                collected_at=draft.collected_at,
                provider_record_id=draft.provider_record_id,
            )
        )
        return DedupOutcome(canonical_key, DedupAction.CREATED, record)

    if not update_existing:
        return DedupOutcome(canonical_key, DedupAction.SKIPPED_EXISTING, existing)

    assert existing.id is not None  # always set for a persisted Record
    updated = repository.update_collected_data(
        existing.id,
        job_id=draft.job_id,
        data=draft.data,
        collected_at=draft.collected_at,
    )
    return DedupOutcome(canonical_key, DedupAction.UPDATED, updated)


def deduplicate_batch(
    drafts: Iterable[RecordDraft],
    repository: RecordRepository,
    *,
    update_existing: bool = True,
) -> tuple[list[DedupOutcome], DedupSummary]:
    """Composes `deduplicate_within_batch()` +
    `resolve_against_existing()` and accumulates `DedupSummary`. This
    is what a caller (the worker, T060+) actually calls — the two
    functions above stay independently usable/testable."""
    summary = DedupSummary()
    outcomes: list[DedupOutcome] = []

    for draft, canonical_key, is_duplicate in deduplicate_within_batch(drafts):
        if is_duplicate:
            outcome = DedupOutcome(
                canonical_key, DedupAction.SKIPPED_DUPLICATE_IN_BATCH
            )
        else:
            outcome = resolve_against_existing(
                draft, canonical_key, repository, update_existing=update_existing
            )
        outcomes.append(outcome)
        summary.record(outcome.action)

    return outcomes, summary
