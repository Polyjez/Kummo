from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Activity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vendor_id: UUID
    title: str
    description: str | None = None
    price: float | None = None
    participants_max: int
    duration: str
    age_group: str | None = None
    picture: str


class ActivityCreate(BaseModel):
    vendor_id: UUID
    title: str
    description: str | None = None
    price: float | None = None
    participants_max: int
    duration: str
    age_group: str | None = None
    picture: str = "https://via.placeholder.com/400x250"
