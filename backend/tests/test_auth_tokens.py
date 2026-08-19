"""Access-token verification.

This is the function every authenticated request runs through, and until now only its
empty-string guard was covered. The provider client is stubbed at
`_get_verifier_client`, which is the single seam between this module and the network —
so the claim handling, the issuer and audience checks and the failure translation all
run for real.
"""

from uuid import UUID

import pytest

from kummo.auth import tokens
from kummo.auth.errors import InvalidToken

AUTH_USER_ID = "11111111-1111-1111-1111-111111111111"


def valid_claims(**overrides) -> dict:
    defaults = {
        "sub": AUTH_USER_ID,
        "email": "anna@example.de",
        "iss": tokens.expected_issuer(),
        "aud": "authenticated",
    }
    return {**defaults, **overrides}


class ClaimsResponse:
    """Mirrors the attribute-style response the provider client returns."""

    def __init__(self, claims):
        self.claims = claims


@pytest.fixture
def provider_claims(monkeypatch):
    """Stubs the verifier client; set `.result` or `.raises` per test."""

    class Auth:
        def __init__(self, holder):
            self._holder = holder

        async def get_claims(self, token):
            self._holder.tokens_seen.append(token)
            if self._holder.raises:
                raise self._holder.raises
            return self._holder.result

    class Client:
        def __init__(self):
            self.result = ClaimsResponse(valid_claims())
            self.raises: Exception | None = None
            self.tokens_seen: list[str] = []
            self.auth = Auth(self)

    fake = Client()

    async def _fake_client():
        return fake

    monkeypatch.setattr(tokens, "_get_verifier_client", _fake_client)
    return fake


# --- The happy path ---------------------------------------------------------------


async def test_a_valid_token_yields_the_identity(provider_claims):
    identity = await tokens.verify_access_token("a.b.c")

    assert identity.auth_user_id == UUID(AUTH_USER_ID)
    assert identity.email == "anna@example.de"
    assert provider_claims.tokens_seen == ["a.b.c"]


async def test_a_token_without_an_email_claim_yields_an_empty_string(provider_claims):
    """Absence is a blank field, never None — the Identity contract is a str."""
    provider_claims.result = ClaimsResponse(valid_claims(email=None))

    assert await tokens.verify_access_token("a.b.c") == tokens.Identity(
        auth_user_id=UUID(AUTH_USER_ID), email=""
    )


async def test_a_dict_shaped_response_is_read_the_same_way(provider_claims):
    """The client has returned both shapes across versions."""
    provider_claims.result = {"claims": valid_claims()}

    identity = await tokens.verify_access_token("a.b.c")

    assert identity.auth_user_id == UUID(AUTH_USER_ID)


# --- Rejections -------------------------------------------------------------------


async def test_an_absent_token_is_rejected_without_calling_the_provider(provider_claims):
    with pytest.raises(InvalidToken):
        await tokens.verify_access_token("")

    assert provider_claims.tokens_seen == []


async def test_a_token_the_provider_rejects_becomes_invalid_token(provider_claims):
    """Expired, malformed or badly signed all arrive here as one exception."""
    provider_claims.raises = RuntimeError("JWT has expired")

    with pytest.raises(InvalidToken):
        await tokens.verify_access_token("a.b.c")


async def test_an_empty_response_is_rejected(provider_claims):
    provider_claims.result = None

    with pytest.raises(InvalidToken):
        await tokens.verify_access_token("a.b.c")


async def test_a_token_without_a_subject_is_rejected(provider_claims):
    provider_claims.result = ClaimsResponse(valid_claims(sub=None))

    with pytest.raises(InvalidToken):
        await tokens.verify_access_token("a.b.c")


async def test_a_subject_that_is_not_a_user_id_is_rejected(provider_claims):
    """Regression: this used to escape as a ValueError, so a 500 rather than a 401."""
    provider_claims.result = ClaimsResponse(valid_claims(sub="not-a-uuid"))

    with pytest.raises(InvalidToken):
        await tokens.verify_access_token("a.b.c")


# --- Issuer and audience ----------------------------------------------------------
#
# The provider client validates `exp` and nothing else, so these two are ours to make.


async def test_a_token_from_another_issuer_is_rejected(provider_claims):
    provider_claims.result = ClaimsResponse(
        valid_claims(iss="https://someone-else.supabase.co/auth/v1")
    )

    with pytest.raises(InvalidToken):
        await tokens.verify_access_token("a.b.c")


async def test_a_token_without_an_issuer_is_rejected(provider_claims):
    provider_claims.result = ClaimsResponse(valid_claims(iss=None))

    with pytest.raises(InvalidToken):
        await tokens.verify_access_token("a.b.c")


async def test_a_token_for_another_audience_is_rejected(provider_claims):
    """An anon or service token is not a signed-in user."""
    provider_claims.result = ClaimsResponse(valid_claims(aud="anon"))

    with pytest.raises(InvalidToken):
        await tokens.verify_access_token("a.b.c")


async def test_an_audience_list_containing_ours_is_accepted(provider_claims):
    """GoTrue sends a string, but the JWT spec allows a list."""
    provider_claims.result = ClaimsResponse(valid_claims(aud=["authenticated", "other"]))

    identity = await tokens.verify_access_token("a.b.c")

    assert identity.auth_user_id == UUID(AUTH_USER_ID)
