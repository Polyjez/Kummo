"""The SQLAlchemy data model must describe the database the migrations built.

This is what replaces Alembic autogenerate. With DDL written by hand in
`supabase/migrations/`, nothing mechanically ties the `kummo` schema to the entities
in `src/kummo/*/data_model.py`, and a column added to one but not the other would
otherwise surface as a query error at runtime. Reflecting the live schema catches the
drift here instead -- and against the database that was actually migrated, which is a
stronger check than a diff of generated DDL.

Add a migration *and* the matching `data_model.py` change, or this fails.
"""

import pytest
from sqlalchemy import inspect

from kummo.data_model import SCHEMA, Entity

# Importing every feature's data model registers it on Entity.metadata. Without these
# the registry is empty and the test would pass by comparing nothing.
from kummo.activities import data_model as _activities  # noqa: F401
from kummo.clients import data_model as _clients  # noqa: F401
from kummo.vendors import data_model as _vendors  # noqa: F401

pytestmark = pytest.mark.integration


async def _reflect(db_session) -> dict[str, dict[str, bool]]:
    """The live `kummo` schema as {table: {column: nullable}}."""

    def read(connection) -> dict[str, dict[str, bool]]:
        inspector = inspect(connection)
        return {
            table: {
                column["name"]: column["nullable"]
                for column in inspector.get_columns(table, schema=SCHEMA)
            }
            for table in inspector.get_table_names(schema=SCHEMA)
        }

    return await db_session.run_sync(lambda session: read(session.connection()))


def _declared() -> dict[str, dict[str, bool]]:
    """The same shape, taken from the declarative registry."""
    return {
        table.name: {column.name: column.nullable for column in table.columns}
        for table in Entity.metadata.tables.values()
    }


async def test_every_declared_table_exists(db_session):
    live = await _reflect(db_session)
    assert set(_declared()) <= set(live)


async def test_columns_match_the_declared_entities(db_session):
    live = await _reflect(db_session)
    declared = _declared()

    for table, columns in declared.items():
        assert columns == live[table], (
            f"kummo.{table} has drifted from its data_model: "
            f"database={live[table]}, declared={columns}"
        )


async def test_no_unmapped_tables_in_the_schema(db_session):
    """A table the migrations created but no entity maps is dead weight or an
    oversight. Failing here forces the decision rather than letting it linger."""
    live = await _reflect(db_session)
    assert set(live) == set(_declared())
