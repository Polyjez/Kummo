"""The /api/auth surface against the real provider, cookies and all.

These are the regression guards for the two bugs the review found. Both were invisible
to the stubbed suite for the same reason: they were about what happens to the *cookies*
on a path where the provider genuinely rejects something, and the stub never did.
"""

import asyncio
from uuid import uuid4

import pytest

from kummo.auth import cookies

from .mail import confirmation_token_hash

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


async def register(db_client, email: str | None = None) -> dict:
    """A registered *and confirmed* client, with the session cookies on `db_client`.

    Registration alone no longer signs anybody in: the local stack requires email
    confirmation, the same as the hosted project. So the helper walks the whole path —
    sign up, read the link out of the mail catcher, redeem it.
    """
    email = email or unique_email()
    response = await db_client.post(
        "/api/auth/register/client",
        json={
            "email": email,
            "password": PASSWORD,
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )
    assert response.status_code == 202, response.text
    assert response.json()["status"] == "pending_confirmation"

    confirmed = await db_client.get(
        "/api/auth/confirm",
        params={"token_hash": await confirmation_token_hash(email)},
        follow_redirects=False,
    )
    assert confirmed.status_code == 303, confirmed.text
    return response.json()["user"]


async def test_register_then_me_round_trips(db_client):
    """The whole chain for real: signup, HttpOnly cookies, then a token this backend
    verifies itself on the way back in."""
    registered = await register(db_client)

    me = await db_client.get("/api/auth/me")

    assert me.status_code == 200
    assert me.json()["id"] == registered["id"]
    assert me.json()["role"] == "client"


async def test_no_token_reaches_the_response_body(db_client):
    await register(db_client)

    me = await db_client.get("/api/auth/me")

    assert "access_token" not in me.text
    assert db_client.cookies[cookies.SESSION_COOKIE] not in me.text


async def test_registration_alone_hands_out_no_session(db_client):
    """The provider requires confirmation, so there is nothing to put in a cookie."""
    response = await db_client.post(
        "/api/auth/register/client",
        json={
            "email": unique_email(),
            "password": PASSWORD,
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )

    assert response.status_code == 202
    assert response.headers.get_list("set-cookie") == []
    assert "access_token" not in response.text
    assert (await db_client.get("/api/auth/me")).status_code == 401


async def test_signing_in_before_confirming_is_403(db_client):
    """The failure that only showed up against the hosted project: the provider answers
    the password grant with a 400 `email_not_confirmed`, which used to reach the browser
    as a 502 "the identity provider is unavailable"."""
    email = unique_email()
    registered = await db_client.post(
        "/api/auth/register/client",
        json={
            "email": email,
            "password": PASSWORD,
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )
    assert registered.status_code == 202

    response = await db_client.post(
        "/api/auth/login", json={"email": email, "password": PASSWORD}
    )

    assert response.status_code == 403
    assert "supabase" not in response.text.lower()


async def test_confirming_then_signing_in_works(db_client):
    registered = await register(db_client)

    signed_in = await db_client.post(
        "/api/auth/login", json={"email": registered["email"], "password": PASSWORD}
    )

    assert signed_in.status_code == 200
    assert signed_in.json()["id"] == registered["id"]


async def test_a_confirmation_link_cannot_be_spent_twice(db_client):
    email = unique_email()
    await register(db_client, email)
    token_hash = await confirmation_token_hash(email)

    again = await db_client.get(
        "/api/auth/confirm", params={"token_hash": token_hash}, follow_redirects=False
    )

    assert again.status_code == 303
    assert again.headers["location"].endswith("/login.html?error=confirm")


async def test_resending_the_confirmation_is_accepted(db_client):
    email = unique_email()
    await db_client.post(
        "/api/auth/register/client",
        json={
            "email": email,
            "password": PASSWORD,
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )
    # The sign-up just sent one. `[auth.email] max_frequency` throttles the next mail to
    # the same address, and a resend inside that window is a 429 by design.
    await asyncio.sleep(1.2)

    response = await db_client.post(
        "/api/auth/resend-confirmation", json={"email": email}
    )

    assert response.status_code == 204


async def test_resending_for_an_unknown_address_says_nothing(db_client):
    """The one place registration's existence disclosure must not leak through."""
    response = await db_client.post(
        "/api/auth/resend-confirmation", json={"email": unique_email()}
    )

    assert response.status_code == 204


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


async def test_registering_a_confirmed_address_again_is_409(db_client):
    """The duplicate has to be *confirmed* before the provider will admit it exists.

    With confirmations on, signing up an address that exists but has not been confirmed
    is not an error at all: the provider re-sends the confirmation and answers 200 with
    the same auth user id, deliberately disclosing nothing. Only a confirmed address
    comes back as `user_already_exists`.
    """
    email = unique_email()
    await register(db_client, email)

    second = await db_client.post(
        "/api/auth/register/client",
        json={
            "email": email,
            "password": PASSWORD,
            "first_name": "Anna",
            "last_name": "Schmidt",
        },
    )

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
