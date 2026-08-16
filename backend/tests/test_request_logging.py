"""The request-id middleware, exercised through the app.

`tests/test_logs.py` covers the plumbing in isolation; what matters here is that a
real request binds an id, that the id reaches the lines the handlers emit, and that
the response carries it back so a user reporting a problem can quote it.
"""

import logging

import pytest

from kummo import logs
from kummo.main import REQUEST_ID_HEADER


@pytest.fixture
def captured(caplog):
    caplog.set_level(logging.INFO, logger="kummo")
    return caplog


async def test_a_response_carries_a_request_id(client, stub_session):
    response = await client.get("/api/vendors")

    assert logs._SAFE_REQUEST_ID.match(response.headers[REQUEST_ID_HEADER])


async def test_a_usable_supplied_id_is_echoed_back(client, stub_session):
    response = await client.get("/api/vendors", headers={REQUEST_ID_HEADER: "trace-abc"})

    assert response.headers[REQUEST_ID_HEADER] == "trace-abc"


async def test_an_unusable_supplied_id_is_replaced(client, stub_session):
    response = await client.get(
        "/api/vendors", headers={REQUEST_ID_HEADER: "not a valid id!"}
    )

    assert response.headers[REQUEST_ID_HEADER] != "not a valid id!"
    assert logs._SAFE_REQUEST_ID.match(response.headers[REQUEST_ID_HEADER])


async def test_each_request_gets_its_own_id(client, stub_session):
    first = await client.get("/api/vendors")
    second = await client.get("/api/vendors")

    assert first.headers[REQUEST_ID_HEADER] != second.headers[REQUEST_ID_HEADER]


async def test_the_outcome_of_an_api_call_is_logged(client, stub_session, captured):
    await client.get("/api/vendors")

    assert any(
        "GET /api/vendors -> 200" in record.message for record in captured.records
    )


async def test_a_client_error_is_logged_at_warning(client, stub_session, captured):
    """A 200 is traffic; a 4xx is the thing somebody will come asking about."""
    await client.post("/api/activities", json={"title": "Ohne Anmeldung"})

    failures = [r for r in captured.records if "POST /api/activities" in r.message]
    assert failures
    assert all(r.levelno == logging.WARNING for r in failures)


async def test_log_lines_carry_the_id_of_their_own_request(client, stub_session, captured):
    """The property the whole mechanism exists for."""
    response = await client.get(
        "/api/vendors", headers={REQUEST_ID_HEADER: "trace-xyz"}
    )

    # caplog has its own handler, without our filter — but a filter mutates the record
    # in place, and both handlers see the same object, so the stamp the root handler
    # applies is visible on the records caplog kept.
    matching = [
        r for r in captured.records if getattr(r, "request_id", None) == "trace-xyz"
    ]
    assert matching, "no log record carried the supplied request id"
    assert response.headers[REQUEST_ID_HEADER] == "trace-xyz"


async def test_the_id_does_not_leak_between_requests(client, stub_session, captured):
    await client.get("/api/vendors", headers={REQUEST_ID_HEADER: "first-req"})
    captured.clear()
    await client.get("/api/vendors", headers={REQUEST_ID_HEADER: "second-req"})

    ids = {getattr(r, "request_id", None) for r in captured.records}
    assert "first-req" not in ids


async def test_static_requests_are_not_logged_as_api_calls(client, stub_session, captured):
    """Static files are most of the traffic and say nothing worth a line each."""
    await client.get("/index.html")

    assert not any("-> 200" in record.message for record in captured.records)
