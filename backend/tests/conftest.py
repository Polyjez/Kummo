import os
from pathlib import Path

from dotenv import load_dotenv

# Settings fields are required, so they must exist before anything imports the app.
# The local environment file is the source of truth — integration tests need the real
# DATABASE_URL, and the rest only need the fields to be present.
REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env.local")


from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from kummo.db import get_session
from kummo.main import app


class StubSession:
    """Stands in for AsyncSession in route tests that do not need a database.

    Query construction is not interpreted — `scalars` returns whatever it was
    seeded with. Filtering and SQL correctness are covered by tests/integration/.
    """

    def __init__(self, rows: list | None = None, get_result: object | None = None):
        self.rows = rows or []
        self.get_result = get_result
        # Consumed in order, one per `scalar()` call; exhausted means "no row".
        self.scalar_results: list = []
        self.added: list = []
        self.commits = 0

    async def scalars(self, query):
        return iter(self.rows)

    async def scalar(self, query):
        if not self.scalar_results:
            return None
        return self.scalar_results.pop(0)

    async def get(self, model, primary_key):
        return self.get_result

    def add(self, instance) -> None:
        self.added.append(instance)

    async def commit(self) -> None:
        self.commits += 1

    async def refresh(self, instance) -> None:
        # Stand in for the server-side defaults a real flush would populate.
        if getattr(instance, "id", None) is None:
            instance.id = uuid4()


@pytest.fixture
def stub_session():
    session = StubSession()
    app.dependency_overrides[get_session] = lambda: session
    yield session
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client
