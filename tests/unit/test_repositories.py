"""T032 tests: one repository per entity, proving create/get, each
entity-specific query, and that pagination works — all through the
domain-object interface, never touching SQLAlchemy row types in the
assertions (proving the acceptance criterion: services can use
repositories without knowing SQLAlchemy implementation details)."""

from datetime import timedelta

import pytest
from app.db.session import session_scope
from app.domain.audit import AuditLogEntry
from app.domain.exports import Export, ExportStatus
from app.domain.job_state_machine import InvalidJobTransition
from app.domain.jobs import Job, JobRun, JobStatus
from app.domain.projects import CollectionConfig, Project
from app.domain.records import Record, RecordProvenance
from app.domain.schedules import Schedule
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.repositories.configs import SqlAlchemyCollectionConfigRepository
from app.repositories.exports import SqlAlchemyExportRepository
from app.repositories.jobs import SqlAlchemyJobRepository
from app.repositories.projects import SqlAlchemyProjectRepository
from app.repositories.records import SqlAlchemyRecordRepository
from app.repositories.schedules import SqlAlchemyScheduleRepository

from tests.unit.factories import (
    make_config,
    make_job,
    make_project,
    make_user,
    make_user_project_config,
    utc_now,
)

# --- projects -----------------------------------------------------


def test_project_repository_create_and_get(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        repo = SqlAlchemyProjectRepository(session)

        created = repo.create(
            Project(
                id=None, user_id=user.id, name="My Project", source_type="google_maps"
            )
        )
        assert created.id is not None

        fetched = repo.get(created.id)
        assert isinstance(fetched, Project)
        assert fetched.name == "My Project"


def test_project_repository_list_for_user_paginates(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        repo = SqlAlchemyProjectRepository(session)
        for i in range(3):
            repo.create(
                Project(
                    id=None,
                    user_id=user.id,
                    name=f"Project {i}",
                    source_type="google_maps",
                )
            )

        page = repo.list_for_user(user.id, limit=2, offset=0)
        assert page.total == 3
        assert len(page.items) == 2
        assert page.limit == 2


# --- collection configs --------------------------------------------


def test_config_repository_get_active_for_project(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        repo = SqlAlchemyCollectionConfigRepository(session)

        repo.create(
            CollectionConfig(
                id=None,
                project_id=project.id,
                provider="google_maps",
                config={"v": 1},
                version=1,
                is_active=False,
            )
        )
        repo.create(
            CollectionConfig(
                id=None,
                project_id=project.id,
                provider="google_maps",
                config={"v": 2},
                version=2,
                is_active=True,
            )
        )

        active = repo.get_active_for_project(project.id)
        assert active is not None
        assert active.version == 2


def test_config_repository_get_active_returns_none_when_no_active_config(
    session_factory,
):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        repo = SqlAlchemyCollectionConfigRepository(session)

        assert repo.get_active_for_project(project.id) is None


# --- jobs ------------------------------------------------------------


def test_job_repository_create_and_get(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        repo = SqlAlchemyJobRepository(session)

        created = repo.create(Job(id=None, project_id=project.id, config_id=config.id))
        assert created.status == JobStatus.DRAFT

        fetched = repo.get(created.id)
        assert isinstance(fetched, Job)


def test_job_repository_update_status_uses_the_state_machine(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        repo = SqlAlchemyJobRepository(session)
        job = repo.create(Job(id=None, project_id=project.id, config_id=config.id))

        updated = repo.update_status(job.id, JobStatus.QUEUED)
        assert updated.status == JobStatus.QUEUED

        # DRAFT -> RUNNING is illegal even after being queued once
        # already moved past draft; jump straight to an illegal target
        # to prove the repository actually enforces the state machine
        # rather than writing whatever status it's given.
        with pytest.raises(InvalidJobTransition):
            repo.update_status(job.id, JobStatus.COMPLETED)


def test_job_repository_list_queued_or_running_is_project_agnostic(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        repo = SqlAlchemyJobRepository(session)
        job = repo.create(Job(id=None, project_id=project.id, config_id=config.id))
        repo.update_status(job.id, JobStatus.QUEUED)

        page = repo.list_queued_or_running()
        assert any(j.id == job.id for j in page.items)


def test_job_repository_create_run_and_list_runs(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        repo = SqlAlchemyJobRepository(session)
        job = repo.create(Job(id=None, project_id=project.id, config_id=config.id))

        repo.create_run(JobRun(id=None, job_id=job.id, worker_id="worker-1", attempt=1))
        repo.create_run(JobRun(id=None, job_id=job.id, worker_id="worker-2", attempt=2))

        runs = repo.list_runs_for_job(job.id)
        assert [r.attempt for r in runs] == [1, 2]


def test_job_repository_list_for_user_is_cross_project_but_scoped_to_the_user(
    session_factory,
):
    with session_scope(session_factory) as session:
        owner = make_user(session, email="owner@example.com")
        stranger = make_user(session, email="stranger@example.com")
        repo = SqlAlchemyJobRepository(session)

        project_a = make_project(session, owner.id, name="Project A")
        config_a = make_config(session, project_a.id)
        project_b = make_project(session, owner.id, name="Project B")
        config_b = make_config(session, project_b.id)
        job_in_a = repo.create(
            Job(id=None, project_id=project_a.id, config_id=config_a.id)
        )
        job_in_b = repo.create(
            Job(id=None, project_id=project_b.id, config_id=config_b.id)
        )

        stranger_project = make_project(session, stranger.id, name="Stranger Project")
        stranger_config = make_config(session, stranger_project.id)
        repo.create(
            Job(id=None, project_id=stranger_project.id, config_id=stranger_config.id)
        )

        page = repo.list_for_user(owner.id)
        assert {job.id for job in page.items} == {job_in_a.id, job_in_b.id}
        assert page.total == 2


def test_job_repository_list_for_user_filters_by_status(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        repo = SqlAlchemyJobRepository(session)
        job = repo.create(Job(id=None, project_id=project.id, config_id=config.id))
        repo.update_status(job.id, JobStatus.QUEUED)

        matching = repo.list_for_user(_user.id, status=JobStatus.QUEUED)
        assert [j.id for j in matching.items] == [job.id]

        not_matching = repo.list_for_user(_user.id, status=JobStatus.FAILED)
        assert not_matching.items == []


def test_job_repository_count_by_status_for_user(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        repo = SqlAlchemyJobRepository(session)
        first = repo.create(Job(id=None, project_id=project.id, config_id=config.id))
        second = repo.create(Job(id=None, project_id=project.id, config_id=config.id))
        repo.update_status(first.id, JobStatus.QUEUED)
        repo.update_status(second.id, JobStatus.QUEUED)
        repo.update_status(second.id, JobStatus.RUNNING)

        counts = repo.count_by_status_for_user(_user.id)

        assert counts[JobStatus.QUEUED] == 1
        assert counts[JobStatus.RUNNING] == 1
        assert JobStatus.FAILED not in counts


# --- records -----------------------------------------------------------


def test_record_repository_create_and_get_by_canonical_key(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repo = SqlAlchemyRecordRepository(session)

        repo.create(
            Record(
                id=None,
                project_id=project.id,
                job_id=job.id,
                provider="google_maps",
                canonical_key="google_maps:places/abc123",
                data={"name": "Example Cafe"},
                collected_at=utc_now(),
            )
        )

        found = repo.get_by_canonical_key(project.id, "google_maps:places/abc123")
        assert found is not None
        assert found.data["name"] == "Example Cafe"

        assert repo.get_by_canonical_key(project.id, "does-not-exist") is None


def test_record_repository_add_provenance(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repo = SqlAlchemyRecordRepository(session)

        record = repo.create(
            Record(
                id=None,
                project_id=project.id,
                job_id=job.id,
                provider="google_maps",
                canonical_key="google_maps:places/abc123",
                data={},
                collected_at=utc_now(),
            )
        )
        provenance = repo.add_provenance(
            RecordProvenance(
                id=None,
                record_id=record.id,
                provider_operation="places.details",
                collected_at=utc_now(),
            )
        )
        assert provenance.id is not None
        assert provenance.record_id == record.id


def test_record_repository_count_for_user_is_cross_project_but_scoped(
    session_factory,
):
    with session_scope(session_factory) as session:
        owner = make_user(session, email="owner@example.com")
        stranger = make_user(session, email="stranger@example.com")
        repo = SqlAlchemyRecordRepository(session)

        project_a = make_project(session, owner.id, name="Project A")
        config_a = make_config(session, project_a.id)
        job_a = make_job(session, project_a.id, config_a.id)
        project_b = make_project(session, owner.id, name="Project B")
        config_b = make_config(session, project_b.id)
        job_b = make_job(session, project_b.id, config_b.id)

        for project, job, key in (
            (project_a, job_a, "google_maps:places/a1"),
            (project_a, job_a, "google_maps:places/a2"),
            (project_b, job_b, "google_maps:places/b1"),
        ):
            repo.create(
                Record(
                    id=None,
                    project_id=project.id,
                    job_id=job.id,
                    provider="google_maps",
                    canonical_key=key,
                    data={},
                    collected_at=utc_now(),
                )
            )

        stranger_project = make_project(session, stranger.id, name="Stranger Project")
        stranger_config = make_config(session, stranger_project.id)
        stranger_job = make_job(session, stranger_project.id, stranger_config.id)
        repo.create(
            Record(
                id=None,
                project_id=stranger_project.id,
                job_id=stranger_job.id,
                provider="google_maps",
                canonical_key="google_maps:places/s1",
                data={},
                collected_at=utc_now(),
            )
        )

        assert repo.count_for_user(owner.id) == 3
        assert repo.count_for_user(stranger.id) == 1


# --- exports ----------------------------------------------------------


def test_export_repository_create_and_update_status(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        repo = SqlAlchemyExportRepository(session)

        export = repo.create(
            Export(id=None, project_id=project.id, requested_by=user.id, format="csv")
        )
        assert export.status == ExportStatus.PENDING

        updated = repo.update_status(
            export.id, ExportStatus.COMPLETED, file_path="/exports/x.csv"
        )
        assert updated.status == ExportStatus.COMPLETED
        assert updated.file_path == "/exports/x.csv"


# --- schedules --------------------------------------------------------


def test_schedule_repository_list_due(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        repo = SqlAlchemyScheduleRepository(session)

        due = repo.create(
            Schedule(
                id=None,
                project_id=project.id,
                cron_expression="0 * * * *",
                next_run_at=utc_now() - timedelta(minutes=1),
            )
        )
        repo.create(
            Schedule(
                id=None,
                project_id=project.id,
                cron_expression="0 * * * *",
                next_run_at=utc_now() + timedelta(hours=1),
            )
        )

        page = repo.list_due(utc_now())
        assert [s.id for s in page.items] == [due.id]


def test_schedule_repository_set_enabled(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        repo = SqlAlchemyScheduleRepository(session)

        schedule = repo.create(
            Schedule(
                id=None,
                project_id=project.id,
                cron_expression="0 * * * *",
                next_run_at=utc_now(),
            )
        )
        updated = repo.set_enabled(schedule.id, False)
        assert updated.enabled is False


# --- audit --------------------------------------------------------------


def test_audit_repository_create_and_list_for_user(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        repo = SqlAlchemyAuditLogRepository(session)

        repo.create(
            AuditLogEntry(
                id=None,
                user_id=user.id,
                action="project.created",
                entity_type="project",
                entity_id=1,
            )
        )

        page = repo.list_for_user(user.id)
        assert page.total == 1
        assert page.items[0].action == "project.created"
