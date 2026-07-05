"""Database setup and session management."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# We configure the engine with pool_pre_ping to check connection liveness
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def init_db() -> None:
    """Initialize database connection. Called during lifespan."""
    # We do not call create_all() here because we are using Alembic for migrations.
    logger.info("Database engine initialized.")

async def close_db() -> None:
    """Close database connection. Called during lifespan shutdown."""
    await engine.dispose()
    logger.info("Database engine disposed.")

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session."""
    async with async_session_maker() as session:
        yield session
