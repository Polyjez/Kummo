from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api import shops, activities

app = FastAPI(title="Kummo API", version="0.1.0")

app.include_router(shops.router, prefix="/api")
app.include_router(activities.router, prefix="/api")

# Serve static/ last so API routes take precedence
STATIC_DIR = Path(__file__).resolve().parents[3] / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
