"""T010 smoke test: verify the backend Python environment is installed
and importable before any application code exists."""

import app


def test_app_package_importable() -> None:
    assert app.__version__ == "0.1.0"


def test_core_dependencies_importable() -> None:
    import alembic  # noqa: F401
    import fastapi  # noqa: F401
    import pydantic  # noqa: F401
    import pydantic_settings  # noqa: F401
    import pymysql  # noqa: F401
    import redis  # noqa: F401
    import sqlalchemy  # noqa: F401
    import uvicorn  # noqa: F401
