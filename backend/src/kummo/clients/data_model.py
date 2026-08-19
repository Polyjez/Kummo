from datetime import datetime
from uuid import UUID

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from ..data_model import SCHEMA, Entity, auth_user_id, created_at, primary_key


class Client(Entity):
    """A B2C user profile.

    Registration collects the name and email only; the rest is enrichment and stays
    null until the client fills it in.
    """

    __tablename__ = "clients"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[UUID] = primary_key()
    created_at: Mapped[datetime] = created_at()
    auth_user_id: Mapped[UUID | None] = auth_user_id()
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    age: Mapped[int | None] = mapped_column(nullable=True)
    interests: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    number_children: Mapped[int | None] = mapped_column(nullable=True)
