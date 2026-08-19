from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BigIntegerPK


def _utc_now() -> datetime:
    return datetime.now(UTC)


class CollectionConfig(Base):
    """One immutable row per configuration version. Never update an
    existing row's config_json/provider after creation — create a new
    version instead (enforced by convention here; the service layer,
    T034, is where this becomes a hard rule)."""

    __tablename__ = "collection_configs"
    __table_args__ = (
        Index("ix_collection_configs_project_id_is_active", "project_id", "is_active"),
        UniqueConstraint("project_id", "version"),
    )

    id: Mapped[int] = mapped_column(BigIntegerPK, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        BigIntegerPK, ForeignKey("projects.id"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    config_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now, onupdate=_utc_now
    )
