"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the AgentHub application.

    All values are read from environment variables (or a .env file).
    Fields without defaults will raise a validation error on startup
    if the corresponding env var is missing — this is intentional to
    fail fast on misconfiguration.
    """

    # Application
    app_name: str = "AgentHub"
    app_version: str = "0.1.0"
    debug: bool = False
    max_upload_size_mb: int = 5

    # PostgreSQL
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333

    # Gemini
    gemini_api_key: str
    gemini_model: str = "gemini-3.1-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-2"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def database_url(self) -> str:
        """Construct the async PostgreSQL URL from components."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


def get_settings() -> Settings:
    """Factory function for use as a FastAPI dependency."""
    return Settings()
