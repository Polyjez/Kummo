"""End-to-end route tests against the kummo schema in a real Postgres.

These cover what the stubbed-session tests cannot: that the SQL is valid, that the
filters actually filter, and that the ORM mapping matches the migration.
"""

from uuid import uuid4

import pytest

from kummo import orm

pytestmark = pytest.mark.integration


async def seed_vendor(session, **overrides) -> orm.Vendor:
    vendor = orm.Vendor(
        **{
            "name": f"Testanbieter {uuid4().hex[:6]}",
            "address": "Teststraße 1, 10999 Berlin",
            "email": "test@example.de",
            "activity_type": ["Basteln"],
            **overrides,
        }
    )
    session.add(vendor)
    await session.flush()
    return vendor


async def seed_activity(session, vendor: orm.Vendor, **overrides) -> orm.Activity:
    activity = orm.Activity(
        **{
            "vendor_id": vendor.id,
            "title": f"Testaktivität {uuid4().hex[:6]}",
            "participants_max": 10,
            "duration": "1h",
            "picture": "https://example.test/a.jpg",
            **overrides,
        }
    )
    session.add(activity)
    await session.flush()
    return activity


async def test_list_vendors_includes_seeded_vendor(db_session, db_client):
    vendor = await seed_vendor(db_session)

    body = (await db_client.get("/api/vendors")).json()

    assert str(vendor.id) in [v["id"] for v in body]


async def test_activities_filter_by_vendor_id(db_session, db_client):
    vendor_a = await seed_vendor(db_session)
    vendor_b = await seed_vendor(db_session)
    activity_a = await seed_activity(db_session, vendor_a)
    await seed_activity(db_session, vendor_b)

    body = (
        await db_client.get("/api/activities", params={"vendor_id": str(vendor_a.id)})
    ).json()

    assert [a["id"] for a in body] == [str(activity_a.id)]


async def test_activities_filter_by_age_group(db_session, db_client):
    vendor = await seed_vendor(db_session)
    marker = uuid4().hex[:8]
    wanted = await seed_activity(db_session, vendor, age_group=marker)
    await seed_activity(db_session, vendor, age_group="0-5")

    body = (
        await db_client.get(
            "/api/activities", params={"vendor_id": str(vendor.id), "age_group": marker}
        )
    ).json()

    assert [a["id"] for a in body] == [str(wanted.id)]


async def test_create_activity_round_trips(db_session, db_client):
    vendor = await seed_vendor(db_session)

    created = await db_client.post(
        "/api/activities",
        json={
            "vendor_id": str(vendor.id),
            "title": "Neue Aktivität",
            "price": 19.5,
            "participants_max": 6,
            "duration": "90min",
        },
    )

    assert created.status_code == 201
    activity_id = created.json()["id"]

    fetched = await db_client.get(f"/api/activities/{activity_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Neue Aktivität"
    assert fetched.json()["vendor_id"] == str(vendor.id)


async def test_get_unknown_activity_returns_404(db_client):
    response = await db_client.get(f"/api/activities/{uuid4()}")

    assert response.status_code == 404
