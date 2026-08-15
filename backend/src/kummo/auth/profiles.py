"""Linking a verified identity to its `kummo.clients` / `kummo.vendors` row.

Registration cannot be atomic: the identity is created over HTTP by the provider while
the profile row is a local transaction, and deleting a stray identity afterwards would
need the service key this backend deliberately does not hold. So every entry path —
register, login, OAuth callback — goes through `ensure_*`, and a profile that failed to
be written the first time is completed on the next sign-in instead of being compensated.
"""

import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..clients import data_model as clients
from ..vendors import data_model as vendors
from .api_model import Role
from .tokens import Identity

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Profile:
    role: Role
    id: UUID
    email: str
    display_name: str


def _as_client_profile(row: clients.Client) -> Profile:
    return Profile(
        role="client",
        id=row.id,
        email=row.email,
        display_name=f"{row.first_name} {row.last_name}".strip(),
    )


def _as_vendor_profile(row: vendors.Vendor) -> Profile:
    return Profile(role="vendor", id=row.id, email=row.email, display_name=row.name)


def split_full_name(full_name: str | None, fallback_email: str) -> tuple[str, str]:
    """Best effort first/last name from an IDP claim.

    Google sends a single `full_name`; the local part of the email is the fallback when
    it sends nothing at all. Users can correct this later when the profile is enriched.
    """
    if full_name and full_name.strip():
        parts = full_name.strip().split()
        if len(parts) == 1:
            return parts[0], ""
        return " ".join(parts[:-1]), parts[-1]
    return fallback_email.split("@")[0] or "Unbekannt", ""


async def find_profile(session: AsyncSession, auth_user_id: UUID) -> Profile | None:
    client_row = await session.scalar(
        select(clients.Client).where(clients.Client.auth_user_id == auth_user_id)
    )
    if client_row is not None:
        return _as_client_profile(client_row)

    vendor_row = await session.scalar(
        select(vendors.Vendor).where(vendors.Vendor.auth_user_id == auth_user_id)
    )
    if vendor_row is not None:
        return _as_vendor_profile(vendor_row)

    return None


async def ensure_client_profile(
    session: AsyncSession,
    identity: Identity,
    first_name: str,
    last_name: str,
) -> Profile:
    existing = await find_profile(session, identity.auth_user_id)
    if existing is not None:
        return existing

    row = clients.Client(
        auth_user_id=identity.auth_user_id,
        first_name=first_name,
        last_name=last_name,
        email=identity.email,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    logger.info("Created client profile for auth user %s", identity.auth_user_id)
    return _as_client_profile(row)


async def ensure_vendor_profile(
    session: AsyncSession,
    identity: Identity,
    name: str,
    address: str,
    activity_type: list[str],
    phone: str | None = None,
    website: str | None = None,
) -> Profile:
    existing = await find_profile(session, identity.auth_user_id)
    if existing is not None:
        return existing

    row = vendors.Vendor(
        auth_user_id=identity.auth_user_id,
        name=name,
        address=address,
        activity_type=activity_type,
        email=identity.email,
        phone=phone,
        website=website,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    logger.info("Created vendor profile for auth user %s", identity.auth_user_id)
    return _as_vendor_profile(row)
