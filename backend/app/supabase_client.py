from supabase import Client, create_client

from app.config import settings

settings.validate_supabase()

# Service role key: the backend already authenticates the user itself (JWKS
# verification in app.dependencies) and scopes every query by user_id in code,
# so it talks to Postgres with elevated privileges rather than as the anon role.
_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def get_supabase() -> Client:
    """FastAPI dependency — returns the shared Supabase client."""
    return _client
