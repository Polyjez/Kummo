"""Conventions shared by every feature's data model.

Each feature declares its own persisted entities in its `data_model.py`; what they
have in common lives here, so the declarative registry is a single one across the
whole `kummo` schema.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA = "kummo"


class Entity(DeclarativeBase):
    """Declarative base. One registry for every entity in the `kummo` schema."""


def primary_key() -> Mapped[UUID]:
    return mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)


def created_at() -> Mapped[datetime]:
    return mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


def auth_user_id() -> Mapped[UUID | None]:
    """Links a profile to a Supabase Auth user.

    Unique, but no foreign key: `auth.users` belongs to GoTrue's own role, which the
    migrations have no privileges on.
    """
    return mapped_column(PgUUID(as_uuid=True), unique=True, nullable=True)


def references(entity: str) -> Mapped[UUID]:
    """A required reference to another entity, e.g. `references("vendors")`."""
    return mapped_column(
        PgUUID(as_uuid=True), ForeignKey(f"{SCHEMA}.{entity}.id"), nullable=False
    )
