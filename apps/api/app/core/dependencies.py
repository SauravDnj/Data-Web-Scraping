from dataclasses import dataclass
from typing import Annotated

import pymysql
import redis
from fastapi import Depends
from sqlalchemy.engine import make_url

from app.core.config import Settings, get_settings

CONNECT_TIMEOUT_SECONDS = 2


@dataclass(frozen=True)
class DependencyStatus:
    name: str
    healthy: bool
    detail: str | None = None


def check_database(
    settings: Annotated[Settings, Depends(get_settings)],
) -> DependencyStatus:
    """Direct connectivity check, deliberately independent of the
    SQLAlchemy engine/session machinery that T020 introduces — this
    task only needs to know whether MySQL is reachable."""
    url = make_url(settings.database_url)
    try:
        connection = pymysql.connect(
            host=url.host,
            port=url.port or 3306,
            user=url.username,
            password=url.password or "",
            database=url.database,
            connect_timeout=CONNECT_TIMEOUT_SECONDS,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        finally:
            connection.close()
        return DependencyStatus(name="database", healthy=True)
    except Exception as exc:  # noqa: BLE001 - reported as a status, not raised
        return DependencyStatus(name="database", healthy=False, detail=str(exc))


def check_redis(
    settings: Annotated[Settings, Depends(get_settings)],
) -> DependencyStatus:
    try:
        client = redis.Redis.from_url(
            settings.redis_url, socket_connect_timeout=CONNECT_TIMEOUT_SECONDS
        )
        client.ping()
        return DependencyStatus(name="redis", healthy=True)
    except Exception as exc:  # noqa: BLE001 - reported as a status, not raised
        return DependencyStatus(name="redis", healthy=False, detail=str(exc))
