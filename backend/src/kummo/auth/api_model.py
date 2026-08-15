"""What the /api/auth surface accepts and returns.

Deliberately free of tokens and provider identifiers: the session travels in HttpOnly
cookies, so nothing here would let a caller tell which identity provider is in use.
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

Role = Literal["client", "vendor"]


class ClientRegistration(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)


class VendorRegistration(BaseModel):
    """A vendor is also the shop, so registration collects the business details."""

    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    activity_type: list[str] = Field(min_length=1)
    phone: str | None = None
    website: str | None = None


class Credentials(BaseModel):
    email: EmailStr
    password: str


class CurrentUser(BaseModel):
    id: UUID
    email: str
    role: Role
    display_name: str
