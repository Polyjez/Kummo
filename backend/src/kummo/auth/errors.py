"""Auth domain errors.

Nothing from Supabase escapes past `service.py` — GoTrue exceptions are translated
into these so the route layer never imports a provider type.
"""

from ..errors import KummoError


class AuthError(KummoError):
    """Base class for authentication failures."""


class InvalidCredentials(AuthError):
    """Wrong email or password."""


class EmailAlreadyRegistered(AuthError):
    """Signup rejected because the address already has an account."""


class WeakPassword(AuthError):
    """Password rejected by the provider's strength policy."""


class EmailConfirmationRequired(AuthError):
    """Signup succeeded but no session was issued until the address is confirmed."""


class InvalidToken(AuthError):
    """Access token missing, malformed, expired, or not verifiable."""


class SessionExpired(AuthError):
    """Refresh token rejected; the caller has to log in again."""


class OAuthExchangeFailed(AuthError):
    """The provider redirect could not be turned into a session."""
