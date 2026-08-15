"""Alembic environment.

Runs as `kummo_migrator` and owns the `kummo` schema only. `auth.*` (GoTrue) and the
legacy `public.*` tables belong to the Supabase CLI migrations and are filtered out of
autogenerate so Alembic never proposes dropping them.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from kummo.config import get_settings
from kummo.data_model import SCHEMA, Entity

# Importing every feature's data model registers it on Entity.metadata. Without these
# imports autogenerate would see an empty schema and propose dropping everything.
from kummo.activities import data_model as _activities  # noqa: F401
from kummo.bookings import data_model as _bookings  # noqa: F401
from kummo.clients import data_model as _clients  # noqa: F401
from kummo.vendors import data_model as _vendors  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Entity.metadata


def include_object(obj, name, type_, reflected, compare_to) -> bool:
    if type_ == "table":
        return obj.schema == SCHEMA
    return True


def _configure(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        include_object=include_object,
        version_table_schema=SCHEMA,
        compare_type=True,
    )


def run_migrations_offline() -> None:
    context.configure(
        url=get_settings().migration_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_schemas=True,
        include_object=include_object,
        version_table_schema=SCHEMA,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _run(connection) -> None:
    _configure(connection)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(get_settings().migration_database_url)
    async with engine.connect() as connection:
        await connection.run_sync(_run)
        await connection.commit()
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
