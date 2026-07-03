"""Gemini LLM service — wraps the google-genai SDK for chat completions.

Responsibilities:
- Manage the Gemini client lifecycle (create once, reuse across requests)
- Construct prompts with system instructions
- Stream responses as async generators
- Map SDK errors to domain-specific exceptions
"""

from collections.abc import AsyncGenerator

from google import genai
from google.genai import types

from app.core.config import Settings


# ---------------------------------------------------------------------------
# System prompt — basic knowledge-assistant persona for V1
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are AgentHub, a helpful AI assistant. "
    "Answer questions clearly and concisely. "
    "If you don't know something, say so — do not make things up."
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class LLMError(Exception):
    """Base exception for LLM service errors."""


class LLMConfigError(LLMError):
    """Raised when the LLM client cannot be configured (e.g. bad API key)."""


class LLMGenerationError(LLMError):
    """Raised when content generation fails (rate limit, network, etc.)."""


# ---------------------------------------------------------------------------
# Client lifecycle
# ---------------------------------------------------------------------------

# Module-level client reference, initialised once via init_llm_client().
_client: genai.Client | None = None
_model: str | None = None


def init_llm_client(settings: Settings) -> None:
    """Create the Gemini client from application settings.

    Called once during FastAPI lifespan startup. Raises LLMConfigError
    if the client cannot be created.
    """
    global _client, _model  # noqa: PLW0603

    try:
        _client = genai.Client(api_key=settings.gemini_api_key)
        _model = settings.gemini_model
    except Exception as exc:
        raise LLMConfigError(f"Failed to initialise Gemini client: {exc}") from exc


def _get_client() -> genai.Client:
    """Return the initialised client or raise if not yet configured."""
    if _client is None:
        raise LLMConfigError(
            "LLM client has not been initialised. "
            "Did the application lifespan start correctly?"
        )
    return _client


# ---------------------------------------------------------------------------
# Core generation
# ---------------------------------------------------------------------------


async def generate_response(message: str) -> AsyncGenerator[str, None]:
    """Stream a Gemini response for the given user message.

    Yields text chunks as they arrive from the Gemini API.

    Raises:
        LLMGenerationError: If the Gemini API call fails.
    """
    client = _get_client()

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
    )

    try:
        stream = await client.aio.models.generate_content_stream(
            model=_model,
            contents=message,
            config=config,
        )

        async for chunk in stream:
            if chunk.text:
                yield chunk.text

    except Exception as exc:
        raise LLMGenerationError(
            f"Gemini generation failed: {exc}"
        ) from exc
