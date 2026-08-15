from uuid import uuid4

from kummo import orm


def make_activity(**overrides) -> orm.Activity:
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
    return orm.Activity(**{**defaults, **overrides})


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


async def test_create_activity_persists_and_returns_201(client, stub_session):
    vendor_id = uuid4()
    payload = {
        "vendor_id": str(vendor_id),
        "title": "Kamishibai-Erzählstunde",
        "participants_max": 12,
        "duration": "45min",
    }

    response = await client.post("/api/activities", json=payload)

    assert response.status_code == 201
    assert stub_session.commits == 1
    assert len(stub_session.added) == 1
    added = stub_session.added[0]
    assert isinstance(added, orm.Activity)
    assert added.vendor_id == vendor_id
    assert added.title == "Kamishibai-Erzählstunde"
    # Default applied by ActivityCreate rather than the database.
    assert added.picture == "https://via.placeholder.com/400x250"


async def test_create_activity_requires_vendor_id(client, stub_session):
    response = await client.post(
        "/api/activities",
        json={"title": "Ohne Anbieter", "participants_max": 5, "duration": "1h"},
    )

    assert response.status_code == 422
    assert stub_session.commits == 0
