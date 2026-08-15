"""SQLAlchemy mappings for the `kummo` schema.

These are the domain/persistence types. The Pydantic models in `models.py` are the
transport types; the two are deliberately kept separate.

`auth_user_id` links a profile row to a Supabase Auth user. It carries a unique
constraint but no foreign key: `auth.users` is owned by GoTrue's own role, and
`kummo_migrator` has no privileges there.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, REAL, TIMESTAMP, UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA = "kummo"


class Base(DeclarativeBase):
    pass


def _pk() -> Mapped[UUID]:
    return mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)


def _created_at() -> Mapped[datetime]:
    return mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


class Vendor(Base):
    """A business offering activities. Absorbs what used to be `public.shops`."""

    __tablename__ = "vendors"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[UUID] = _pk()
    created_at: Mapped[datetime] = _created_at()
    auth_user_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), unique=True, nullable=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    website: Mapped[str | None] = mapped_column(Text, nullable=True)
    activity_type: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    picture: Mapped[str | None] = mapped_column(Text, nullable=True)


class Client(Base):
    """A B2C user profile. Replaces `public.users`."""

    __tablename__ = "clients"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[UUID] = _pk()
    created_at: Mapped[datetime] = _created_at()
    auth_user_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), unique=True, nullable=True
    )
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    # Enrichment fields, populated after registration.
    age: Mapped[int | None] = mapped_column(nullable=True)
    interests: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    number_children: Mapped[int | None] = mapped_column(nullable=True)


class Child(Base):
    __tablename__ = "children"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[UUID] = _pk()
    created_at: Mapped[datetime] = _created_at()
    client_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey(f"{SCHEMA}.clients.id"), nullable=False
    )
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    age: Mapped[int] = mapped_column(nullable=False)
    interests: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    gender: Mapped[str | None] = mapped_column(Text, nullable=True)


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[UUID] = _pk()
    created_at: Mapped[datetime] = _created_at()
    vendor_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey(f"{SCHEMA}.vendors.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(REAL, nullable=True)
    participants_max: Mapped[int] = mapped_column(nullable=False)
    duration: Mapped[str] = mapped_column(Text, nullable=False)
    age_group: Mapped[str | None] = mapped_column(Text, nullable=True)
    picture: Mapped[str] = mapped_column(Text, nullable=False)


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[UUID] = _pk()
    created_at: Mapped[datetime] = _created_at()
    client_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey(f"{SCHEMA}.clients.id"), nullable=False
    )
    vendor_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey(f"{SCHEMA}.vendors.id"), nullable=False
    )
    slot: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int | None] = mapped_column(nullable=True)
    total_price: Mapped[float | None] = mapped_column(REAL, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
