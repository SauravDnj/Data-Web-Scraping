"""Versioned provider configuration and its validation workflow. No
HTTP, no SQLAlchemy — depends on repository Protocols (T032), the
interim provider-validation Protocol (app.domain.provider_validation —
see its docstring for why it's interim), and ProjectService (T033)
for ownership authorization, reused rather than duplicated."""

from typing import Any

from app.domain.audit_actions import AuditAction
from app.domain.projects import CollectionConfig
from app.domain.provider_validation import ProviderConfigValidator
from app.repositories.base import Page
from app.repositories.configs import CollectionConfigRepository
from app.services.audit import AuditService
from app.services.errors import InvalidStateError
from app.services.projects import ProjectService

# V1 only supports Google Maps (docs/00_MASTER_README.md). Extending
# this set is how a future provider gets onboarded at this layer.
SUPPORTED_PROVIDERS = frozenset({"google_maps"})


class ConfigurationService:
    def __init__(
        self,
        configs: CollectionConfigRepository,
        projects: ProjectService,
        validator: ProviderConfigValidator,
        audit: AuditService,
    ) -> None:
        self._configs = configs
        self._projects = projects
        self._validator = validator
        self._audit = audit

    def create_version(
        self,
        project_id: int,
        *,
        requesting_user_id: int,
        provider: str,
        config: dict[str, Any],
        activate: bool = True,
    ) -> CollectionConfig:
        # Authorization boundary — reuses ProjectService rather than
        # re-implementing ownership checks here.
        self._projects.get_project(project_id, requesting_user_id=requesting_user_id)

        errors = self._validate_generic(provider)
        provider_result = self._validator.validate_config(provider, config)
        if not provider_result.is_valid:
            errors = errors + list(provider_result.errors)
        if errors:
            # Invalid configuration cannot become active — validation
            # happens strictly before any row is created.
            raise InvalidStateError("Configuration is invalid: " + "; ".join(errors))

        new_version = CollectionConfig(
            id=None,
            project_id=project_id,
            provider=provider,
            config=config,
            version=self._next_version_number(project_id),
            is_active=False,  # activation is a separate, explicit step below
        )
        created = self._configs.create(new_version)
        assert created.id is not None  # freshly persisted, always has an id
        self._audit.record_event(
            actor_user_id=requesting_user_id,
            action=AuditAction.CONFIG_CREATED,
            entity_type="collection_config",
            entity_id=created.id,
            details={
                "project_id": project_id,
                "provider": provider,
                "version": created.version,
            },
        )

        if activate:
            created = self._configs.set_active_version(project_id, created.id)
            self._audit.record_event(
                actor_user_id=requesting_user_id,
                action=AuditAction.CONFIG_ACTIVATED,
                entity_type="collection_config",
                entity_id=created.id,
                details={"project_id": project_id, "version": created.version},
            )

        return created

    def activate_version(
        self, project_id: int, config_id: int, *, requesting_user_id: int
    ) -> CollectionConfig:
        """Switch which already-persisted version is active, without
        creating a new one — e.g. reverting to a previous version."""
        self._projects.get_project(project_id, requesting_user_id=requesting_user_id)
        activated = self._configs.set_active_version(project_id, config_id)
        self._audit.record_event(
            actor_user_id=requesting_user_id,
            action=AuditAction.CONFIG_ACTIVATED,
            entity_type="collection_config",
            entity_id=config_id,
            details={"project_id": project_id, "version": activated.version},
        )
        return activated

    def get_active(
        self, project_id: int, *, requesting_user_id: int
    ) -> CollectionConfig | None:
        self._projects.get_project(project_id, requesting_user_id=requesting_user_id)
        return self._configs.get_active_for_project(project_id)

    def list_versions(
        self, project_id: int, *, requesting_user_id: int
    ) -> Page[CollectionConfig]:
        self._projects.get_project(project_id, requesting_user_id=requesting_user_id)
        return self._configs.list_for_project(project_id)

    def _validate_generic(self, provider: str) -> list[str]:
        if provider not in SUPPORTED_PROVIDERS:
            return [f"Unsupported provider '{provider}'."]
        return []

    def _next_version_number(self, project_id: int) -> int:
        # list_for_project orders by version desc (T032) — the first
        # item, if any, is the current highest version.
        latest = self._configs.list_for_project(project_id, limit=1, offset=0)
        if not latest.items:
            return 1
        return latest.items[0].version + 1
