"""What the /api/auth surface accepts and returns.

Deliberately free of tokens and provider identifiers: the session travels in HttpOnly
cookies, so nothing here would let a caller tell which identity provider is in use.
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

Role = Literal["client", "vendor"]

# The provider hashes with bcrypt, which silently ignores everything past 72 bytes:
# accepting more would mean quietly storing a shorter password than the one typed.
PASSWORD_MAX_LENGTH = 72


class ClientRegistration(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=PASSWORD_MAX_LENGTH)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)


class VendorRegistration(BaseModel):
    """A vendor is also the shop, so registration collects the business details."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=PASSWORD_MAX_LENGTH)
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    activity_type: list[str] = Field(min_length=1)
    phone: str | None = None
    website: str | None = None


class Credentials(BaseModel):
    email: EmailStr
    # No minimum — a wrong password of any length is the provider's answer to give,
    # not ours — but a cap, so an oversized body never reaches it.
    password: str = Field(max_length=PASSWORD_MAX_LENGTH)


class EmailRequest(BaseModel):
    """A bare address, for the paths that only need one (resending a confirmation)."""

    email: EmailStr


class CurrentUser(BaseModel):
    id: UUID
    email: str
    role: Role
    display_name: str


# Whether registration ends with a usable session depends on the provider's email
# confirmation setting, so the caller is told which of the two happened rather than
# having to infer it from the status code.
RegistrationStatus = Literal["active", "pending_confirmation"]


class RegistrationResult(BaseModel):
    status: RegistrationStatus
    user: CurrentUser
