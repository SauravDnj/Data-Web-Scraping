"""T030 tests: domain models are usable and validated without any
database — no fixtures here touch SQLite or SQLAlchemy at all, proving
domain logic really is DB-independent."""

from datetime import UTC, datetime

import pytest

from app.db.models import (
    ExportStatus as OrmExportStatus,
)
from app.db.models import (
    JobRunStatus as OrmJobRunStatus,
)
from app.db.models import (
    JobStatus as OrmJobStatus,
)
from app.db.models import (
    ProjectStatus as OrmProjectStatus,
)
from app.domain.exports import Export, ExportStatus
from app.domain.jobs import Job, JobCounters, JobRun, JobRunStatus, JobStatus
from app.domain.projects import CollectionConfig, Project, ProjectStatus
from app.domain.records import Record, RecordProvenance
from app.domain.schedules import Schedule


def test_status_enums_are_centralized_not_duplicated():
    """app.db.models re-exports the exact same enum objects from
    app.domain — not a second, parallel definition."""
    assert OrmProjectStatus is ProjectStatus
    assert OrmJobStatus is JobStatus
    assert OrmJobRunStatus is JobRunStatus
    assert OrmExportStatus is ExportStatus


def test_project_rejects_empty_name():
    with pytest.raises(ValueError, match="name"):
        Project(id=None, user_id=1, name="   ", source_type="google_maps")


def test_project_defaults_to_active_status():
    project = Project(id=None, user_id=1, name="My Project", source_type="google_maps")
    assert project.status == ProjectStatus.ACTIVE


def test_collection_config_rejects_version_below_one():
    with pytest.raises(ValueError, match="version"):
        CollectionConfig(
            id=None, project_id=1, provider="google_maps", config={}, version=0
        )


def test_collection_config_holds_arbitrary_provider_config():
    """No provider-specific fields modeled here — config is opaque."""
    config = CollectionConfig(
        id=None,
        project_id=1,
        provider="google_maps",
        config={"query": "coffee shops", "radius_m": 500, "anything": [1, 2, 3]},
        version=1,
    )
    assert config.config["anything"] == [1, 2, 3]


def test_job_counters_reject_negative_values():
    with pytest.raises(ValueError, match="must not be negative"):
        JobCounters(successful_units=-1)


def test_job_counters_default_to_zero():
    counters = JobCounters()
    assert counters.total_units == 0
    assert counters.records_rejected == 0


def test_job_defaults_to_draft_status():
    job = Job(id=None, project_id=1, config_id=1)
    assert job.status == JobStatus.DRAFT
    assert job.counters == JobCounters()


def test_job_run_rejects_attempt_below_one():
    with pytest.raises(ValueError, match="attempt"):
        JobRun(id=None, job_id=1, worker_id="worker-1", attempt=0)


def test_job_run_defaults_to_running_status_and_first_attempt():
    run = JobRun(id=None, job_id=1, worker_id="worker-1")
    assert run.status == JobRunStatus.RUNNING
    assert run.attempt == 1
    assert run.metrics == {}


def test_record_rejects_empty_canonical_key():
    with pytest.raises(ValueError, match="canonical_key"):
        Record(
            id=None,
            project_id=1,
            job_id=1,
            provider="google_maps",
            canonical_key="  ",
            data={},
            collected_at=datetime.now(UTC),
        )


def test_record_holds_arbitrary_provider_data():
    record = Record(
        id=None,
        project_id=1,
        job_id=1,
        provider="google_maps",
        canonical_key="google_maps:places/abc123",
        data={"name": "Example Cafe", "rating": 4.5},
        collected_at=datetime.now(UTC),
    )
    assert record.data["rating"] == 4.5


def test_record_provenance_defaults_metadata_to_empty_dict():
    provenance = RecordProvenance(
        id=None,
        record_id=1,
        provider_operation="places.details",
        collected_at=datetime.now(UTC),
    )
    assert provenance.metadata == {}


def test_export_defaults_to_pending_status_and_no_job_reference():
    export = Export(id=None, project_id=1, requested_by=1, format="csv")
    assert export.status == ExportStatus.PENDING
    assert not hasattr(export, "job_id")


def test_schedule_defaults_to_enabled_and_utc():
    schedule = Schedule(
        id=None,
        project_id=1,
        cron_expression="0 * * * *",
        next_run_at=datetime.now(UTC),
    )
    assert schedule.enabled is True
    assert schedule.timezone == "UTC"


def test_domain_objects_are_immutable():
    project = Project(id=None, user_id=1, name="My Project", source_type="google_maps")
    with pytest.raises(AttributeError):
        project.name = "Renamed"  # type: ignore[misc]
