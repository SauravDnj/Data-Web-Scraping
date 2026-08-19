"""T039: verifies app.api.service_errors maps each ServiceError
subclass to the correct HTTP status and the standard error envelope.
No real project-scoped route exists yet (those land at T070+) — this
mounts throwaway routes on a fresh FastAPI app with only the handlers
under test registered, the only way to exercise this mapping today."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.service_errors import register_service_error_handlers
from app.services.errors import InvalidStateError, NotFoundError, PermissionDeniedError


def _make_client() -> TestClient:
    app = FastAPI()
    register_service_error_handlers(app)

    @app.get("/not-found")
    def _not_found() -> None:
        raise NotFoundError("Project", 55)

    @app.get("/permission-denied")
    def _permission_denied() -> None:
        raise PermissionDeniedError("User 1 cannot access project 55.")

    @app.get("/invalid-state")
    def _invalid_state() -> None:
        raise InvalidStateError("Project 55 is archived and cannot start new jobs.")

    return TestClient(app, raise_server_exceptions=False)


def test_not_found_error_maps_to_404():
    response = _make_client().get("/not-found")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["message"] == "Project 55 not found."
    assert "request_id" in body


def test_permission_denied_error_maps_to_403_not_401():
    """Not 401 — by the time a service raises this, T038 has already
    authenticated the caller; this is an authorization failure on a
    specific resource, matching docs/10_SECURITY_DEEP.md's model."""
    response = _make_client().get("/permission-denied")
    assert response.status_code == 403
    assert response.json()["error"]["message"] == "User 1 cannot access project 55."


def test_invalid_state_error_maps_to_409():
    response = _make_client().get("/invalid-state")
    assert response.status_code == 409
    assert "archived" in response.json()["error"]["message"]
