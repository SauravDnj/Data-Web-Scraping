"""Shared service-layer error types, reused by every service (T033+).
Deliberately NOT app.core.errors.ApiError — that's an HTTP-transport
concern; the API layer (T039+) is responsible for translating these
into HTTP responses. Keeping API transport out of service code means
services never import from app.api or app.core.errors."""


class ServiceError(Exception):
    """Base for all service-layer errors."""


class NotFoundError(ServiceError):
    def __init__(self, entity: str, entity_id: int) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} {entity_id} not found.")


class PermissionDeniedError(ServiceError):
    def __init__(
        self, message: str = "You do not have access to this resource."
    ) -> None:
        super().__init__(message)


class InvalidStateError(ServiceError):
    """An operation was attempted against an entity in a state that
    doesn't allow it (e.g. starting a job on an archived project)."""
