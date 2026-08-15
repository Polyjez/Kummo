"""Operational tasks, exposed as console scripts so `uv run <name>` drives them.

    uv run alembic upgrade head   # schema only
    uv run kummo-db-seed          # development data
    uv run kummo-db-reset         # supabase reset + upgrade + seed, in that order

Ordering is the reason `kummo-db-reset` exists: `supabase db reset` replays the CLI
migrations only, so the kummo tables do not exist until Alembic has run, which is why
seeding is no longer part of the reset itself (see [db.seed] in supabase/config.toml).
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path

import asyncpg
from alembic import command
from alembic.config import Config

from .config import get_settings

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent
SEED_FILE = REPO_ROOT / "supabase" / "seed.sql"


def _asyncpg_dsn(url: str) -> str:
    """Strip SQLAlchemy's driver marker; asyncpg wants a plain postgresql:// DSN."""
    return url.replace("postgresql+asyncpg://", "postgresql://", 1)


def _supabase_cli() -> list[str]:
    local = REPO_ROOT / "node_modules" / ".bin" / "supabase"
    if local.exists():
        return [str(local)]
    return ["npx", "--yes", "supabase"]


async def _apply_seed() -> None:
    sql = SEED_FILE.read_text(encoding="utf-8")
    connection = await asyncpg.connect(_asyncpg_dsn(get_settings().database_url))
    try:
        await connection.execute(sql)
    finally:
        await connection.close()


def db_seed() -> None:
    """Apply supabase/seed.sql to the kummo schema."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger.info("Seeding from %s", SEED_FILE)
    asyncio.run(_apply_seed())
    logger.info("Seed applied")


def db_upgrade() -> None:
    """Run Alembic migrations as kummo_migrator."""
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(config, "head")


def db_reset() -> None:
    """Rebuild the local database from scratch: reset, migrate, seed."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    logger.info("Resetting the local Supabase database")
    result = subprocess.run([*_supabase_cli(), "db", "reset"], cwd=REPO_ROOT)
    if result.returncode != 0:
        logger.error("supabase db reset failed; is Docker running?")
        sys.exit(result.returncode)

    logger.info("Applying Alembic migrations")
    db_upgrade()

    db_seed()
    logger.info("Database ready")
