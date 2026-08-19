"""The /metrics surface and the counters behind it.

Counters live in a process-wide registry and every other test in the session moves
them, so nothing here asserts an absolute value: each test measures the delta across
the request it makes. That is also the property that matters — a counter is only ever
read as a rate.
"""

from uuid import uuid4

import pytest
from prometheus_client import REGISTRY

from kummo import metrics
from kummo.auth import routes as auth_routes
from kummo.auth.dependencies import get_current_vendor
from kummo.auth.errors import InvalidCredentials
from kummo.auth.profiles import Profile
from kummo.auth.service import Session
from kummo.main import app

CREDENTIALS = {"email": "anna@example.de", "password": "ein-gutes-passwort"}

NEW_ACTIVITY = {
    "title": "Kamishibai-Erzählstunde",
    "participants_max": 12,
    "duration": "45min",
}


def sample(name: str, **labels) -> float:
    """The current value of one series, 0.0 before it has ever been touched."""
    value = REGISTRY.get_sample_value(name, labels)
    return 0.0 if value is None else value


def requests_counted(endpoint: str, method: str = "GET", status: str = "200") -> float:
    return sample(
        "kummo_http_requests_total", method=method, endpoint=endpoint, status=status
    )


def auth_events_counted(event: str, outcome: str = metrics.SUCCESS) -> float:
    return sample("kummo_auth_events_total", event=event, outcome=outcome)


@pytest.fixture
def signed_in_vendor():
    vendor = Profile(
        role="vendor",
        id=uuid4(),
        email="info@werkstatt.de",
        display_name="Kreativwerkstatt",
    )
    app.dependency_overrides[get_current_vendor] = lambda: vendor
    yield vendor
    app.dependency_overrides.pop(get_current_vendor, None)


# --- The scrape endpoint ----------------------------------------------------------


async def test_scrape_returns_the_prometheus_text_format(client):
    response = await client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "kummo_http_requests_total" in response.text


async def test_scrape_includes_the_default_process_collectors(client):
    """They come with the registry; the point is that we did not replace it."""
    response = await client.get("/metrics")

    assert "python_info" in response.text


async def test_scrape_is_reachable_without_a_session(client):
    """No cookie is sent here, and the endpoint is outside /api on purpose."""
    response = await client.get("/metrics")

    assert response.status_code == 200


async def test_a_scrape_does_not_count_itself(client):
    before = requests_counted("/metrics")
    await client.get("/metrics")
    after = requests_counted("/metrics")

    assert after == before


# --- HTTP metrics -----------------------------------------------------------------


async def test_a_request_is_counted_under_its_route_and_status(client, stub_session):
    before = requests_counted("/api/vendors")

    await client.get("/api/vendors")

    assert requests_counted("/api/vendors") == before + 1


async def test_the_duration_of_a_request_is_observed(client, stub_session):
    before = sample(
        "kummo_http_request_duration_seconds_count",
        method="GET",
        endpoint="/api/vendors",
    )

    await client.get("/api/vendors")

    after = sample(
        "kummo_http_request_duration_seconds_count",
        method="GET",
        endpoint="/api/vendors",
    )
    assert after == before + 1


async def test_path_parameters_collapse_into_the_route_template(client, stub_session):
    """The property the whole labelling scheme exists for: no series per activity id."""
    template = "/api/activities/{activity_id}"
    before = requests_counted(template, status="404")

    await client.get(f"/api/activities/{uuid4()}")
    await client.get(f"/api/activities/{uuid4()}")

    assert requests_counted(template, status="404") == before + 2


async def test_a_failing_status_is_its_own_series(client, stub_session):
    before = requests_counted("/api/activities", method="POST", status="401")

    await client.post("/api/activities", json=NEW_ACTIVITY)

    assert requests_counted("/api/activities", method="POST", status="401") == before + 1


async def test_a_path_that_matched_no_api_route_is_labelled_unmatched(client):
    """A 404 under /api is a caller mistake, not a route: it must not become a label."""
    before = requests_counted(metrics.UNMATCHED_ENDPOINT, status="404")

    await client.get("/api/does-not-exist")

    assert requests_counted(metrics.UNMATCHED_ENDPOINT, status="404") == before + 1


async def test_static_files_collapse_into_one_label(client):
    """Otherwise every asset the site serves would open a series of its own."""
    before = requests_counted(metrics.STATIC_ENDPOINT)

    await client.get("/index.html")

    assert requests_counted(metrics.STATIC_ENDPOINT) == before + 1


# --- Auth and domain counters -----------------------------------------------------


async def test_a_rejected_sign_in_is_counted_as_a_failure(
    client, stub_session, monkeypatch
):
    async def rejects(email, password):
        raise InvalidCredentials("Email or password is incorrect")

    monkeypatch.setattr(auth_routes.service, "sign_in", rejects)
    before = auth_events_counted(metrics.AUTH_LOGIN, metrics.FAILURE)

    response = await client.post("/api/auth/login", json=CREDENTIALS)

    assert response.status_code == 401
    assert auth_events_counted(metrics.AUTH_LOGIN, metrics.FAILURE) == before + 1


async def test_a_successful_sign_in_is_counted(client, stub_session, monkeypatch):
    async def accepts(email, password):
        return Session(
            access_token="access-token-value",
            refresh_token="refresh-token-value",
            expires_in=3600,
            auth_user_id=uuid4(),
            email=email,
            full_name=None,
        )

    monkeypatch.setattr(auth_routes.service, "sign_in", accepts)
    before = auth_events_counted(metrics.AUTH_LOGIN)

    response = await client.post("/api/auth/login", json=CREDENTIALS)

    assert response.status_code == 200
    assert auth_events_counted(metrics.AUTH_LOGIN) == before + 1


async def test_an_unknown_oauth_provider_is_counted_once_not_labelled(client):
    """The provider name is caller-supplied, so it must never become a label."""
    before = auth_events_counted(metrics.AUTH_OAUTH_START, metrics.FAILURE)

    await client.get("/api/auth/oauth/definitely-not-a-provider")

    assert (
        auth_events_counted(metrics.AUTH_OAUTH_START, metrics.FAILURE) == before + 1
    )
    assert "definitely-not-a-provider" not in (await client.get("/metrics")).text


async def test_creating_an_activity_is_counted(client, stub_session, signed_in_vendor):
    before = sample("kummo_activities_created_total")

    response = await client.post("/api/activities", json=NEW_ACTIVITY)

    assert response.status_code == 201
    assert sample("kummo_activities_created_total") == before + 1
