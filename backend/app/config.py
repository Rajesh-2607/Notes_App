from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    # Server-side only secret (bypasses Row Level Security). The backend verifies
    # users itself via JWT and enforces user_id scoping in code, so it needs this
    # to talk to Postgres through Supabase's REST layer. Never send this to the frontend.
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSIONS: int = 768
    # Comma-separated list of allowed frontend origins, e.g.
    # "http://localhost:5173,https://your-app.vercel.app"
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def validate_supabase(self) -> None:
        if not self.SUPABASE_URL or not self.SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required. "
                "Copy .env.example to .env and fill in your Supabase project settings."
            )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
