"""Unit tests for the LLM service (app/services/llm.py).

All tests mock the Gemini SDK — no real API calls are made.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services import llm
from app.services.llm import (
    LLMConfigError,
    LLMGenerationError,
    generate_response,
    init_llm_client,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_settings(**overrides: str) -> MagicMock:
    """Create a mock Settings object with sensible defaults."""
    defaults = {
        "gemini_api_key": "test-api-key",
        "gemini_model": "gemini-3.1-flash-lite",
    }
    defaults.update(overrides)
    settings = MagicMock()
    for key, value in defaults.items():
        setattr(settings, key, value)
    return settings


def _make_chunk(text: str | None) -> MagicMock:
    """Create a mock response chunk with optional text."""
    chunk = MagicMock()
    chunk.text = text
    return chunk


# ---------------------------------------------------------------------------
# init_llm_client
# ---------------------------------------------------------------------------


class TestInitLLMClient:
    """Tests for client initialisation."""

    @patch("app.services.llm.genai.Client")
    def test_initialises_client_successfully(self, mock_client_cls: MagicMock) -> None:
        """Client is created with the configured API key."""
        settings = _make_settings()
        init_llm_client(settings)

        mock_client_cls.assert_called_once_with(api_key="test-api-key")
        assert llm._client is mock_client_cls.return_value
        assert llm._model == "gemini-3.1-flash-lite"

    @patch("app.services.llm.genai.Client", side_effect=Exception("bad key"))
    def test_raises_config_error_on_failure(self, _mock: MagicMock) -> None:
        """LLMConfigError is raised if the client cannot be created."""
        settings = _make_settings()
        with pytest.raises(LLMConfigError, match="Failed to initialise Gemini client"):
            init_llm_client(settings)


# ---------------------------------------------------------------------------
# generate_response
# ---------------------------------------------------------------------------


class TestGenerateResponse:
    """Tests for async streaming generation."""

    @pytest.fixture(autouse=True)
    def _reset_client(self) -> None:
        """Reset module-level client state between tests."""
        llm._client = None
        llm._model = None

    @pytest.mark.asyncio
    async def test_raises_config_error_when_uninitialised(self) -> None:
        """Calling generate_response before init should raise LLMConfigError."""
        with pytest.raises(LLMConfigError, match="not been initialised"):
            async for _ in generate_response("hello"):
                pass

    @pytest.mark.asyncio
    async def test_yields_text_chunks(self) -> None:
        """Streamed text chunks from the API are yielded correctly."""
        chunks = [_make_chunk("Hello"), _make_chunk(", "), _make_chunk("world!")]

        mock_client = MagicMock()

        # Build an async iterator for the stream
        async def _async_iter() -> None:
            for c in chunks:
                yield c

        mock_client.aio.models.generate_content_stream = AsyncMock(
            return_value=_async_iter()
        )

        llm._client = mock_client
        llm._model = "test-model"

        collected: list[str] = []
        async for text in generate_response("test prompt"):
            collected.append(text)

        assert collected == ["Hello", ", ", "world!"]

    @pytest.mark.asyncio
    async def test_skips_empty_chunks(self) -> None:
        """Chunks with None text are skipped."""
        chunks = [_make_chunk("Hi"), _make_chunk(None), _make_chunk("!")]

        mock_client = MagicMock()

        async def _async_iter() -> None:
            for c in chunks:
                yield c

        mock_client.aio.models.generate_content_stream = AsyncMock(
            return_value=_async_iter()
        )

        llm._client = mock_client
        llm._model = "test-model"

        collected: list[str] = []
        async for text in generate_response("test"):
            collected.append(text)

        assert collected == ["Hi", "!"]

    @pytest.mark.asyncio
    async def test_raises_generation_error_on_api_failure(self) -> None:
        """LLMGenerationError is raised if the Gemini API call fails."""
        mock_client = MagicMock()
        mock_client.aio.models.generate_content_stream = AsyncMock(
            side_effect=Exception("rate limited")
        )

        llm._client = mock_client
        llm._model = "test-model"

        with pytest.raises(LLMGenerationError, match="Gemini generation failed"):
            async for _ in generate_response("test"):
                pass
