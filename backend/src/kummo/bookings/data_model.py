from datetime import datetime
from uuid import UUID

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import REAL
from sqlalchemy.orm import Mapped, mapped_column

from ..data_model import SCHEMA, Entity, created_at, primary_key, references


class Booking(Entity):
    __tablename__ = "bookings"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[UUID] = primary_key()
    created_at: Mapped[datetime] = created_at()
    client_id: Mapped[UUID] = references("clients")
    vendor_id: Mapped[UUID] = references("vendors")
    slot: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int | None] = mapped_column(nullable=True)
    total_price: Mapped[float | None] = mapped_column(REAL, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
