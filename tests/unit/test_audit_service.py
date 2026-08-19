"""T037 tests: action names, secret redaction, and queryability —
against SQLite in-memory (see tests/unit/test_db_session.py)."""

from tests.unit.factories import make_user

from app.db.session import session_scope
from app.domain.audit_actions import AuditAction
from app.domain.audit_redaction import redact_details
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.services.audit import AuditService


def test_redact_details_scrubs_known_sensitive_keys():
    details = {
        "password": "hunter2",
        "api_key": "sk-abc123",
        "Authorization": "Bearer xyz",
        "name": "My Project",
    }
    redacted = redact_details(details)

    assert redacted["password"] == "[redacted]"
    assert redacted["api_key"] == "[redacted]"
    assert redacted["Authorization"] == "[redacted]"
    assert redacted["name"] == "My Project"  # untouched


def test_redact_details_is_recursive():
    details = {"config": {"provider_secret_token": "abc", "query": "coffee shops"}}
    redacted = redact_details(details)

    assert redacted["config"]["provider_secret_token"] == "[redacted]"
    assert redacted["config"]["query"] == "coffee shops"


def test_record_event_persists_redacted_details(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        audit = AuditService(SqlAlchemyAuditLogRepository(session))

        entry = audit.record_event(
            actor_user_id=user.id,
            action=AuditAction.PROJECT_CREATED,
            entity_type="project",
            entity_id=1,
            details={"name": "My Project", "password": "should-not-be-stored"},
        )

        assert entry.action == "project.created"
        assert entry.details["password"] == "[redacted]"
        assert entry.details["name"] == "My Project"


def test_record_event_uses_the_actual_action_value(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        audit = AuditService(SqlAlchemyAuditLogRepository(session))

        entry = audit.record_event(
            actor_user_id=user.id,
            action=AuditAction.JOB_RETRIED,
            entity_type="job",
            entity_id=42,
        )
        assert entry.action == "job.retried"
        assert entry.details == {}


def test_list_for_entity_returns_full_history_of_one_entity(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        audit = AuditService(SqlAlchemyAuditLogRepository(session))

        audit.record_event(
            actor_user_id=user.id,
            action=AuditAction.PROJECT_CREATED,
            entity_type="project",
            entity_id=7,
        )
        audit.record_event(
            actor_user_id=user.id,
            action=AuditAction.PROJECT_UPDATED,
            entity_type="project",
            entity_id=7,
        )
        audit.record_event(
            actor_user_id=user.id,
            action=AuditAction.PROJECT_CREATED,
            entity_type="project",
            entity_id=8,  # different entity — must not show up
        )

        history = audit.list_for_entity("project", 7)
        assert history.total == 2
        assert {entry.action for entry in history.items} == {
            "project.created",
            "project.updated",
        }


def test_every_action_identifies_actor_and_entity(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        audit = AuditService(SqlAlchemyAuditLogRepository(session))

        entry = audit.record_event(
            actor_user_id=user.id,
            action=AuditAction.CONFIG_ACTIVATED,
            entity_type="collection_config",
            entity_id=3,
        )
        assert entry.user_id == user.id
        assert entry.entity_type == "collection_config"
        assert entry.entity_id == 3
