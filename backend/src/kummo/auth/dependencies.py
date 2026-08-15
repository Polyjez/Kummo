"""FastAPI dependencies for authenticated routes."""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from .cookies import read_access_token
from .errors import InvalidToken
from .profiles import Profile, find_profile
from .tokens import Identity, verify_access_token

UNAUTHENTICATED = HTTPException(status_code=401, detail="Not authenticated")


async def get_current_identity(request: Request) -> Identity:
    """The verified caller. 401 when the session cookie is missing or invalid."""
    try:
        return await verify_access_token(read_access_token(request))
    except InvalidToken as error:
        raise UNAUTHENTICATED from error


async def get_optional_identity(request: Request) -> Identity | None:
    """Like `get_current_identity`, but for routes that also serve anonymous callers."""
    try:
        return await verify_access_token(read_access_token(request))
    except InvalidToken:
        return None


async def get_current_profile(
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> Profile:
    profile = await find_profile(session, identity.auth_user_id)
    if profile is None:
        # Authenticated but unlinked: registration was interrupted after the identity
        # was created. Signing in again completes it via ensure_*_profile.
        raise HTTPException(status_code=404, detail="No profile linked to this account")
    return profile


async def get_current_client(
    profile: Profile = Depends(get_current_profile),
) -> Profile:
    if profile.role != "client":
        raise HTTPException(status_code=403, detail="This route requires a client account")
    return profile


async def get_current_vendor(
    profile: Profile = Depends(get_current_profile),
) -> Profile:
    if profile.role != "vendor":
        raise HTTPException(status_code=403, detail="This route requires a vendor account")
    return profile
