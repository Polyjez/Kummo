"""Fixtures for tests that talk to the real local Postgres.

Requires a running local Supabase (`pnpm exec supabase start`) with the schema applied
(`uv run alembic upgrade head`). Each test runs inside a transaction that is rolled
back, so the seed data is left untouched — including the routes' own `commit()`, which
lands on a savepoint thanks to `join_transaction_mode`.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from kummo.config import get_settings
from kummo.db import get_session
from kummo.main import app


@pytest.fixture
async def db_session():
    engine = create_async_engine(get_settings().database_url)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
    await engine.dispose()


@pytest.fixture
async def db_client(db_session):
    from httpx import ASGITransport, AsyncClient

    app.dependency_overrides[get_session] = lambda: db_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as async_client:
            yield async_client
    finally:
        app.dependency_overrides.clear()
