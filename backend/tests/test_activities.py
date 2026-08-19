from uuid import uuid4

import pytest

from kummo.activities import data_model as activities
from kummo.auth.dependencies import get_current_profile, get_current_vendor
from kummo.auth.profiles import Profile
from kummo.main import app


def make_activity(**overrides) -> activities.Activity:
    defaults = dict(
        id=uuid4(),
        vendor_id=uuid4(),
        title="Töpferkurs für Kinder",
        description="Ein Nachmittag an der Töpferscheibe.",
        price=25.0,
        participants_max=8,
        duration="2h",
        age_group="6-10",
        picture="https://example.test/activity.jpg",
    )
    return activities.Activity(**{**defaults, **overrides})


async def test_list_activities_returns_serialized_rows(client, stub_session):
    activity = make_activity()
    stub_session.rows = [activity]

    response = await client.get("/api/activities")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["id"] == str(activity.id)
    assert body[0]["vendor_id"] == str(activity.vendor_id)
    assert body[0]["title"] == "Töpferkurs für Kinder"


async def test_list_activities_rejects_non_uuid_vendor_id(client, stub_session):
    response = await client.get("/api/activities", params={"vendor_id": "not-a-uuid"})

    assert response.status_code == 422


async def test_get_activity_returns_the_row(client, stub_session):
    activity = make_activity()
    stub_session.get_result = activity

    response = await client.get(f"/api/activities/{activity.id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Töpferkurs für Kinder"


async def test_get_activity_missing_returns_404(client, stub_session):
    stub_session.get_result = None

    response = await client.get(f"/api/activities/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# --- Creating an activity ---------------------------------------------------------
#
# Writing is the one part of this surface that is not public: the owner comes from the
# session, so the route cannot be used to file an activity under another business.

NEW_ACTIVITY = {
    "title": "Kamishibai-Erzählstunde",
    "participants_max": 12,
    "duration": "45min",
}


@pytest.fixture
def signed_in_vendor():
    """Puts a vendor behind the route's `get_current_vendor` guard."""
    vendor = Profile(
        role="vendor",
        id=uuid4(),
        email="info@werkstatt.de",
        display_name="Kreativwerkstatt",
    )
    app.dependency_overrides[get_current_vendor] = lambda: vendor
    yield vendor
    app.dependency_overrides.pop(get_current_vendor, None)


async def test_create_activity_persists_and_returns_201(
    client, stub_session, signed_in_vendor
):
    response = await client.post("/api/activities", json=NEW_ACTIVITY)

    assert response.status_code == 201
    assert stub_session.commits == 1
    assert len(stub_session.added) == 1
    added = stub_session.added[0]
    assert isinstance(added, activities.Activity)
    assert added.vendor_id == signed_in_vendor.id
    assert added.title == "Kamishibai-Erzählstunde"
    # Default applied by ActivityCreate rather than the database.
    assert added.picture == "https://via.placeholder.com/400x250"


async def test_create_activity_ignores_a_vendor_id_in_the_body(
    client, stub_session, signed_in_vendor
):
    """The owner is not a caller-supplied field, so a forged one must not take effect."""
    somebody_else = uuid4()

    response = await client.post(
        "/api/activities", json={**NEW_ACTIVITY, "vendor_id": str(somebody_else)}
    )

    assert response.status_code == 201
    added = stub_session.added[0]
    assert added.vendor_id == signed_in_vendor.id
    assert added.vendor_id != somebody_else


async def test_create_activity_anonymously_is_401(client, stub_session):
    response = await client.post("/api/activities", json=NEW_ACTIVITY)

    assert response.status_code == 401
    assert stub_session.commits == 0
    assert stub_session.added == []


async def test_create_activity_as_a_client_is_403(client, stub_session):
    profile = Profile(
        role="client", id=uuid4(), email="anna@example.de", display_name="Anna Schmidt"
    )
    app.dependency_overrides[get_current_profile] = lambda: profile
    try:
        response = await client.post("/api/activities", json=NEW_ACTIVITY)
    finally:
        app.dependency_overrides.pop(get_current_profile, None)

    assert response.status_code == 403
    assert stub_session.added == []
