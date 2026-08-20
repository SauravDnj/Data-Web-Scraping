"""T071 HTTP-layer tests: `GET /jobs`, `GET /jobs/summary`,
`GET /records/count` — the minimal backend surface the dashboard
needs (docs/T071_PROMPT.md's "API-backed metrics"). Same `TestClient`
+ `get_db` override technique as `test_auth_api.py` (T038)."""

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from app.core.security import hash_password, normalize_email
from app.db.models import CollectionConfig as CollectionConfigRow
from app.db.models import Job as JobRow
from app.db.models import Project as ProjectRow
from app.db.models import Record as RecordRow
from app.db.models import User as UserRow
from app.db.session import get_db, session_scope
from app.domain.jobs import JobStatus
from app.main import app
from app.repositories.jobs import SqlAlchemyJobRepository
from fastapi.testclient import TestClient

VALID_PASSWORD = "correct horse battery staple"


@pytest.fixture
def client(session_factory) -> Iterator[TestClient]:
    def override_get_db():
        with session_scope(session_factory) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


def _seed_user(session_factory, email: str) -> int:
    with session_scope(session_factory) as session:
        user = UserRow(
            email=normalize_email(email),
            password_hash=hash_password(VALID_PASSWORD),
            status="active",
        )
        session.add(user)
        session.flush()
        return user.id


def _login(client, email: str) -> str:
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD}
    )
    assert response.status_code == 200
    return response.json()["data"]["token"]


def _seed_job(session_factory, user_id: int, *, project_name: str = "Project") -> int:
    """A fresh QUEUED job in a new project for `user_id`. Returns the
    job id so the caller can transition its status further."""
    with session_scope(session_factory) as session:
        project = ProjectRow(
            user_id=user_id, name=project_name, source_type="google_maps"
        )
        session.add(project)
        session.flush()
        config = CollectionConfigRow(
            project_id=project.id,
            provider="google_maps",
            config_json={},
            version=1,
            is_active=True,
        )
        session.add(config)
        session.flush()
        job = JobRow(project_id=project.id, config_id=config.id)
        session.add(job)
        session.flush()
        job_id = job.id
        project_id = project.id

    with session_scope(session_factory) as session:
        SqlAlchemyJobRepository(session).update_status(job_id, JobStatus.QUEUED)

    return job_id, project_id


def _seed_record(
    session_factory, project_id: int, job_id: int, canonical_key: str
) -> None:
    with session_scope(session_factory) as session:
        session.add(
            RecordRow(
                project_id=project_id,
                job_id=job_id,
                provider="google_maps",
                canonical_key=canonical_key,
                data_json={},
                collected_at=datetime.now(UTC),
            )
        )


def test_jobs_endpoints_require_authentication(client):
    assert client.get("/api/v1/jobs").status_code == 401
    assert client.get("/api/v1/jobs/summary").status_code == 401
    assert client.get("/api/v1/records/count").status_code == 401


def test_list_jobs_is_empty_for_a_user_with_no_jobs(client, session_factory):
    _seed_user(session_factory, "owner@example.com")
    token = _login(client, "owner@example.com")

    response = client.get("/api/v1/jobs", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()["data"]
    assert body == {"items": [], "total": 0, "limit": 50, "offset": 0}


def test_list_jobs_is_cross_project_but_scoped_to_the_requesting_user(
    client, session_factory
):
    owner_id = _seed_user(session_factory, "owner@example.com")
    stranger_id = _seed_user(session_factory, "stranger@example.com")
    job_a, _ = _seed_job(session_factory, owner_id, project_name="Project A")
    job_b, _ = _seed_job(session_factory, owner_id, project_name="Project B")
    _seed_job(session_factory, stranger_id, project_name="Stranger Project")
    stranger_token = _login(client, "stranger@example.com")
    owner_token = _login(client, "owner@example.com")

    response = client.get(
        "/api/v1/jobs", headers={"Authorization": f"Bearer {owner_token}"}
    )
    body = response.json()["data"]
    assert body["total"] == 2
    assert {item["id"] for item in body["items"]} == {job_a, job_b}

    stranger_response = client.get(
        "/api/v1/jobs", headers={"Authorization": f"Bearer {stranger_token}"}
    )
    stranger_body = stranger_response.json()["data"]
    assert stranger_body["total"] == 1
    assert job_a not in {item["id"] for item in stranger_body["items"]}
    assert job_b not in {item["id"] for item in stranger_body["items"]}


def test_list_jobs_filters_by_status(client, session_factory):
    owner_id = _seed_user(session_factory, "owner@example.com")
    job_id, _ = _seed_job(session_factory, owner_id)
    token = _login(client, "owner@example.com")

    matching = client.get(
        "/api/v1/jobs?status=queued", headers={"Authorization": f"Bearer {token}"}
    )
    assert matching.json()["data"]["total"] == 1
    assert matching.json()["data"]["items"][0]["id"] == job_id

    not_matching = client.get(
        "/api/v1/jobs?status=failed", headers={"Authorization": f"Bearer {token}"}
    )
    assert not_matching.json()["data"]["total"] == 0


def test_jobs_summary_buckets_by_the_three_dashboard_statuses(client, session_factory):
    owner_id = _seed_user(session_factory, "owner@example.com")
    _seed_job(session_factory, owner_id)  # active (QUEUED)

    running_id, _ = _seed_job(session_factory, owner_id)
    with session_scope(session_factory) as session:
        SqlAlchemyJobRepository(session).update_status(running_id, JobStatus.RUNNING)

    completed_id, _ = _seed_job(session_factory, owner_id)
    with session_scope(session_factory) as session:
        repo = SqlAlchemyJobRepository(session)
        repo.update_status(completed_id, JobStatus.RUNNING)
        repo.finalize_job(
            completed_id, status=JobStatus.COMPLETED, finished_at=datetime.now(UTC)
        )

    failed_id, _ = _seed_job(session_factory, owner_id)
    with session_scope(session_factory) as session:
        repo = SqlAlchemyJobRepository(session)
        repo.update_status(failed_id, JobStatus.RUNNING)
        repo.finalize_job(
            failed_id,
            status=JobStatus.FAILED,
            finished_at=datetime.now(UTC),
            error_code="temporary",
        )

    token = _login(client, "owner@example.com")
    response = client.get(
        "/api/v1/jobs/summary", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "active_jobs": 2,
        "completed_jobs": 1,
        "failed_jobs": 1,
    }


def test_records_count_is_cross_project_but_scoped_to_the_requesting_user(
    client, session_factory
):
    owner_id = _seed_user(session_factory, "owner@example.com")
    _seed_user(session_factory, "stranger@example.com")
    job_a, project_a = _seed_job(session_factory, owner_id, project_name="Project A")
    job_b, project_b = _seed_job(session_factory, owner_id, project_name="Project B")
    _seed_record(session_factory, project_a, job_a, "google_maps:places/a1")
    _seed_record(session_factory, project_a, job_a, "google_maps:places/a2")
    _seed_record(session_factory, project_b, job_b, "google_maps:places/b1")

    owner_token = _login(client, "owner@example.com")
    stranger_token = _login(client, "stranger@example.com")

    owner_response = client.get(
        "/api/v1/records/count", headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert owner_response.json()["data"] == {"total": 3}

    stranger_response = client.get(
        "/api/v1/records/count",
        headers={"Authorization": f"Bearer {stranger_token}"},
    )
    assert stranger_response.json()["data"] == {"total": 0}
