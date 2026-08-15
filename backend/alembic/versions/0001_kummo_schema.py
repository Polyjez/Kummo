"""Create the kummo schema tables.

Supersedes the legacy public.* tables, which the Supabase CLI migration
20260815120000_drop-legacy-public-tables.sql drops.

Two shape changes come with the move:
  - `shops` becomes `vendors`: a vendor is the business identity *and* the shop.
  - profile tables gain `auth_user_id`, linking them to a Supabase Auth user.
    Unique, but no foreign key — `auth.users` belongs to GoTrue's own role and
    `kummo_migrator` has no privileges in that schema.

Revision ID: 0001_kummo_schema
Revises:
Create Date: 2026-08-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_kummo_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kummo"

_UUID = postgresql.UUID(as_uuid=True)
_TS = postgresql.TIMESTAMP(timezone=True)
_TEXT_ARRAY = postgresql.ARRAY(sa.Text())


def upgrade() -> None:
    # The schema itself belongs to 20260804155602_kummo-backend.sql, which creates it
    # with `authorization kummo_migrator`. Creating it here would need CREATE on the
    # database, which kummo_migrator does not have -- and Postgres checks that
    # privilege before the IF NOT EXISTS short-circuit, so it fails either way.
    op.create_table(
        "vendors",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", _TS, nullable=False, server_default=sa.text("now()")),
        sa.Column("auth_user_id", _UUID, nullable=True, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("phone", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("website", sa.Text(), nullable=True),
        sa.Column("activity_type", _TEXT_ARRAY, nullable=False),
        sa.Column("picture", sa.Text(), nullable=True),
        schema=SCHEMA,
    )

    op.create_table(
        "clients",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", _TS, nullable=False, server_default=sa.text("now()")),
        sa.Column("auth_user_id", _UUID, nullable=True, unique=True),
        sa.Column("first_name", sa.Text(), nullable=False),
        sa.Column("last_name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        # Enrichment fields: not collected at registration.
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("interests", _TEXT_ARRAY, nullable=True),
        sa.Column("number_children", sa.Integer(), nullable=True),
        schema=SCHEMA,
    )

    op.create_table(
        "activities",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", _TS, nullable=False, server_default=sa.text("now()")),
        sa.Column("vendor_id", _UUID, sa.ForeignKey(f"{SCHEMA}.vendors.id"), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", postgresql.REAL(), nullable=True),
        sa.Column("participants_max", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Text(), nullable=False),
        sa.Column("age_group", sa.Text(), nullable=True),
        sa.Column("picture", sa.Text(), nullable=False),
        schema=SCHEMA,
    )

    op.create_table(
        "bookings",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", _TS, nullable=False, server_default=sa.text("now()")),
        sa.Column("client_id", _UUID, sa.ForeignKey(f"{SCHEMA}.clients.id"), nullable=False),
        sa.Column("vendor_id", _UUID, sa.ForeignKey(f"{SCHEMA}.vendors.id"), nullable=False),
        sa.Column("slot", sa.Text(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("total_price", postgresql.REAL(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        schema=SCHEMA,
    )

    # The default privileges from 20260804155602_kummo-backend.sql cover tables created
    # by kummo_migrator, but grant explicitly so this migration stands on its own.
    op.execute(
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {SCHEMA} TO kummo_app"
    )


def downgrade() -> None:
    for table in ("bookings", "activities", "clients", "vendors"):
        op.drop_table(table, schema=SCHEMA)
