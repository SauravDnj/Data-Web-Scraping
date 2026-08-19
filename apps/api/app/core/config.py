from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables (and
    a local .env file in development). Missing required variables fail
    startup clearly rather than allowing the app to run misconfigured."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_secret: str
    database_url: str
    redis_url: str
    google_maps_api_key: str | None = None
    frontend_origin: str = "http://localhost:3000"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # fields are populated from env vars
