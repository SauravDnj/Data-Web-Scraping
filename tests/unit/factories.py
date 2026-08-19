"""Shared ORM-row creation helpers for repository tests. Not a pytest
fixture module — plain functions, called within an open session."""

from datetime import UTC, datetime

from app.core.security import hash_password, normalize_email
from app.db.models import CollectionConfig, Job, Project, User


def make_user(session, email: str = "owner@example.com") -> User:
    user = User(
        email=normalize_email(email),
        password_hash=hash_password("correct horse battery staple"),
    )
    session.add(user)
    session.flush()
    return user


def make_project(session, user_id: int, name: str = "My Project") -> Project:
    project = Project(user_id=user_id, name=name, source_type="google_maps")
    session.add(project)
    session.flush()
    return project


def make_config(
    session, project_id: int, *, version: int = 1, is_active: bool = True
) -> CollectionConfig:
    config = CollectionConfig(
        project_id=project_id,
        provider="google_maps",
        config_json={},
        version=version,
        is_active=is_active,
    )
    session.add(config)
    session.flush()
    return config


def make_job(session, project_id: int, config_id: int) -> Job:
    job = Job(project_id=project_id, config_id=config_id)
    session.add(job)
    session.flush()
    return job


def make_user_project_config(session, email: str = "owner@example.com"):
    user = make_user(session, email=email)
    project = make_project(session, user.id)
    config = make_config(session, project.id)
    return user, project, config


def utc_now() -> datetime:
    return datetime.now(UTC)
