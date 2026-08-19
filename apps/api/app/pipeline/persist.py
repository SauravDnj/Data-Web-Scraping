"""Stage 7 ("Persistence") of docs/08_DATA_PIPELINE_DEEP.md (T054) —
wraps each of T053's per-record dedup decisions in its own SAVEPOINT
(`session.begin_nested()`), so one record's failure (a database
constraint conflict, item 6 — e.g. a concurrent insert that slipped in
between this record's `get_by_canonical_key` check and its own
`create()`) rolls back only *that* record, never the rest of the batch
already written earlier in the same outer transaction. This is the
literal meaning of T054's acceptance criterion, "a failed transaction
does not leave partial inconsistent state," applied at record
granularity — not "the whole batch is all-or-nothing" (that would
contradict docs/08's "never hide failures" principle: a batch of 500
where 50 fail should report 450 real successes and 50 real failures,
`status = partially_completed`, not discard the 450 just because 50
had a problem).

**Counters (item 5) are only incremented after a record's SAVEPOINT
actually releases successfully** — never optimistically before. This
is the bug T053's plain `DedupSummary` had no protection against on
its own: `resolve_against_existing()` calls `repository.create()`,
which only `flush()`es (not commits) — if a *later* record in the same
outer transaction failed and the whole `session_scope()` rolled back
without this module's SAVEPOINT isolation, T053's counters would have
already claimed successes that the rollback undid. The SAVEPOINT is
what makes each record's own success durable *within* the still-open
outer transaction, independent of what happens to later records.

**Provenance (item 3)**: only recorded for an actual write (CREATED/
UPDATED) — a SKIPPED_EXISTING or SKIPPED_DUPLICATE_IN_BATCH outcome
touched no data, so there is nothing to attach provenance to.
`provider_operation` is caller-supplied (e.g.
`app.providers.google_maps.mapper.GOOGLE_MAPS_TEXT_SEARCH_OPERATION`)
— this module has no Google-specific import anywhere, same
provider-agnostic principle as every other `app.pipeline` module."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.records import RecordDraft, RecordProvenance
from app.pipeline.deduplicate import (
    DedupAction,
    deduplicate_within_batch,
    resolve_against_existing,
)
from app.repositories.records import RecordRepository


class PersistAction(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    SKIPPED_EXISTING = "skipped_existing"
    SKIPPED_DUPLICATE_IN_BATCH = "skipped_duplicate_in_batch"
    FAILED = "failed"


_DEDUP_TO_PERSIST_ACTION: dict[DedupAction, PersistAction] = {
    DedupAction.CREATED: PersistAction.CREATED,
    DedupAction.UPDATED: PersistAction.UPDATED,
    DedupAction.SKIPPED_EXISTING: PersistAction.SKIPPED_EXISTING,
    DedupAction.SKIPPED_DUPLICATE_IN_BATCH: PersistAction.SKIPPED_DUPLICATE_IN_BATCH,
}


@dataclass(frozen=True)
class PersistOutcome:
    canonical_key: str
    action: PersistAction
    record_id: int | None = None
    error: str | None = None


@dataclass
class PersistSummary:
    created: int = 0
    updated: int = 0
    skipped_existing: int = 0
    duplicates_in_batch: int = 0
    failed: int = 0

    def record(self, action: PersistAction) -> None:
        match action:
            case PersistAction.CREATED:
                self.created += 1
            case PersistAction.UPDATED:
                self.updated += 1
            case PersistAction.SKIPPED_EXISTING:
                self.skipped_existing += 1
            case PersistAction.SKIPPED_DUPLICATE_IN_BATCH:
                self.duplicates_in_batch += 1
            case PersistAction.FAILED:
                self.failed += 1


def persist_batch(
    session: Session,
    drafts: Iterable[RecordDraft],
    repository: RecordRepository,
    *,
    provider_operation: str,
    update_existing: bool = True,
) -> tuple[list[PersistOutcome], PersistSummary]:
    """The caller (the worker, T060+) owns the outer transaction
    (`session_scope()`, T020) — this function never commits or rolls
    back that outer transaction itself, only the per-record SAVEPOINTs
    nested inside it."""
    summary = PersistSummary()
    outcomes: list[PersistOutcome] = []

    for draft, canonical_key, is_duplicate in deduplicate_within_batch(drafts):
        if is_duplicate:
            outcome = PersistOutcome(
                canonical_key, PersistAction.SKIPPED_DUPLICATE_IN_BATCH
            )
        else:
            outcome = _persist_one(
                session,
                draft,
                canonical_key,
                repository,
                provider_operation=provider_operation,
                update_existing=update_existing,
            )
        outcomes.append(outcome)
        summary.record(outcome.action)

    return outcomes, summary


def _persist_one(
    session: Session,
    draft: RecordDraft,
    canonical_key: str,
    repository: RecordRepository,
    *,
    provider_operation: str,
    update_existing: bool,
) -> PersistOutcome:
    try:
        with session.begin_nested():
            dedup_outcome = resolve_against_existing(
                draft, canonical_key, repository, update_existing=update_existing
            )
            if dedup_outcome.action in (DedupAction.CREATED, DedupAction.UPDATED):
                assert dedup_outcome.record is not None
                assert dedup_outcome.record.id is not None
                repository.add_provenance(
                    RecordProvenance(
                        id=None,
                        record_id=dedup_outcome.record.id,
                        provider_operation=provider_operation,
                        collected_at=draft.collected_at,
                        source_reference=None,
                        metadata={},
                    )
                )
    except IntegrityError as exc:
        # The SAVEPOINT above has already been rolled back by the
        # `with` block's own exception handling — the outer
        # transaction, and every sibling record already persisted
        # within it, is untouched.
        return PersistOutcome(canonical_key, PersistAction.FAILED, error=str(exc))

    action = _DEDUP_TO_PERSIST_ACTION[dedup_outcome.action]
    record_id = dedup_outcome.record.id if dedup_outcome.record is not None else None
    return PersistOutcome(canonical_key, action, record_id=record_id)
