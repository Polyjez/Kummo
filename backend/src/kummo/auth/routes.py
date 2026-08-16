"""The /api/auth surface.

Every route here hands the caller a session through HttpOnly cookies and a plain
`CurrentUser` body. Nothing leaks that the identity provider is Supabase — not a URL,
not a token, not a provider error code.
"""

import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
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


def _log_safe(value: str | None, limit: int = 80) -> str:
    """Make provider-supplied text safe to put in a log line.

    Anything arriving on the query string is attacker-controlled; a newline in it
    would let a caller forge whole entries in a plaintext log sink.
    """
    if not value:
        return "none"
    collapsed = " ".join(value.split())
    return collapsed[:limit] if len(collapsed) <= limit else f"{collapsed[:limit]}..."


def _failed_response(error: AuthError) -> JSONResponse:
    """The same mapping as `_http_error`, but as a response we can attach cookies to.

    Headers written to the injected `Response` are only merged into the reply when the
    handler *returns*; raising discards them, because the exception handler builds a
    fresh response. So any path that has to both fail and clear cookies must return.
    """
    http_error = _http_error(error)
    return JSONResponse({"detail": http_error.detail}, status_code=http_error.status_code)


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
    # The refresh token alone is enough to revoke, and it is the half that is still
    # there: the access cookie lasts an hour, the refresh cookie thirty days. Waiting
    # for both meant the common case — logging out of a tab left open overnight —
    # cleared the cookies while the session stayed alive at the provider.
    refresh_token = cookies.read_refresh_token(request)
    if refresh_token:
        await service.sign_out(refresh_token, cookies.read_access_token(request))

    response = Response(status_code=204)
    cookies.clear_session_cookies(response)
    cookies.clear_oauth_state(response)
    return response


@router.post("/refresh", response_model=CurrentUser)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_session),
) -> CurrentUser | Response:
    refresh_token = cookies.read_refresh_token(request)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        auth_session = await service.refresh(refresh_token)
    except AuthError as error:
        # Returned, not raised, so the cookie clearing survives — otherwise the browser
        # keeps a token the provider has already rejected and re-sends it every time.
        failed = _failed_response(error)
        cookies.clear_session_cookies(failed)
        return failed

    profile = await find_profile(db, auth_session.auth_user_id)
    if profile is None:
        # The refresh succeeded, so rotation has already revoked the token the browser
        # holds. Leaving it in place would strand the session on a dead cookie.
        failed = JSONResponse(
            {"detail": "No profile linked to this account"}, status_code=404
        )
        cookies.clear_session_cookies(failed)
        return failed

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
    cookies.set_oauth_state(response, redirect.code_verifier, redirect.state)
    return response


@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> RedirectResponse:
    base = settings.app_base_url.rstrip("/")
    expected_state, verifier = cookies.read_oauth_state(request)

    def back_to_login() -> RedirectResponse:
        failed = RedirectResponse(f"{base}/login.html?error=oauth", status_code=303)
        cookies.clear_oauth_state(failed)
        return failed

    if code is None or not verifier:
        # The provider's text is attacker-controlled, so it is summarised, never
        # interpolated: a newline in it would forge entries in a plaintext log.
        logger.info(
            "OAuth callback without a usable code (provider error: %s)",
            _log_safe(error or error_description),
        )
        return back_to_login()

    # PKCE already stops the code being redeemed anywhere but the browser holding the
    # verifier; `state` is what proves this callback belongs to the flow we started.
    # Compared as bytes: `compare_digest` refuses non-ASCII str, and the query string
    # is caller-controlled, so a stray umlaut would otherwise be a 500.
    if not state or not secrets.compare_digest(
        state.encode("utf-8"), expected_state.encode("utf-8")
    ):
        logger.warning("OAuth callback with a mismatched state; discarding the flow")
        return back_to_login()

    try:
        auth_session = await service.exchange_code(code, verifier)
    except AuthError as exchange_error:
        # OAuthExchangeFailed plus the provider-unavailable case: from the browser's
        # point of view both are the same dead end.
        logger.warning("OAuth code exchange failed: %s", exchange_error)
        return back_to_login()

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
