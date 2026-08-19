"""Shared plumbing for SQLAlchemy-backed repositories. Services depend
on each entity's Protocol (e.g. app.repositories.projects.
ProjectRepository), never on this class or on SQLAlchemy types
directly — that's what makes "services can use repositories without
knowing SQLAlchemy implementation details" (T032's acceptance
criterion) true.

Repositories never call session.commit()/rollback() themselves — the
caller's session_scope() (T020) owns the transaction boundary. That's
what "transaction-aware" means here: a repository participates in
whatever transaction it's handed, it doesn't start its own."""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

DEFAULT_PAGE_LIMIT = 50


@dataclass(frozen=True)
class Page[DomainT]:
    items: list[DomainT]
    total: int
    limit: int
    offset: int


class SqlAlchemyRepository[OrmT, DomainT]:
    model: type[OrmT]

    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_domain(self, row: OrmT) -> DomainT:
        raise NotImplementedError

    def get(self, entity_id: int) -> DomainT | None:
        row = self._session.get(self.model, entity_id)
        return self._to_domain(row) if row is not None else None

    def _paginate(
        self, statement: Select[Any], *, limit: int, offset: int
    ) -> Page[DomainT]:
        total = self._session.scalar(
            select(func.count()).select_from(statement.subquery())
        )
        rows = self._session.scalars(statement.limit(limit).offset(offset)).all()
        return Page(
            items=[self._to_domain(row) for row in rows],
            total=total or 0,
            limit=limit,
            offset=offset,
        )
