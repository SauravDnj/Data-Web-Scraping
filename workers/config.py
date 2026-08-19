from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """Worker configuration. Deliberately smaller than the API's
    Settings — the worker doesn't need APP_SECRET or the database
    driver at this stage."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    redis_url: str
    log_level: str = "INFO"
    worker_id: str | None = None


@lru_cache
def get_worker_settings() -> WorkerSettings:
    return WorkerSettings()  # type: ignore[call-arg]  # fields come from env vars
