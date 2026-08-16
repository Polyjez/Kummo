from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase Auth (GoTrue). Application data no longer goes through PostgREST,
    # but identity still does.
    supabase_url: str
    supabase_api_key: str

    # Runtime connection, as the DML-only `kummo_app` role. The backend never does
    # DDL -- schema changes are Supabase CLI migrations, applied out of band.
    database_url: str

    # Where this app is served. Used to build the OAuth callback URL and to decide
    # where to send the browser after a provider redirect.
    app_base_url: str = "http://localhost:8000"
    # Session cookies are HttpOnly always; Secure only where there is TLS to require.
    cookie_secure: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
