"""Shared success-response envelope for /api/v1 endpoints:
{"data": ..., "request_id": ...} — matches docs/05_API_DESIGN.md.
Error responses already get this shape from app.core.errors (T014).
First used at T038 (the first real /api/v1 business endpoints); every
future route should use this rather than returning a bare model."""

from pydantic import BaseModel

from app.core.request_context import get_request_id


class Envelope[T](BaseModel):
    data: T
    request_id: str | None = None


def envelope[T](data: T) -> Envelope[T]:
    return Envelope(data=data, request_id=get_request_id())
