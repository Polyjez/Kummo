"""The /api/auth surface against the real provider, cookies and all.

These are the regression guards for the two bugs the review found. Both were invisible
to the stubbed suite for the same reason: they were about what happens to the *cookies*
on a path where the provider genuinely rejects something, and the stub never did.
"""

from uuid import uuid4

import pytest

from kummo.auth import cookies

pytestmark = pytest.mark.integration

PASSWORD = "ein-geheimes-passwort"


def unique_email() -> str:
    return f"anna-{uuid4().hex[:12]}@example.de"


def expired_cookies(response) -> set[str]:
    return {
        header.split("=", 1)[0]
        for header in response.headers.get_list("set-cookie")
        if "Max-Age=0" in header or "01 Jan 1970" in header
    }


async def register(db_client) -> dict:
    response = await db_client.post(
        "/api/auth/register/client",
        json={
            "email": unique_email(),
            "password": PASSWORD,
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_register_then_me_round_trips(db_client):
    """The whole chain for real: signup, HttpOnly cookies, then a token this backend
    verifies itself on the way back in."""
    registered = await register(db_client)

    me = await db_client.get("/api/auth/me")

    assert me.status_code == 200
    assert me.json()["id"] == registered["id"]
    assert me.json()["role"] == "client"


async def test_no_token_reaches_the_response_body(db_client):
    response = await db_client.post(
        "/api/auth/register/client",
        json={
            "email": unique_email(),
            "password": PASSWORD,
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )

    assert "access_token" not in response.text
    assert db_client.cookies[cookies.SESSION_COOKIE] not in response.text


async def test_refresh_rotates_the_session(db_client):
    await register(db_client)
    before = db_client.cookies[cookies.REFRESH_COOKIE]

    refreshed = await db_client.post("/api/auth/refresh")

    assert refreshed.status_code == 200
    assert db_client.cookies[cookies.REFRESH_COOKIE] != before


async def test_a_rejected_refresh_token_is_cleared_from_the_browser(db_client):
    """Regression: the clear was written to the injected Response and then discarded,
    because raising discards it. The browser kept re-sending a token the provider had
    already rejected, on every retry, forever."""
    await register(db_client)
    db_client.cookies.set(cookies.REFRESH_COOKIE, "definitely-not-a-refresh-token")

    response = await db_client.post("/api/auth/refresh")

    assert response.status_code == 401
    assert expired_cookies(response) == {
        cookies.SESSION_COOKIE,
        cookies.REFRESH_COOKIE,
    }


async def test_logout_revokes_the_session_at_the_provider(db_client):
    """Regression: logout cleared the cookies but left the refresh token live, so the
    session outlived the sign-out. Proven here by trying to spend it afterwards."""
    await register(db_client)
    refresh_token = db_client.cookies[cookies.REFRESH_COOKIE]

    assert (await db_client.post("/api/auth/logout")).status_code == 204

    # Present the revoked token as a fresh browser would.
    db_client.cookies.set(cookies.REFRESH_COOKIE, refresh_token)
    assert (await db_client.post("/api/auth/refresh")).status_code == 401


async def test_logout_revokes_even_without_the_access_cookie(db_client):
    """The ordinary case: the access cookie lasts an hour, the refresh cookie thirty
    days, so by the time somebody clicks Abmelden the access half is usually gone."""
    await register(db_client)
    refresh_token = db_client.cookies[cookies.REFRESH_COOKIE]
    db_client.cookies.delete(cookies.SESSION_COOKIE)

    assert (await db_client.post("/api/auth/logout")).status_code == 204

    db_client.cookies.set(cookies.REFRESH_COOKIE, refresh_token)
    assert (await db_client.post("/api/auth/refresh")).status_code == 401


async def test_me_is_401_once_the_session_cookie_is_gone(db_client):
    await register(db_client)
    db_client.cookies.delete(cookies.SESSION_COOKIE)

    assert (await db_client.get("/api/auth/me")).status_code == 401


async def test_registering_the_same_address_twice_is_409(db_client):
    email = unique_email()
    body = {
        "email": email,
        "password": PASSWORD,
        "first_name": "Anna",
        "last_name": "Schmidt",
    }

    assert (await db_client.post("/api/auth/register/client", json=body)).status_code == 201
    second = await db_client.post("/api/auth/register/client", json=body)

    assert second.status_code == 409


async def test_signing_in_with_the_wrong_password_is_401(db_client):
    registered = await register(db_client)

    response = await db_client.post(
        "/api/auth/login",
        json={"email": registered["email"], "password": "das-falsche-passwort"},
    )

    assert response.status_code == 401
    # The provider's own wording must not reach the caller.
    assert "supabase" not in response.text.lower()
