from uuid import UUID
from pydantic import BaseModel


class Shop(BaseModel):
    id: UUID
    name: str
    address: str
    phone: str | None = None
    email: str
    website: str | None = None
    activity_type: list[str]
    picture: str | None = None


class Activity(BaseModel):
    id: UUID
    shop_id: UUID
    title: str
    description: str | None = None
    price: float | None = None
    participants_max: int
    duration: str
    age_group: str | None = None
    picture: str


class ActivityCreate(BaseModel):
    shop_id: UUID
    title: str
    description: str | None = None
    price: float | None = None
    participants_max: int
    duration: str
    age_group: str | None = None
    picture: str = "https://via.placeholder.com/400x250"
