"""The /api/auth surface.

Every route here hands the caller a session through HttpOnly cookies and a plain
`CurrentUser` body. Nothing leaks that the identity provider is Supabase — not a URL,
not a token, not a provider error code.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import Settings, get_settings
from ..db import get_session
from . import cookies, service
from .api_model import ClientRegistration, Credentials, CurrentUser, VendorRegistration
from .dependencies import get_current_profile
from .errors import (
    AuthError,
    EmailAlreadyRegistered,
    EmailConfirmationRequired,
    InvalidCredentials,
    OAuthExchangeFailed,
    SessionExpired,
    WeakPassword,
)
from .profiles import (
    Profile,
    ensure_client_profile,
    ensure_vendor_profile,
    find_profile,
    split_full_name,
)
from .tokens import Identity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

SUPPORTED_PROVIDERS = {"google", "apple", "azure", "github", "facebook"}


def _as_current_user(profile: Profile) -> CurrentUser:
    return CurrentUser(
        id=profile.id,
        email=profile.email,
        role=profile.role,
        display_name=profile.display_name,
    )


def _identity_of(session: service.Session) -> Identity:
    return Identity(auth_user_id=session.auth_user_id, email=session.email)


def _http_error(error: AuthError) -> HTTPException:
    if isinstance(error, InvalidCredentials):
        return HTTPException(status_code=401, detail=str(error))
    if isinstance(error, EmailAlreadyRegistered):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, (WeakPassword, EmailConfirmationRequired)):
        return HTTPException(status_code=400, detail=str(error))
    if isinstance(error, SessionExpired):
        return HTTPException(status_code=401, detail=str(error))
    return HTTPException(status_code=502, detail="The identity provider is unavailable")


@router.post("/register/client", response_model=CurrentUser, status_code=201)
async def register_client(
    body: ClientRegistration,
    response: Response,
    db: AsyncSession = Depends(get_session),
) -> CurrentUser:
    try:
        auth_session = await service.sign_up(body.email, body.password)
    except AuthError as error:
        raise _http_error(error) from error

    profile = await ensure_client_profile(
        db, _identity_of(auth_session), body.first_name, body.last_name
    )
    cookies.set_session_cookies(response, auth_session)
    return _as_current_user(profile)


@router.post("/register/vendor", response_model=CurrentUser, status_code=201)
async def register_vendor(
    body: VendorRegistration,
    response: Response,
    db: AsyncSession = Depends(get_session),
) -> CurrentUser:
    try:
        auth_session = await service.sign_up(body.email, body.password)
    except AuthError as error:
        raise _http_error(error) from error

    profile = await ensure_vendor_profile(
        db,
        _identity_of(auth_session),
        name=body.name,
        address=body.address,
        activity_type=body.activity_type,
        phone=body.phone,
        website=body.website,
    )
    cookies.set_session_cookies(response, auth_session)
    return _as_current_user(profile)


@router.post("/login", response_model=CurrentUser)
async def login(
    body: Credentials,
    response: Response,
    db: AsyncSession = Depends(get_session),
) -> CurrentUser:
    try:
        auth_session = await service.sign_in(body.email, body.password)
    except AuthError as error:
        raise _http_error(error) from error

    profile = await find_profile(db, auth_session.auth_user_id)
    if profile is None:
        # Registration was interrupted after the identity was created. Complete it now
        # rather than leaving the account permanently unusable.
        first_name, last_name = split_full_name(
            auth_session.full_name, auth_session.email
        )
        profile = await ensure_client_profile(
            db, _identity_of(auth_session), first_name, last_name
        )

    cookies.set_session_cookies(response, auth_session)
    return _as_current_user(profile)


@router.post("/logout", status_code=204)
async def logout(request: Request) -> Response:
    access_token = cookies.read_access_token(request)
    refresh_token = cookies.read_refresh_token(request)
    if access_token and refresh_token:
        await service.sign_out(access_token, refresh_token)

    response = Response(status_code=204)
    cookies.clear_session_cookies(response)
    return response


@router.post("/refresh", response_model=CurrentUser)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_session),
) -> CurrentUser:
    refresh_token = cookies.read_refresh_token(request)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        auth_session = await service.refresh(refresh_token)
    except AuthError as error:
        cookies.clear_session_cookies(response)
        raise _http_error(error) from error

    profile = await find_profile(db, auth_session.auth_user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="No profile linked to this account")

    cookies.set_session_cookies(response, auth_session)
    return _as_current_user(profile)


@router.get("/me", response_model=CurrentUser)
async def me(profile: Profile = Depends(get_current_profile)) -> CurrentUser:
    return _as_current_user(profile)


@router.get("/oauth/{provider}")
async def start_oauth(
    provider: str, settings: Settings = Depends(get_settings)
) -> RedirectResponse:
    """Send the browser to the provider.

    Sign-up through a provider always produces a *client*: a vendor is also the shop,
    and a Google profile carries no address or activity types. An existing vendor can
    still sign in this way — the callback finds the profile that is already linked.
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unknown provider")

    redirect = service.build_oauth_redirect(
        provider, f"{settings.app_base_url.rstrip('/')}/api/auth/callback"
    )
    response = RedirectResponse(redirect.url, status_code=307)
    cookies.set_oauth_state(response, redirect.code_verifier)
    return response


@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: str | None = None,
    error_description: str | None = None,
    db: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> RedirectResponse:
    base = settings.app_base_url.rstrip("/")
    verifier = cookies.read_oauth_verifier(request)

    if code is None or not verifier:
        logger.info("OAuth callback without a usable code (%s)", error_description)
        failed = RedirectResponse(f"{base}/login.html?error=oauth", status_code=303)
        cookies.clear_oauth_state(failed)
        return failed

    try:
        auth_session = await service.exchange_code(code, verifier)
    except OAuthExchangeFailed:
        failed = RedirectResponse(f"{base}/login.html?error=oauth", status_code=303)
        cookies.clear_oauth_state(failed)
        return failed

    profile = await find_profile(db, auth_session.auth_user_id)
    if profile is None:
        first_name, last_name = split_full_name(
            auth_session.full_name, auth_session.email
        )
        profile = await ensure_client_profile(
            db, _identity_of(auth_session), first_name, last_name
        )

    # Land on the page that belongs to the role, the same split the frontend
    # guard enforces: a vendor has no profile page, a client no dashboard.
    destination = "/vendor.html" if profile.role == "vendor" else "/client.html"
    response = RedirectResponse(f"{base}{destination}", status_code=303)
    cookies.clear_oauth_state(response)
    cookies.set_session_cookies(response, auth_session)
    return response
