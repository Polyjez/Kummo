"""Database connection, shared by every feature.

Connections are made as `kummo_app`, which holds DML privileges only. Schema changes
are Supabase CLI migrations — see `supabase/migrations/`. What the tables look like is
`data_model.py`'s business, not this module's.
"""

import logging
from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_engine() -> AsyncEngine:
    """The process-wide connection pool, built on first use."""
    settings = get_settings()
    logger.info("Creating database engine")
    return create_async_engine(settings.database_url, pool_pre_ping=True)


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a session scoped to one request."""
    async with get_sessionmaker()() as session:
        yield session


async def dispose_engine() -> None:
    """Close the pool on shutdown. A no-op if no engine was ever built."""
    if get_engine.cache_info().currsize == 0:
        return
    logger.info("Disposing database engine")
    await get_engine().dispose()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
