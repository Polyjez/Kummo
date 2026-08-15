"""The only module that knows the identity provider is Supabase.

Everything above this layer works with `Session`, `OAuthRedirect` and the errors in
`errors.py`, so the `/api/auth/*` surface stays transparent: callers never see a
Supabase URL, a provider error code, or a token.

OAuth uses PKCE with the verifier held in a short-lived cookie rather than in the
client's in-memory storage, because the authorize request and the callback are two
separate HTTP requests handled by (potentially) different workers.
"""

import base64
import hashlib
import logging
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode
from uuid import UUID

from supabase import AsyncClient, AsyncClientOptions, create_async_client
from supabase_auth.errors import AuthApiError, AuthError as ProviderAuthError

from ..config import get_settings
from .errors import (
    AuthError,
    EmailAlreadyRegistered,
    EmailConfirmationRequired,
    InvalidCredentials,
    OAuthExchangeFailed,
    SessionExpired,
    WeakPassword,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Session:
    """A verified identity plus the tokens that prove it."""

    access_token: str
    refresh_token: str
    expires_in: int
    auth_user_id: UUID
    email: str
    # Present on OAuth signups: whatever the IDP told us about the person.
    full_name: str | None = None


@dataclass(frozen=True)
class OAuthRedirect:
    url: str
    code_verifier: str


async def _client() -> AsyncClient:
    """A fresh client per operation: session state must not leak between requests."""
    settings = get_settings()
    return await create_async_client(
        settings.supabase_url,
        settings.supabase_api_key,
        options=AsyncClientOptions(
            flow_type="pkce",
            auto_refresh_token=False,
            persist_session=False,
        ),
    )


def _to_session(response) -> Session:
    session = getattr(response, "session", None)
    if session is None or session.access_token is None:
        raise EmailConfirmationRequired(
            "The identity provider issued no session for this account."
        )
    user = session.user
    metadata = user.user_metadata or {}
    return Session(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        expires_in=session.expires_in or 3600,
        auth_user_id=UUID(str(user.id)),
        email=user.email or "",
        full_name=metadata.get("full_name") or metadata.get("name"),
    )


def _translate(error: ProviderAuthError) -> AuthError:
    code = getattr(error, "code", None) or ""
    message = str(getattr(error, "message", error))
    if code in {"user_already_exists", "email_exists"}:
        return EmailAlreadyRegistered("That email address already has an account.")
    if code == "weak_password":
        return WeakPassword(message)
    if code in {"invalid_credentials", "invalid_grant"}:
        return InvalidCredentials("Wrong email or password.")
    if "Invalid login credentials" in message:
        return InvalidCredentials("Wrong email or password.")
    logger.warning("Unmapped provider auth error (code=%s): %s", code, message)
    return AuthError(message)


async def sign_up(email: str, password: str) -> Session:
    client = await _client()
    try:
        response = await client.auth.sign_up({"email": email, "password": password})
    except AuthApiError as error:
        raise _translate(error) from error
    return _to_session(response)


async def sign_in(email: str, password: str) -> Session:
    client = await _client()
    try:
        response = await client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except AuthApiError as error:
        raise _translate(error) from error
    return _to_session(response)


async def refresh(refresh_token: str) -> Session:
    client = await _client()
    try:
        response = await client.auth.refresh_session(refresh_token)
    except AuthApiError as error:
        raise SessionExpired("The session could not be refreshed.") from error
    return _to_session(response)


async def sign_out(access_token: str, refresh_token: str) -> None:
    """Revoke this session only; other devices stay signed in."""
    client = await _client()
    try:
        await client.auth.set_session(access_token, refresh_token)
        await client.auth.sign_out({"scope": "local"})
    except ProviderAuthError as error:
        # An already-invalid token is not a failure worth surfacing: the caller
        # wanted to be logged out, and the cookies are cleared either way.
        logger.info("Sign-out on an already-invalid session: %s", error)


def build_oauth_redirect(provider: str, redirect_to: str) -> OAuthRedirect:
    """Authorize URL for the provider, with a freshly minted PKCE verifier.

    Built by hand rather than through `sign_in_with_oauth` because that method keeps
    the verifier in the client's storage, which does not survive to the callback
    request. The verifier travels in an HttpOnly cookie instead.
    """
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    query = urlencode(
        {
            "provider": provider,
            "redirect_to": redirect_to,
            "code_challenge": challenge,
            "code_challenge_method": "s256",
        }
    )
    base = get_settings().supabase_url.rstrip("/")
    return OAuthRedirect(url=f"{base}/auth/v1/authorize?{query}", code_verifier=verifier)


async def exchange_code(code: str, code_verifier: str) -> Session:
    client = await _client()
    try:
        response = await client.auth.exchange_code_for_session(
            {"auth_code": code, "code_verifier": code_verifier}
        )
    except ProviderAuthError as error:
        raise OAuthExchangeFailed("The sign-in could not be completed.") from error
    return _to_session(response)
