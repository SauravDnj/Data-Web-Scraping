"""Shared paginated-list response shape for /api/v1 endpoints — every
future list route (jobs, records, projects, ...) wraps its
`app.repositories.base.Page` in this rather than inventing its own
items/total/limit/offset shape. `total` is always a real database
count (`Page.total`, from `SqlAlchemyRepository._paginate()`'s own
`COUNT(*)`), never derived from `len(items)` — that distinction is
what makes it safe for a frontend to treat as authoritative."""

from pydantic import BaseModel


class PagedResponse[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int
