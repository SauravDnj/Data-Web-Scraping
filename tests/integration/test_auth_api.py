"""T038 acceptance criteria, tested at the real HTTP layer (not just
the service layer — tests/unit/test_auth_service.py already covers
the business rules in depth): unauthenticated protected requests
fail; authenticated requests succeed. Overrides app.db.session.get_db
to point at a SQLite in-memory database instead of the real
DATABASE_URL, same technique as T014's dependency-override tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password, normalize_email
from app.db.models import User as UserRow
from app.db.session import get_db, session_scope
from app.main import app

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


def _seed_user(session_factory, email: str = "owner@example.com") -> None:
    with session_scope(session_factory) as session:
        session.add(
            UserRow(
                email=normalize_email(email),
                password_hash=hash_password(VALID_PASSWORD),
                status="active",
            )
        )


def test_me_without_a_token_is_rejected(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_a_garbage_token_is_rejected(client):
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_login_then_me_succeeds(client, session_factory):
    _seed_user(session_factory)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": VALID_PASSWORD},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["token"]
    assert token  # never logged, but fine to assert non-empty in a test

    me_response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    body = me_response.json()
    assert body["data"]["email"] == "owner@example.com"
    assert "request_id" in body


def test_login_with_wrong_password_is_rejected(client, session_factory):
    _seed_user(session_factory)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "wrong password"},
    )
    assert response.status_code == 401
    assert "error" in response.json()


def test_logout_then_me_is_rejected(client, session_factory):
    _seed_user(session_factory)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": VALID_PASSWORD},
    )
    token = login_response.json()["data"]["token"]

    logout_response = client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_response.status_code == 204

    me_response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 401
