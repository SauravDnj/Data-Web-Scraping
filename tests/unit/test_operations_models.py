"""T026 tests: exports tracked independently, schedule enable/disable,
and audit records identifying actor/action/entity — against SQLite
in-memory (see tests/unit/test_db_session.py)."""

from datetime import UTC, datetime, timedelta

from app.core.security import hash_password, normalize_email
from app.db.models import AuditLog, Export, ExportStatus, Project, Schedule, User
from app.db.session import build_session_factory, session_scope


def _make_user_and_project(session, email: str = "owner@example.com"):
    user = User(
        email=normalize_email(email),
        password_hash=hash_password("correct horse battery staple"),
    )
    session.add(user)
    session.flush()

    project = Project(user_id=user.id, name="My Project", source_type="google_maps")
    session.add(project)
    session.flush()

    return user, project


def test_export_can_be_tracked_independently_of_a_job(sqlite_engine):
    """No job_id anywhere on Export — it's its own unit of work."""
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        user, project = _make_user_and_project(session)
        session.add(
            Export(
                project_id=project.id,
                requested_by=user.id,
                format="csv",
                filters_json={"status": "completed"},
            )
        )
        project_id = project.id

    with session_scope(factory) as session:
        export = session.query(Export).filter_by(project_id=project_id).one()
        assert export.status == ExportStatus.PENDING
        assert export.completed_at is None
        assert not hasattr(export, "job_id")


def test_export_lifecycle_to_completion(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        user, project = _make_user_and_project(session)
        export = Export(project_id=project.id, requested_by=user.id, format="json")
        session.add(export)
        session.flush()
        export_id = export.id

    with session_scope(factory) as session:
        export = session.query(Export).filter_by(id=export_id).one()
        export.status = ExportStatus.RUNNING

    with session_scope(factory) as session:
        export = session.query(Export).filter_by(id=export_id).one()
        export.status = ExportStatus.COMPLETED
        export.file_path = "/exports/example.json"
        export.completed_at = datetime.now(UTC)

    with session_scope(factory) as session:
        export = session.query(Export).filter_by(id=export_id).one()
        assert export.status == ExportStatus.COMPLETED
        assert export.file_path == "/exports/example.json"
        assert export.completed_at is not None


def test_schedule_can_be_enabled_and_disabled(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        _user, project = _make_user_and_project(session)
        session.add(
            Schedule(
                project_id=project.id,
                cron_expression="0 * * * *",
                timezone="UTC",
                next_run_at=datetime.now(UTC) + timedelta(hours=1),
            )
        )
        project_id = project.id

    with session_scope(factory) as session:
        schedule = session.query(Schedule).filter_by(project_id=project_id).one()
        assert schedule.enabled is True
        schedule.enabled = False

    with session_scope(factory) as session:
        schedule = session.query(Schedule).filter_by(project_id=project_id).one()
        assert schedule.enabled is False


def test_audit_log_identifies_actor_action_and_entity(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        user, project = _make_user_and_project(session)
        session.add(
            AuditLog(
                user_id=user.id,
                action="project.created",
                entity_type="project",
                entity_id=project.id,
                details_json={"name": project.name},
            )
        )
        user_id = user.id

    with session_scope(factory) as session:
        entry = session.query(AuditLog).filter_by(user_id=user_id).one()
        assert entry.action == "project.created"
        assert entry.entity_type == "project"
        assert entry.entity_id is not None


def test_audit_log_allows_system_initiated_actions_without_a_user(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        session.add(
            AuditLog(
                user_id=None,
                action="job.recovered",
                entity_type="job",
                entity_id=42,
                details_json={"reason": "stale heartbeat"},
            )
        )

    with session_scope(factory) as session:
        entry = session.query(AuditLog).filter_by(action="job.recovered").one()
        assert entry.user_id is None
