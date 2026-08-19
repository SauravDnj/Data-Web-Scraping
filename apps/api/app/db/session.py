from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def build_engine(
    database_url: str, *, echo: bool = False, **engine_kwargs: Any
) -> Engine:
    """Factory, not a singleton — lets tests build an isolated engine
    (e.g. SQLite in-memory) without touching the app's cached one."""
    engine_kwargs.setdefault("pool_pre_ping", True)
    return create_engine(database_url, echo=echo, **engine_kwargs)


@lru_cache
def get_engine() -> Engine:
    return build_engine(get_settings().database_url)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return build_session_factory(get_engine())


@contextmanager
def session_scope(
    session_factory: sessionmaker[Session] | None = None,
) -> Generator[Session, None, None]:
    """The transaction boundary for a unit of work: commits on success,
    rolls back and re-raises on failure, always closes. Connection
    errors (e.g. MySQL unreachable) surface here as the underlying
    SQLAlchemy/driver exception — not swallowed or reworded, since its
    message is already clear and re-wrapping it would only hide detail."""
    factory = session_factory or get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: request-scoped session, always closed."""
    with session_scope() as session:
        yield session
