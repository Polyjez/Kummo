import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from . import logs
from .activities import routes as activities
from .auth import routes as auth
from .auth.tokens import reset_verifier_client
from .config import get_settings
from .db import dispose_engine
from .vendors import routes as vendors

# Before anything else logs: get_settings() itself can fail, and that message is the
# one you most need to see.
logs.configure(get_settings().log_level)

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"

# Static files are the bulk of the traffic and say nothing worth a line each.
API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(
        "Kummo API starting (base url %s, secure cookies %s)",
        settings.app_base_url,
        settings.cookie_secure,
    )
    yield
    logger.info("Kummo API shutting down")
    await dispose_engine()
    reset_verifier_client()


app = FastAPI(title="Kummo API", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def request_context(request: Request, call_next):
    """Give every request an id, and log how each API call turned out.

    The id is bound to the task, so anything logged while handling this request
    carries it without the call sites knowing — including SQLAlchemy and httpx.
    """
    request_id = logs.new_request_id(request.headers.get(REQUEST_ID_HEADER))
    token = logs.set_request_id(request_id)
    started = time.perf_counter()
    is_api = request.url.path.startswith(API_PREFIX)
    try:
        try:
            response = await call_next(request)
        except Exception:
            # The handler will re-raise into Starlette's 500; this is the only place
            # the failure is tied to its request id.
            logger.exception(
                "%s %s failed after %.0fms",
                request.method,
                request.url.path,
                (time.perf_counter() - started) * 1000,
            )
            raise

        if is_api:
            # Logged before the id is released, or the one line worth correlating
            # would be the one without an id on it.
            level = logging.WARNING if response.status_code >= 400 else logging.INFO
            logger.log(
                level,
                "%s %s -> %d (%.0fms)",
                request.method,
                request.url.path,
                response.status_code,
                (time.perf_counter() - started) * 1000,
            )
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
    finally:
        logs.reset_request_id(token)


app.include_router(auth.router, prefix="/api")
app.include_router(vendors.router, prefix="/api")
app.include_router(activities.router, prefix="/api")

# Serve static/ last so API routes take precedence
STATIC_DIR = Path(__file__).resolve().parents[3] / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
