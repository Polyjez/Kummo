from uuid import uuid4

from kummo.vendors import data_model as vendors


def make_vendor(**overrides) -> vendors.Vendor:
    defaults = dict(
        id=uuid4(),
        name="Kreativwerkstatt Kreuzberg",
        address="Oranienstraße 1, 10999 Berlin",
        phone="+49 30 1234567",
        email="hallo@kreativwerkstatt.de",
        website="https://kreativwerkstatt.de",
        activity_type=["Basteln", "Malen"],
        picture="https://example.test/shop.jpg",
    )
    return vendors.Vendor(**{**defaults, **overrides})


async def test_list_vendors_returns_serialized_rows(client, stub_session):
    vendor = make_vendor()
    stub_session.rows = [vendor]

    response = await client.get("/api/vendors")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == str(vendor.id)
    assert body[0]["name"] == "Kreativwerkstatt Kreuzberg"
    assert body[0]["activity_type"] == ["Basteln", "Malen"]


async def test_list_vendors_empty(client, stub_session):
    response = await client.get("/api/vendors")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_vendors_omits_auth_user_id(client, stub_session):
    """auth_user_id is an internal link to Supabase Auth and must not be exposed."""
    stub_session.rows = [make_vendor(auth_user_id=uuid4())]

    response = await client.get("/api/vendors")

    assert "auth_user_id" not in response.json()[0]


async def test_list_vendors_allows_null_optional_fields(client, stub_session):
    stub_session.rows = [make_vendor(phone=None, website=None, picture=None)]

    body = (await client.get("/api/vendors")).json()[0]

    assert body["phone"] is None
    assert body["website"] is None
    assert body["picture"] is None
