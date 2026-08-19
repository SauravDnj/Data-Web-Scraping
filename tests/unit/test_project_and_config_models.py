"""T023 tests: project ownership, config-project linkage, immutable
historical versions, and deterministic active-version selection —
against SQLite in-memory (see tests/unit/test_db_session.py)."""

import pytest
from app.core.security import hash_password, normalize_email
from app.db.models import CollectionConfig, Project, User
from app.db.session import build_session_factory, session_scope
from sqlalchemy.exc import IntegrityError, NoResultFound


def _make_user(session, email: str = "owner@example.com") -> User:
    user = User(
        email=normalize_email(email),
        password_hash=hash_password("correct horse battery staple"),
    )
    session.add(user)
    session.flush()
    return user


def _make_project(session, user_id: int, name: str = "My Project") -> Project:
    project = Project(user_id=user_id, name=name, source_type="google_maps")
    session.add(project)
    session.flush()
    return project


def test_project_belongs_to_user(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        user = _make_user(session)
        project = _make_project(session, user.id)
        project_id = project.id

    with session_scope(factory) as session:
        project = session.query(Project).filter_by(id=project_id).one()
        user = session.query(User).filter_by(id=project.user_id).one()
        assert user.email == "owner@example.com"


def test_project_requires_an_existing_user(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with pytest.raises(IntegrityError), session_scope(factory) as session:
        session.add(Project(user_id=999_999, name="Orphan", source_type="google_maps"))


def test_collection_config_belongs_to_project(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        user = _make_user(session)
        project = _make_project(session, user.id)
        session.add(
            CollectionConfig(
                project_id=project.id,
                provider="google_maps",
                config_json={"query": "coffee shops"},
                version=1,
                is_active=True,
            )
        )
        project_id = project.id

    with session_scope(factory) as session:
        config = session.query(CollectionConfig).filter_by(project_id=project_id).one()
        assert config.provider == "google_maps"


def test_historical_versions_are_retained_and_unmutated(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        user = _make_user(session)
        project = _make_project(session, user.id)
        session.add(
            CollectionConfig(
                project_id=project.id,
                provider="google_maps",
                config_json={"query": "coffee shops"},
                version=1,
                is_active=False,
            )
        )
        session.flush()
        session.add(
            CollectionConfig(
                project_id=project.id,
                provider="google_maps",
                config_json={"query": "coffee shops", "radius_m": 500},
                version=2,
                is_active=True,
            )
        )
        project_id = project.id

    with session_scope(factory) as session:
        versions = (
            session.query(CollectionConfig)
            .filter_by(project_id=project_id)
            .order_by(CollectionConfig.version)
            .all()
        )
        assert len(versions) == 2
        assert versions[0].config_json == {"query": "coffee shops"}
        assert versions[1].config_json == {
            "query": "coffee shops",
            "radius_m": 500,
        }


def test_active_version_is_selected_deterministically(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        user = _make_user(session)
        project = _make_project(session, user.id)
        session.add(
            CollectionConfig(
                project_id=project.id,
                provider="google_maps",
                config_json={"v": 1},
                version=1,
                is_active=False,
            )
        )
        session.add(
            CollectionConfig(
                project_id=project.id,
                provider="google_maps",
                config_json={"v": 2},
                version=2,
                is_active=True,
            )
        )
        project_id = project.id

    with session_scope(factory) as session:
        active = (
            session.query(CollectionConfig)
            .filter_by(project_id=project_id, is_active=True)
            .one()
        )
        assert active.version == 2


def test_no_active_version_is_a_clear_empty_result_not_an_error(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        user = _make_user(session)
        project = _make_project(session, user.id)
        session.add(
            CollectionConfig(
                project_id=project.id,
                provider="google_maps",
                config_json={},
                version=1,
                is_active=False,
            )
        )
        project_id = project.id

    with session_scope(factory) as session, pytest.raises(NoResultFound):
        session.query(CollectionConfig).filter_by(
            project_id=project_id, is_active=True
        ).one()


def test_duplicate_version_number_within_project_is_rejected(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        user = _make_user(session)
        project = _make_project(session, user.id)
        session.add(
            CollectionConfig(
                project_id=project.id,
                provider="google_maps",
                config_json={},
                version=1,
                is_active=True,
            )
        )
        project_id = project.id

    with pytest.raises(IntegrityError), session_scope(factory) as session:
        session.add(
            CollectionConfig(
                project_id=project_id,
                provider="google_maps",
                config_json={"different": "content"},
                version=1,
                is_active=True,
            )
        )
