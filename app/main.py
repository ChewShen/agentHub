"""AgentHub FastAPI application."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import close_db, init_db
from app.routers.chat import router as chat_router
from app.routers.documents import router as documents_router
from app.services.embedding import init_embedding_client
from app.services.llm import init_llm_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — initialise shared resources on startup."""
    settings = get_settings()
    init_llm_client(settings)
    init_embedding_client(settings)
    logger.info("LLM and Embedding clients initialised (model=%s, emb_model=%s)", settings.gemini_model, settings.gemini_embedding_model)
    await init_db()
    yield
    await close_db()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(chat_router)
app.include_router(documents_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe. Returns HTTP 200 when the API is running."""
    return {"status": "healthy"}
