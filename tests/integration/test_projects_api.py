"""T072 HTTP-layer tests: the full `/projects` CRUD surface
(`docs/05_API_DESIGN.md`), built on `ProjectService` (T033, already
unit-tested in depth — this file proves the HTTP wiring, not the
business rules again). Same `TestClient` + `get_db` override technique
as `test_auth_api.py`/`test_dashboard_api.py`."""

from collections.abc import Iterator

import pytest
from app.core.security import hash_password, normalize_email
from app.db.models import User as UserRow
from app.db.session import get_db, session_scope
from app.main import app
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


def _seed_user(session_factory, email: str) -> None:
    with session_scope(session_factory) as session:
        session.add(
            UserRow(
                email=normalize_email(email),
                password_hash=hash_password(VALID_PASSWORD),
                status="active",
            )
        )


def _login(client, email: str) -> str:
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD}
    )
    assert response.status_code == 200
    return response.json()["data"]["token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_projects_endpoints_require_authentication(client):
    assert client.get("/api/v1/projects").status_code == 401
    assert (
        client.post(
            "/api/v1/projects", json={"name": "x", "source_type": "y"}
        ).status_code
        == 401
    )
    assert client.get("/api/v1/projects/1").status_code == 401


def test_create_project_then_it_appears_in_the_list(client, session_factory):
    """T072's literal acceptance criterion."""
    _seed_user(session_factory, "owner@example.com")
    token = _login(client, "owner@example.com")

    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Coffee Shops NYC",
            "source_type": "google_maps",
            "description": "Weekly coffee shop scan",
        },
        headers=_auth_headers(token),
    )
    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["name"] == "Coffee Shops NYC"
    assert created["status"] == "active"
    assert created["description"] == "Weekly coffee shop scan"

    list_response = client.get("/api/v1/projects", headers=_auth_headers(token))
    body = list_response.json()["data"]
    assert body["total"] == 1
    assert body["items"][0]["id"] == created["id"]


def test_create_project_rejects_an_empty_name(client, session_factory):
    _seed_user(session_factory, "owner@example.com")
    token = _login(client, "owner@example.com")

    response = client.post(
        "/api/v1/projects",
        json={"name": "   ", "source_type": "google_maps"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 422


def test_list_projects_is_scoped_to_the_requesting_user(client, session_factory):
    _seed_user(session_factory, "owner@example.com")
    _seed_user(session_factory, "stranger@example.com")
    owner_token = _login(client, "owner@example.com")
    stranger_token = _login(client, "stranger@example.com")

    client.post(
        "/api/v1/projects",
        json={"name": "Owner Project", "source_type": "google_maps"},
        headers=_auth_headers(owner_token),
    )

    stranger_body = client.get(
        "/api/v1/projects", headers=_auth_headers(stranger_token)
    ).json()["data"]
    assert stranger_body == {"items": [], "total": 0, "limit": 50, "offset": 0}


def test_get_project_detail_and_not_found_and_cross_user_denied(
    client, session_factory
):
    _seed_user(session_factory, "owner@example.com")
    _seed_user(session_factory, "stranger@example.com")
    owner_token = _login(client, "owner@example.com")
    stranger_token = _login(client, "stranger@example.com")

    created = client.post(
        "/api/v1/projects",
        json={"name": "Owner Project", "source_type": "google_maps"},
        headers=_auth_headers(owner_token),
    ).json()["data"]

    ok_response = client.get(
        f"/api/v1/projects/{created['id']}", headers=_auth_headers(owner_token)
    )
    assert ok_response.status_code == 200
    assert ok_response.json()["data"]["name"] == "Owner Project"

    not_found = client.get(
        "/api/v1/projects/999999", headers=_auth_headers(owner_token)
    )
    assert not_found.status_code == 404

    denied = client.get(
        f"/api/v1/projects/{created['id']}", headers=_auth_headers(stranger_token)
    )
    assert denied.status_code == 403


def test_update_project_changes_name_and_description(client, session_factory):
    _seed_user(session_factory, "owner@example.com")
    token = _login(client, "owner@example.com")
    created = client.post(
        "/api/v1/projects",
        json={"name": "Original", "source_type": "google_maps"},
        headers=_auth_headers(token),
    ).json()["data"]

    updated = client.patch(
        f"/api/v1/projects/{created['id']}",
        json={"name": "Renamed", "description": "Updated description"},
        headers=_auth_headers(token),
    )
    assert updated.status_code == 200
    body = updated.json()["data"]
    assert body["name"] == "Renamed"
    assert body["description"] == "Updated description"


def test_update_project_rejects_an_empty_name(client, session_factory):
    _seed_user(session_factory, "owner@example.com")
    token = _login(client, "owner@example.com")
    created = client.post(
        "/api/v1/projects",
        json={"name": "Original", "source_type": "google_maps"},
        headers=_auth_headers(token),
    ).json()["data"]

    response = client.patch(
        f"/api/v1/projects/{created['id']}",
        json={"name": "   "},
        headers=_auth_headers(token),
    )
    assert response.status_code == 422


def test_delete_archives_rather_than_hard_deleting(client, session_factory):
    _seed_user(session_factory, "owner@example.com")
    token = _login(client, "owner@example.com")
    created = client.post(
        "/api/v1/projects",
        json={"name": "Original", "source_type": "google_maps"},
        headers=_auth_headers(token),
    ).json()["data"]

    archived = client.delete(
        f"/api/v1/projects/{created['id']}", headers=_auth_headers(token)
    )
    assert archived.status_code == 200
    assert archived.json()["data"]["status"] == "archived"

    # still fetchable — archived, not gone
    still_there = client.get(
        f"/api/v1/projects/{created['id']}", headers=_auth_headers(token)
    )
    assert still_there.status_code == 200
    assert still_there.json()["data"]["status"] == "archived"
