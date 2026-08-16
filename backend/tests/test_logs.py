"""Logging setup and the request-id plumbing.

The point of these is that a log line can be traced to the request that produced it,
so what is tested is the binding and the isolation between concurrent tasks — not the
wording of any particular message.
"""

import asyncio
import logging

import pytest

from kummo import logs


@pytest.fixture
def restore_logging():
    """`configure()` mutates the root logger, so put it back afterwards."""
    root = logging.getLogger()
    saved = (list(root.handlers), root.level)
    yield
    root.handlers = saved[0]
    root.setLevel(saved[1])


# --- Request ids ------------------------------------------------------------------


def test_a_supplied_id_is_reused_so_a_caller_can_correlate():
    assert logs.new_request_id("abc-123_XY.z") == "abc-123_XY.z"


@pytest.mark.parametrize(
    "supplied",
    [
        None,
        "",
        "has spaces",
        "has\nnewline",
        "punctuation!",
        "x" * 65,  # longer than the cap
    ],
)
def test_an_unusable_supplied_id_is_replaced(supplied):
    """The header is caller-controlled and lands in every line of its own request, so
    anything that is not plainly an id gets one generated instead."""
    generated = logs.new_request_id(supplied)

    assert generated != supplied
    assert logs._SAFE_REQUEST_ID.match(generated)


def test_generated_ids_differ():
    assert logs.new_request_id() != logs.new_request_id()


def test_outside_a_request_the_id_reads_as_absent():
    assert logs.current_request_id() == logs.NO_REQUEST


def test_the_id_is_bound_and_released():
    token = logs.set_request_id("req-1")
    try:
        assert logs.current_request_id() == "req-1"
    finally:
        logs.reset_request_id(token)

    assert logs.current_request_id() == logs.NO_REQUEST


async def test_concurrent_tasks_do_not_share_an_id():
    """The whole point of a ContextVar over a global: two requests in flight at once
    must not read each other's id."""
    seen = {}

    async def handle(name: str, delay: float):
        token = logs.set_request_id(name)
        try:
            await asyncio.sleep(delay)
            seen[name] = logs.current_request_id()
        finally:
            logs.reset_request_id(token)

    await asyncio.gather(handle("first", 0.02), handle("second", 0.01))

    assert seen == {"first": "first", "second": "second"}


# --- The filter -------------------------------------------------------------------


def make_record() -> logging.LogRecord:
    return logging.LogRecord("kummo.test", logging.INFO, __file__, 1, "hello", (), None)


def test_the_filter_stamps_the_current_id_onto_a_record():
    token = logs.set_request_id("req-42")
    try:
        record = make_record()
        logs.RequestIdFilter().filter(record)
    finally:
        logs.reset_request_id(token)

    assert record.request_id == "req-42"


def test_the_filter_stamps_records_from_outside_a_request_too():
    """Library records reach this filter as well, so it must never raise."""
    record = make_record()

    assert logs.RequestIdFilter().filter(record) is True
    assert record.request_id == logs.NO_REQUEST


def test_the_format_string_renders_with_a_stamped_record():
    record = make_record()
    logs.RequestIdFilter().filter(record)

    rendered = logging.Formatter(logs.FORMAT, datefmt=logs.TIME_FORMAT).format(record)

    assert logs.NO_REQUEST in rendered
    assert "kummo.test" in rendered
    assert "hello" in rendered


# --- configure() ------------------------------------------------------------------


def test_configure_attaches_exactly_one_handler(restore_logging):
    logs.configure("INFO")
    logs.configure("INFO")  # `fastapi dev` reloads; a second call must not double up.

    assert len(logging.getLogger().handlers) == 1


def test_configure_sets_the_requested_level(restore_logging):
    logs.configure("warning")

    assert logging.getLogger().level == logging.WARNING


def test_application_logs_actually_come_out(restore_logging, capsys):
    """The regression guard for the whole point of this module: without `configure`,
    every one of these statements went nowhere."""
    logs.configure("INFO")

    logging.getLogger("kummo.somewhere").info("a thing happened")

    assert "a thing happened" in capsys.readouterr().err
