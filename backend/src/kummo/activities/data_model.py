from datetime import datetime
from uuid import UUID

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import REAL
from sqlalchemy.orm import Mapped, mapped_column

from ..data_model import SCHEMA, Entity, created_at, primary_key, references


class Activity(Entity):
    __tablename__ = "activities"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[UUID] = primary_key()
    created_at: Mapped[datetime] = created_at()
    vendor_id: Mapped[UUID] = references("vendors")
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(REAL, nullable=True)
    participants_max: Mapped[int] = mapped_column(nullable=False)
    duration: Mapped[str] = mapped_column(Text, nullable=False)
    age_group: Mapped[str | None] = mapped_column(Text, nullable=True)
    picture: Mapped[str] = mapped_column(Text, nullable=False)
