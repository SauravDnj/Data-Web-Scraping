import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_requires_mandatory_infrastructure_vars(monkeypatch):
    monkeypatch.delenv("APP_SECRET", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_loads_from_environment(monkeypatch):
    monkeypatch.setenv("APP_SECRET", "s")
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://u:p@localhost:3306/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    settings = Settings(_env_file=None)

    assert settings.app_secret == "s"
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert settings.google_maps_api_key is None
