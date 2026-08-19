from collections.abc import Iterator

import pytest
from app.core.dependencies import DependencyStatus, check_database, check_redis
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _fake_status(name: str, healthy: bool):
    def _check() -> DependencyStatus:
        return DependencyStatus(
            name=name, healthy=healthy, detail=None if healthy else "boom"
        )

    return _check


@pytest.fixture(autouse=True)
def _clear_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def test_ready_reports_ok_when_all_dependencies_healthy():
    app.dependency_overrides[check_database] = _fake_status("database", True)
    app.dependency_overrides[check_redis] = _fake_status("redis", True)

    response = client.get("/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["dependencies"]["database"]["healthy"] is True
    assert body["dependencies"]["redis"]["healthy"] is True


def test_ready_reports_unavailable_when_a_dependency_fails():
    app.dependency_overrides[check_database] = _fake_status("database", True)
    app.dependency_overrides[check_redis] = _fake_status("redis", False)

    response = client.get("/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["dependencies"]["redis"]["healthy"] is False
    assert body["dependencies"]["redis"]["detail"] == "boom"


def test_ready_against_real_environment_never_crashes():
    # No overrides: exercises the real check functions. MySQL/Redis dev
    # setup (T012/T013) may not be finished at this point in the build,
    # so this only asserts the endpoint reports status cleanly either
    # way rather than raising.
    response = client.get("/ready")

    assert response.status_code in (200, 503)
    dependencies = response.json()["dependencies"]
    assert "database" in dependencies
    assert "redis" in dependencies
