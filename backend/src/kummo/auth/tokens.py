"""Access-token verification.

Verification happens against the provider's published signing keys, which the client
caches in-process — so this is a local check, not a network round trip per request.
That is why one client instance is reused here, unlike `service.py`: `get_claims`
reads nothing from and writes nothing to session storage.
"""

import logging
from dataclasses import dataclass
from uuid import UUID

from supabase import AsyncClient, AsyncClientOptions, create_async_client

from ..config import get_settings
from .errors import InvalidToken

logger = logging.getLogger(__name__)

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
    subject = claims.get("sub")
    if not subject:
        raise InvalidToken("The access token carries no subject.")

    return Identity(auth_user_id=UUID(str(subject)), email=claims.get("email") or "")


def reset_verifier_client() -> None:
    """Drop the cached client. For tests and shutdown."""
    global _verifier_client
    _verifier_client = None
