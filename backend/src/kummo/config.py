from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase Auth (GoTrue). Application data no longer goes through PostgREST,
    # but identity still does.
    supabase_url: str
    supabase_api_key: str

    # Runtime connection, as the DML-only `kummo_app` role.
    database_url: str
    # DDL connection, as `kummo_migrator`. Used by Alembic only.
    migration_database_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
