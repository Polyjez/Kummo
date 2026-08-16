from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .activities import routes as activities
from .auth import routes as auth
from .auth.tokens import reset_verifier_client
from .db import dispose_engine
from .vendors import routes as vendors


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await dispose_engine()
    reset_verifier_client()


app = FastAPI(title="Kummo API", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router, prefix="/api")
app.include_router(vendors.router, prefix="/api")
app.include_router(activities.router, prefix="/api")

# Serve static/ last so API routes take precedence
STATIC_DIR = Path(__file__).resolve().parents[3] / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
