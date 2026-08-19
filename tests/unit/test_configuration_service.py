"""T034 tests: versioning, activation, validation, and immutability of
historical configuration — against SQLite in-memory via the real
repositories (T032), same rationale as tests/unit/test_db_session.py."""

import pytest
from tests.unit.factories import make_user
from tests.unit.fakes import (
    AlwaysInvalidValidator,
    AlwaysValidValidator,
    RequiresQueryFieldValidator,
)

from app.db.session import session_scope
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.repositories.configs import SqlAlchemyCollectionConfigRepository
from app.repositories.projects import SqlAlchemyProjectRepository
from app.services.configs import ConfigurationService
from app.services.errors import InvalidStateError, PermissionDeniedError
from app.services.projects import ProjectService


def _make_services(session, validator=None):
    projects = ProjectService(
        SqlAlchemyProjectRepository(session), SqlAlchemyAuditLogRepository(session)
    )
    configs = ConfigurationService(
        SqlAlchemyCollectionConfigRepository(session),
        projects,
        validator or AlwaysValidValidator(),
    )
    return projects, configs


def test_create_version_starts_at_one_and_activates_by_default(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs = _make_services(session)
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        version = configs.create_version(
            project.id,
            requesting_user_id=user.id,
            provider="google_maps",
            config={"query": "coffee shops"},
        )
        assert version.version == 1
        assert version.is_active is True


def test_version_numbers_increment_deterministically(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs = _make_services(session)
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        v1 = configs.create_version(
            project.id, requesting_user_id=user.id, provider="google_maps", config={}
        )
        v2 = configs.create_version(
            project.id, requesting_user_id=user.id, provider="google_maps", config={}
        )
        v3 = configs.create_version(
            project.id, requesting_user_id=user.id, provider="google_maps", config={}
        )
        assert (v1.version, v2.version, v3.version) == (1, 2, 3)


def test_only_one_version_is_active_at_a_time(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs = _make_services(session)
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        configs.create_version(
            project.id, requesting_user_id=user.id, provider="google_maps", config={}
        )
        configs.create_version(
            project.id, requesting_user_id=user.id, provider="google_maps", config={}
        )

        all_versions = configs.list_versions(project.id, requesting_user_id=user.id)
        active_versions = [v for v in all_versions.items if v.is_active]
        assert len(active_versions) == 1
        assert active_versions[0].version == 2


def test_changing_active_config_does_not_rewrite_old_version_content(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs = _make_services(session)
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        v1 = configs.create_version(
            project.id,
            requesting_user_id=user.id,
            provider="google_maps",
            config={"query": "coffee shops"},
        )
        configs.create_version(
            project.id,
            requesting_user_id=user.id,
            provider="google_maps",
            config={"query": "restaurants"},
        )

        all_versions = configs.list_versions(project.id, requesting_user_id=user.id)
        v1_now = next(v for v in all_versions.items if v.id == v1.id)
        assert v1_now.config == {"query": "coffee shops"}
        assert v1_now.is_active is False  # only the pointer changed


def test_invalid_configuration_cannot_become_active(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs = _make_services(session, validator=AlwaysInvalidValidator())
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        with pytest.raises(InvalidStateError):
            configs.create_version(
                project.id,
                requesting_user_id=user.id,
                provider="google_maps",
                config={},
            )

        assert configs.get_active(project.id, requesting_user_id=user.id) is None


def test_generic_validation_rejects_unsupported_provider(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs = _make_services(session)
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        with pytest.raises(InvalidStateError, match="Unsupported provider"):
            configs.create_version(
                project.id,
                requesting_user_id=user.id,
                provider="some_other_provider",
                config={},
            )


def test_provider_specific_validation_is_delegated_to_the_adapter(session_factory):
    """Proves the provider adapter's own rules actually run, not just
    the generic provider-name check."""
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs = _make_services(
            session, validator=RequiresQueryFieldValidator()
        )
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        with pytest.raises(InvalidStateError, match="query"):
            configs.create_version(
                project.id,
                requesting_user_id=user.id,
                provider="google_maps",
                config={"radius_m": 500},
            )

        version = configs.create_version(
            project.id,
            requesting_user_id=user.id,
            provider="google_maps",
            config={"query": "coffee shops"},
        )
        assert version.is_active is True


def test_activate_version_switches_the_active_pointer(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs = _make_services(session)
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )
        v1 = configs.create_version(
            project.id, requesting_user_id=user.id, provider="google_maps", config={}
        )
        configs.create_version(
            project.id, requesting_user_id=user.id, provider="google_maps", config={}
        )

        reactivated = configs.activate_version(
            project.id, v1.id, requesting_user_id=user.id
        )
        assert reactivated.version == 1
        active = configs.get_active(project.id, requesting_user_id=user.id)
        assert active.id == v1.id


def test_stranger_cannot_create_or_view_configuration(session_factory):
    with session_scope(session_factory) as session:
        owner = make_user(session, email="owner@example.com")
        stranger = make_user(session, email="stranger@example.com")
        projects, configs = _make_services(session)
        project = projects.create_project(
            user_id=owner.id, name="My Project", source_type="google_maps"
        )

        with pytest.raises(PermissionDeniedError):
            configs.create_version(
                project.id,
                requesting_user_id=stranger.id,
                provider="google_maps",
                config={},
            )

        with pytest.raises(PermissionDeniedError):
            configs.get_active(project.id, requesting_user_id=stranger.id)
