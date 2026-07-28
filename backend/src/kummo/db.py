from supabase import Client, create_client
from .config import Settings


def get_supabase(settings: Settings) -> Client:
    return create_client(settings.supabase_url, settings.supabase_anon_key)
