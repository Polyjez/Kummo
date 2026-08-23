"""Logging setup, shared by every feature.

Two things live here. First, the configuration: modules everywhere call
`logging.getLogger(__name__)`, but nothing ever attached a handler to the root logger,
so every one of those statements was discarded — uvicorn configures its *own* loggers
and leaves the root alone. `configure()` is what makes them appear.

Second, the request id. A log line is only useful if you can tell which request it
belongs to, and an async server interleaves them freely. The id lives in a
`ContextVar`, which follows the task across awaits, and a filter copies it onto every
record so the format string can print it without any call site passing it along.

Not named `logging.py`: that would shadow the standard library module this imports.
"""

import logging
import re
import uuid
from contextvars import ContextVar

# "-" reads better than "None" in a column, and marks the lines emitted outside a
# request — startup, shutdown, background work.
NO_REQUEST = "-"

_request_id: ContextVar[str] = ContextVar("request_id", default=NO_REQUEST)

FORMAT = "%(asctime)s [%(levelname)-5s] (%(name)s) %(request_id)s : %(message)s"
TIME_FORMAT = "%H:%M:%S"

# An inbound X-Request-ID is caller-supplied, so it is only reused if it looks like an
# id: anything else would let a caller write punctuation, newlines included, into every
# log line of its own request.
_SAFE_REQUEST_ID = re.compile(r"\A[A-Za-z0-9._-]{1,64}\Z")


class RequestIdFilter(logging.Filter):
    """Copies the current request id onto every record.

    A filter rather than a `LoggerAdapter` because it has to reach records from
    libraries too — SQLAlchemy, uvicorn, supabase — none of which know about us.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id.get()
        return True


def new_request_id(supplied: str | None = None) -> str:
    """The id for one request: the caller's if it is usable, otherwise a fresh one."""
    if supplied and _SAFE_REQUEST_ID.match(supplied):
        return supplied
    return uuid.uuid4().hex[:12]


def set_request_id(request_id: str):
    """Bind the id for the current task. Returns the token to reset with."""
    return _request_id.set(request_id)


def reset_request_id(token) -> None:
    _request_id.reset(token)


def current_request_id() -> str:
    return _request_id.get()


def configure(level: str = "INFO") -> None:
    """Attach a console handler to the root logger.

    Idempotent, because `fastapi dev` reloads on every edit and a second handler would
    double every line.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(FORMAT, datefmt=TIME_FORMAT))
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(level.upper())

    # uvicorn installs its own handlers; without this its records print twice, once
    # from its handler and once from ours after propagating up.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
