"""Access-token verification.

Verification goes through the provider client, which is why one instance is reused
here unlike in `service.py`: `get_claims` reads nothing from and writes nothing to
session storage.

**This is not a purely local check today.** `get_claims` only verifies a signature
locally when the token is signed with an asymmetric key it can fetch from the JWKS
endpoint. The Supabase project signs with HS256 (`supabase/config.toml` leaves
`signing_keys_path` commented out), and for HS256 the client falls back to calling
the provider's `/user` endpoint — so every authenticated request costs a network
round trip. Moving to asymmetric signing keys is what would make it local; until
then, do not describe it as one.

`get_claims` also validates nothing but `exp`, so the issuer and audience checks
below are ours to make.
"""

import logging
from dataclasses import dataclass
from uuid import UUID

from supabase import AsyncClient, AsyncClientOptions, create_async_client

from ..config import get_settings
from .errors import InvalidToken

logger = logging.getLogger(__name__)

# Every GoTrue access token for a signed-in (non-anonymous) user carries this.
EXPECTED_AUDIENCE = "authenticated"

_verifier_client: AsyncClient | None = None


@dataclass(frozen=True)
class Identity:
    """Who the caller is, according to a verified token."""

    auth_user_id: UUID
    email: str


async def _get_verifier_client() -> AsyncClient:
    global _verifier_client
    if _verifier_client is None:
        settings = get_settings()
        _verifier_client = await create_async_client(
            settings.supabase_url,
            settings.supabase_api_key,
            options=AsyncClientOptions(auto_refresh_token=False, persist_session=False),
        )
    return _verifier_client


async def verify_access_token(token: str) -> Identity:
    if not token:
        raise InvalidToken("No access token supplied.")

    client = await _get_verifier_client()
    try:
        response = await client.auth.get_claims(token)
    except Exception as error:  # provider errors are all equally "not verifiable"
        logger.info("Access token rejected: %s", error)
        raise InvalidToken("The access token is not valid.") from error

    if response is None:
        raise InvalidToken("The access token is not valid.")

    claims = response.get("claims") if isinstance(response, dict) else response.claims
    _check_issuer(claims.get("iss"))
    _check_audience(claims.get("aud"))

    subject = claims.get("sub")
    if not subject:
        raise InvalidToken("The access token carries no subject.")

    try:
        auth_user_id = UUID(str(subject))
    except ValueError as error:
        raise InvalidToken("The access token subject is not a user id.") from error

    return Identity(auth_user_id=auth_user_id, email=claims.get("email") or "")


def expected_issuer() -> str:
    return f"{get_settings().supabase_url.rstrip('/')}/auth/v1"


def _check_issuer(issuer: object) -> None:
    expected = expected_issuer()
    if issuer != expected:
        # Both values, because a misconfigured SUPABASE_URL rejects every token and
        # the difference is the whole diagnosis.
        logger.warning(
            "Access token rejected: issuer %r does not match the expected %r",
            issuer,
            expected,
        )
        raise InvalidToken("The access token was not issued for this application.")


def _check_audience(audience: object) -> None:
    # The claim is a string in GoTrue's tokens, but the JWT spec allows a list.
    values = audience if isinstance(audience, list) else [audience]
    if EXPECTED_AUDIENCE not in values:
        logger.info("Access token rejected: unexpected audience %r", audience)
        raise InvalidToken("The access token was not issued for this application.")


def reset_verifier_client() -> None:
    """Drop the cached client. For tests and shutdown."""
    global _verifier_client
    _verifier_client = None
