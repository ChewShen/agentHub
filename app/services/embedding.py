"""Gemini Embedding service.

Responsibilities:
- Manage the Gemini client for embeddings (create once, reuse)
- Generate embeddings for single texts or lists of texts
- Map SDK errors to domain-specific exceptions
"""

import logging
from collections.abc import Sequence

from google import genai

from app.core.config import Settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class EmbeddingError(Exception):
    """Base exception for embedding service errors."""

class EmbeddingConfigError(EmbeddingError):
    """Raised when the embedding client cannot be configured."""

class EmbeddingGenerationError(EmbeddingError):
    """Raised when embedding generation fails."""


# ---------------------------------------------------------------------------
# Client lifecycle
# ---------------------------------------------------------------------------

_client: genai.Client | None = None
_model: str | None = None


def init_embedding_client(settings: Settings) -> None:
    """Create the Gemini client for embeddings from application settings."""
    global _client, _model  # noqa: PLW0603

    try:
        _client = genai.Client(api_key=settings.gemini_api_key)
        _model = settings.gemini_embedding_model
    except Exception as exc:
        raise EmbeddingConfigError(f"Failed to initialise embedding client: {exc}") from exc


def _get_client() -> genai.Client:
    """Return the initialised client or raise if not yet configured."""
    if _client is None:
        raise EmbeddingConfigError(
            "Embedding client has not been initialised. "
            "Did the application lifespan start correctly?"
        )
    return _client


# ---------------------------------------------------------------------------
# Core generation
# ---------------------------------------------------------------------------

async def embed_text(text: str) -> list[float]:
    """Generate an embedding for a single string.

    Args:
        text: The text to embed.

    Returns:
        A list of floats representing the embedding vector.

    Raises:
        EmbeddingGenerationError: If the Gemini API call fails.
    """
    if not text.strip():
        # Avoid unnecessary API call for empty text
        return []

    client = _get_client()
    try:
        response = await client.aio.models.embed_content(
            model=_model,
            contents=text,
        )
        if not response.embeddings or not response.embeddings[0].values:
            raise EmbeddingGenerationError("Received empty embedding from API.")
        
        return list(response.embeddings[0].values)
    except Exception as exc:
        logger.error("Failed to generate embedding: %s", exc)
        raise EmbeddingGenerationError(f"Gemini embedding failed: {exc}") from exc


async def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    """Generate embeddings for multiple strings.

    Args:
        texts: A list of text strings to embed.

    Returns:
        A list of embedding vectors corresponding to the input texts.

    Raises:
        EmbeddingGenerationError: If the Gemini API call fails.
    """
    if not texts:
        return []

    client = _get_client()
    try:
        response = await client.aio.models.embed_content(
            model=_model,
            contents=texts,
        )
        if not response.embeddings or len(response.embeddings) != len(texts):
            raise EmbeddingGenerationError("Mismatch between number of inputs and embeddings returned.")
        
        return [list(e.values) for e in response.embeddings]
    except Exception as exc:
        logger.error("Failed to generate embeddings batch: %s", exc)
        raise EmbeddingGenerationError(f"Gemini embedding batch failed: {exc}") from exc
