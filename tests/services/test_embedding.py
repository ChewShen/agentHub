"""Unit tests for the embedding service.

Tests mock the Gemini SDK to avoid real API calls.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services import embedding
from app.services.embedding import (
    EmbeddingConfigError,
    EmbeddingGenerationError,
    embed_text,
    embed_texts,
    init_embedding_client,
)


def _make_settings(**overrides: str) -> MagicMock:
    defaults = {
        "gemini_api_key": "test-api-key",
        "gemini_embedding_model": "text-embedding-004",
    }
    defaults.update(overrides)
    settings = MagicMock()
    for key, value in defaults.items():
        setattr(settings, key, value)
    return settings


class TestInitEmbeddingClient:
    
    @patch("app.services.embedding.genai.Client")
    def test_initialises_client_successfully(self, mock_client_cls: MagicMock) -> None:
        settings = _make_settings()
        init_embedding_client(settings)

        mock_client_cls.assert_called_once_with(api_key="test-api-key")
        assert embedding._client is mock_client_cls.return_value
        assert embedding._model == "text-embedding-004"

    @patch("app.services.embedding.genai.Client", side_effect=Exception("bad key"))
    def test_raises_config_error_on_failure(self, _mock: MagicMock) -> None:
        settings = _make_settings()
        with pytest.raises(EmbeddingConfigError, match="Failed to initialise embedding client"):
            init_embedding_client(settings)


class TestEmbedText:

    @pytest.fixture(autouse=True)
    def _reset_client(self) -> None:
        embedding._client = None
        embedding._model = None

    @pytest.mark.asyncio
    async def test_raises_config_error_when_uninitialised(self) -> None:
        with pytest.raises(EmbeddingConfigError, match="not been initialised"):
            await embed_text("hello")

    @pytest.mark.asyncio
    async def test_empty_text_returns_empty_list(self) -> None:
        assert await embed_text("   ") == []

    @pytest.mark.asyncio
    async def test_embed_text_success(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1, 0.2, 0.3]
        mock_response.embeddings = [mock_embedding]
        
        mock_client.aio.models.embed_content = AsyncMock(return_value=mock_response)
        
        embedding._client = mock_client
        embedding._model = "test-model"

        result = await embed_text("hello")
        
        assert result == [0.1, 0.2, 0.3]
        mock_client.aio.models.embed_content.assert_called_once_with(
            model="test-model",
            contents="hello",
        )

    @pytest.mark.asyncio
    async def test_embed_texts_success(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        
        mock_emb1 = MagicMock()
        mock_emb1.values = [0.1, 0.2]
        mock_emb2 = MagicMock()
        mock_emb2.values = [0.3, 0.4]
        
        mock_response.embeddings = [mock_emb1, mock_emb2]
        
        mock_client.aio.models.embed_content = AsyncMock(return_value=mock_response)
        
        embedding._client = mock_client
        embedding._model = "test-model"

        texts = ["hello", "world"]
        result = await embed_texts(texts)
        
        assert len(result) == 2
        assert result[0] == [0.1, 0.2]
        assert result[1] == [0.3, 0.4]
