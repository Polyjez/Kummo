"""Profile linking against the real schema.

The unique constraint on `auth_user_id` is the thing under test here, so a stubbed
session would prove nothing — these need real Postgres.
"""

from uuid import uuid4

import pytest

from kummo.auth.profiles import (
    ensure_client_profile,
    ensure_vendor_profile,
    find_profile,
)
from kummo.auth.tokens import Identity

pytestmark = pytest.mark.integration


def make_identity() -> Identity:
    return Identity(auth_user_id=uuid4(), email=f"anna-{uuid4().hex[:8]}@example.de")


async def test_a_new_identity_gets_a_client_profile(db_session):
    identity = make_identity()

    profile = await ensure_client_profile(db_session, identity, "Anna", "Schmidt")

    assert profile.role == "client"
    assert profile.display_name == "Anna Schmidt"
    assert profile.email == identity.email


async def test_a_new_identity_gets_a_vendor_profile(db_session):
    identity = make_identity()

    profile = await ensure_vendor_profile(
        db_session,
        identity,
        name="Kreativwerkstatt",
        address="Oranienstraße 1, 10999 Berlin",
        activity_type=["kunst"],
    )

    assert profile.role == "vendor"
    assert profile.display_name == "Kreativwerkstatt"


async def test_ensuring_twice_does_not_create_a_second_profile(db_session):
    """`ensure_*` is the entry path for register, login and the OAuth callback, so it
    runs repeatedly for the same identity by design."""
    identity = make_identity()

    first = await ensure_client_profile(db_session, identity, "Anna", "Schmidt")
    second = await ensure_client_profile(db_session, identity, "Andere", "Person")

    assert first.id == second.id
    # The second call must not overwrite the profile either.
    assert second.display_name == "Anna Schmidt"


async def test_a_concurrent_insert_is_absorbed_rather_than_raised(db_session):
    """Regression: two requests racing past the `find_profile` check both inserted,
    and the loser hit the unique constraint as an unhandled 500. Losing the race
    means the profile exists, which is what the caller asked for.

    The race is simulated by inserting the row behind `ensure_*`'s back, between its
    lookup and its commit — which is exactly the window the real race opens.
    """
    from kummo.clients import data_model as clients

    identity = make_identity()
    db_session.add(
        clients.Client(
            auth_user_id=identity.auth_user_id,
            first_name="Anna",
            last_name="Schmidt",
            email=identity.email,
        )
    )
    await db_session.commit()

    # A caller that read "no profile" a moment earlier now tries to insert.
    row = clients.Client(
        auth_user_id=identity.auth_user_id,
        first_name="Anna",
        last_name="Schmidt",
        email=identity.email,
    )
    from kummo.auth.profiles import _as_client_profile, _insert_profile

    profile = await _insert_profile(
        db_session, row, identity.auth_user_id, _as_client_profile
    )

    assert profile.role == "client"
    assert profile.display_name == "Anna Schmidt"


async def test_find_profile_returns_none_for_an_unlinked_identity(db_session):
    assert await find_profile(db_session, uuid4()) is None
