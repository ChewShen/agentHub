"""AgentHub FastAPI application."""

from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe. Returns HTTP 200 when the API is running."""
    return {"status": "healthy"}
