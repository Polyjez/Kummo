"""Route tests for /api/auth.

The identity provider is stubbed at the `service` boundary — that module is the only
one that talks to Supabase, so replacing it exercises everything above it (cookies,
profile linking, status codes) without a network call.
"""

from uuid import UUID, uuid4

import pytest

from kummo.auth import cookies, routes, service
from kummo.auth.dependencies import get_current_identity
from kummo.auth.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    OAuthExchangeFailed,
    SessionExpired,
)
from kummo.auth.tokens import Identity
from kummo.clients import data_model as clients
from kummo.main import app
from kummo.vendors import data_model as vendors


def make_session(**overrides) -> service.Session:
    defaults = dict(
        access_token="access-token-value",
        refresh_token="refresh-token-value",
        expires_in=3600,
        auth_user_id=uuid4(),
        email="anna@example.de",
        full_name=None,
    )
    return service.Session(**{**defaults, **overrides})


@pytest.fixture
def provider(monkeypatch):
    """Replaces the identity provider with recorded, controllable behaviour."""

    class Provider:
        def __init__(self):
            self.session = make_session()
            self.signed_out: list[tuple[str, str]] = []
            self.raises: Exception | None = None

        async def sign_up(self, email, password):
            if self.raises:
                raise self.raises
            return self.session

        async def sign_in(self, email, password):
            if self.raises:
                raise self.raises
            return self.session

        async def refresh(self, refresh_token):
            if self.raises:
                raise self.raises
            return self.session

        async def sign_out(self, access_token, refresh_token):
            self.signed_out.append((access_token, refresh_token))

        async def exchange_code(self, code, verifier):
            if self.raises:
                raise self.raises
            return self.session

        def build_oauth_redirect(self, provider_name, redirect_to):
            return service.OAuthRedirect(
                url=f"https://idp.test/authorize?provider={provider_name}",
                code_verifier="verifier-value",
            )

    fake = Provider()
    for name in (
        "sign_up",
        "sign_in",
        "refresh",
        "sign_out",
        "exchange_code",
        "build_oauth_redirect",
    ):
        monkeypatch.setattr(routes.service, name, getattr(fake, name))
    return fake


# --- Registration ---------------------------------------------------------------


async def test_register_client_creates_profile_and_sets_cookies(
    client, stub_session, provider
):
    response = await client.post(
        "/api/auth/register/client",
        json={
            "email": "anna@example.de",
            "password": "ein-gutes-passwort",
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "client"
    assert body["display_name"] == "Anna Schmidt"

    added = stub_session.added[0]
    assert isinstance(added, clients.Client)
    assert added.auth_user_id == provider.session.auth_user_id


async def test_register_client_response_carries_no_tokens(client, stub_session, provider):
    response = await client.post(
        "/api/auth/register/client",
        json={
            "email": "anna@example.de",
            "password": "ein-gutes-passwort",
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )

    serialized = response.text
    assert provider.session.access_token not in serialized
    assert provider.session.refresh_token not in serialized
    assert set(response.json()) == {"id", "email", "role", "display_name"}


async def test_session_cookies_are_httponly(client, stub_session, provider):
    response = await client.post(
        "/api/auth/register/client",
        json={
            "email": "anna@example.de",
            "password": "ein-gutes-passwort",
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )

    set_cookie_headers = response.headers.get_list("set-cookie")
    session_header = next(
        h for h in set_cookie_headers if h.startswith(f"{cookies.SESSION_COOKIE}=")
    )
    refresh_header = next(
        h for h in set_cookie_headers if h.startswith(f"{cookies.REFRESH_COOKIE}=")
    )
    assert "HttpOnly" in session_header
    assert "HttpOnly" in refresh_header


async def test_register_vendor_creates_vendor_profile(client, stub_session, provider):
    response = await client.post(
        "/api/auth/register/vendor",
        json={
            "email": "info@werkstatt.de",
            "password": "ein-gutes-passwort",
            "name": "Kreativwerkstatt",
            "address": "Oranienstraße 1, 10999 Berlin",
            "activity_type": ["kunst"],
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "vendor"
    assert response.json()["display_name"] == "Kreativwerkstatt"
    assert isinstance(stub_session.added[0], vendors.Vendor)


async def test_register_vendor_requires_activity_type(client, stub_session, provider):
    response = await client.post(
        "/api/auth/register/vendor",
        json={
            "email": "info@werkstatt.de",
            "password": "ein-gutes-passwort",
            "name": "Kreativwerkstatt",
            "address": "Oranienstraße 1",
            "activity_type": [],
        },
    )

    assert response.status_code == 422


async def test_register_rejects_short_password(client, stub_session, provider):
    response = await client.post(
        "/api/auth/register/client",
        json={
            "email": "anna@example.de",
            "password": "kurz",
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )

    assert response.status_code == 422


async def test_register_duplicate_email_is_409(client, stub_session, provider):
    provider.raises = EmailAlreadyRegistered("already exists")

    response = await client.post(
        "/api/auth/register/client",
        json={
            "email": "anna@example.de",
            "password": "ein-gutes-passwort",
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )

    assert response.status_code == 409


# --- Login / logout -------------------------------------------------------------


async def test_login_returns_existing_profile(client, stub_session, provider):
    existing = clients.Client(
        id=uuid4(),
        auth_user_id=provider.session.auth_user_id,
        first_name="Anna",
        last_name="Schmidt",
        email="anna@example.de",
    )
    stub_session.scalar_results = [existing]

    response = await client.post(
        "/api/auth/login",
        json={"email": "anna@example.de", "password": "ein-gutes-passwort"},
    )

    assert response.status_code == 200
    assert response.json()["display_name"] == "Anna Schmidt"
    # An existing profile must not be duplicated.
    assert stub_session.added == []


async def test_login_completes_an_interrupted_registration(
    client, stub_session, provider
):
    """No profile row: registration died between the identity and the insert."""
    provider.session = make_session(full_name="Anna Schmidt")
    stub_session.scalar_results = [None, None]

    response = await client.post(
        "/api/auth/login",
        json={"email": "anna@example.de", "password": "ein-gutes-passwort"},
    )

    assert response.status_code == 200
    assert isinstance(stub_session.added[0], clients.Client)
    assert response.json()["display_name"] == "Anna Schmidt"


async def test_login_with_bad_credentials_is_401(client, stub_session, provider):
    provider.raises = InvalidCredentials("nope")

    response = await client.post(
        "/api/auth/login", json={"email": "anna@example.de", "password": "falsch"}
    )

    assert response.status_code == 401


async def test_logout_clears_cookies_and_revokes(client, stub_session, provider):
    client.cookies.set(cookies.SESSION_COOKIE, "access-token-value")
    client.cookies.set(cookies.REFRESH_COOKIE, "refresh-token-value")

    response = await client.post("/api/auth/logout")

    assert response.status_code == 204
    assert provider.signed_out == [("access-token-value", "refresh-token-value")]
    cleared = response.headers.get_list("set-cookie")
    assert any(cookies.SESSION_COOKIE in header for header in cleared)
    assert any(cookies.REFRESH_COOKIE in header for header in cleared)


async def test_logout_without_a_session_still_succeeds(client, stub_session, provider):
    response = await client.post("/api/auth/logout")

    assert response.status_code == 204
    assert provider.signed_out == []


# --- Refresh --------------------------------------------------------------------


async def test_refresh_without_cookie_is_401(client, stub_session, provider):
    response = await client.post("/api/auth/refresh")

    assert response.status_code == 401


async def test_refresh_with_expired_token_is_401(client, stub_session, provider):
    client.cookies.set(cookies.REFRESH_COOKIE, "stale")
    provider.raises = SessionExpired("expired")

    response = await client.post("/api/auth/refresh")

    assert response.status_code == 401


# --- /me ------------------------------------------------------------------------


async def test_me_without_a_session_is_401(client, stub_session):
    response = await client.get("/api/auth/me")

    assert response.status_code == 401


async def test_me_returns_the_linked_profile(client, stub_session):
    auth_user_id = uuid4()
    stub_session.scalar_results = [
        clients.Client(
            id=uuid4(),
            auth_user_id=auth_user_id,
            first_name="Anna",
            last_name="Schmidt",
            email="anna@example.de",
        )
    ]
    app.dependency_overrides[get_current_identity] = lambda: Identity(
        auth_user_id=auth_user_id, email="anna@example.de"
    )
    try:
        response = await client.get("/api/auth/me")
    finally:
        app.dependency_overrides.pop(get_current_identity, None)

    assert response.status_code == 200
    assert response.json()["role"] == "client"


# --- OAuth ----------------------------------------------------------------------


async def test_oauth_start_redirects_and_stores_the_verifier(
    client, stub_session, provider
):
    response = await client.get("/api/auth/oauth/google", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"].startswith("https://idp.test/authorize")
    verifier_cookie = next(
        h
        for h in response.headers.get_list("set-cookie")
        if h.startswith(f"{cookies.OAUTH_VERIFIER_COOKIE}=")
    )
    assert "HttpOnly" in verifier_cookie


async def test_oauth_start_rejects_unknown_provider(client, stub_session, provider):
    response = await client.get("/api/auth/oauth/myspace", follow_redirects=False)

    assert response.status_code == 404


async def test_oauth_callback_creates_a_client_profile(client, stub_session, provider):
    provider.session = make_session(full_name="Anna Schmidt")
    stub_session.scalar_results = [None, None]
    client.cookies.set(cookies.OAUTH_VERIFIER_COOKIE, "verifier-value")

    response = await client.get(
        "/api/auth/callback", params={"code": "abc"}, follow_redirects=False
    )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/index.html")
    added = stub_session.added[0]
    assert isinstance(added, clients.Client)
    assert (added.first_name, added.last_name) == ("Anna", "Schmidt")


async def test_oauth_callback_sends_a_vendor_to_the_dashboard(
    client, stub_session, provider
):
    stub_session.scalar_results = [
        None,
        vendors.Vendor(
            id=uuid4(),
            auth_user_id=provider.session.auth_user_id,
            name="Kreativwerkstatt",
            address="Oranienstraße 1",
            email="info@werkstatt.de",
            activity_type=["kunst"],
        ),
    ]
    client.cookies.set(cookies.OAUTH_VERIFIER_COOKIE, "verifier-value")

    response = await client.get(
        "/api/auth/callback", params={"code": "abc"}, follow_redirects=False
    )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/business.html")
    assert stub_session.added == []


async def test_oauth_callback_without_a_verifier_goes_back_to_login(
    client, stub_session, provider
):
    response = await client.get(
        "/api/auth/callback", params={"code": "abc"}, follow_redirects=False
    )

    assert response.status_code == 303
    assert "error=oauth" in response.headers["location"]


async def test_oauth_callback_with_a_failed_exchange_goes_back_to_login(
    client, stub_session, provider
):
    provider.raises = OAuthExchangeFailed("bad code")
    client.cookies.set(cookies.OAUTH_VERIFIER_COOKIE, "verifier-value")

    response = await client.get(
        "/api/auth/callback", params={"code": "abc"}, follow_redirects=False
    )

    assert response.status_code == 303
    assert "error=oauth" in response.headers["location"]


def test_uuid_round_trip_of_identity():
    identity = Identity(auth_user_id=UUID(int=1), email="a@b.de")

    assert identity.auth_user_id == UUID(int=1)
