"""Integration tests for POST /chat endpoint.

The LLM service is mocked at the service boundary — no real API calls.
"""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.llm import LLMConfigError, LLMGenerationError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _fake_stream(message: str) -> AsyncGenerator[str, None]:
    """Simulate a streamed LLM response."""
    for word in ["Hello", " from", " AgentHub!"]:
        yield word


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestChatEndpoint:
    """Integration tests for the /chat route."""

    @pytest.fixture
    def transport(self) -> ASGITransport:
        return ASGITransport(app=app)

    @pytest.mark.asyncio
    @patch("app.routers.chat.generate_response_full", new_callable=AsyncMock)
    async def test_chat_without_document_id(
        self, mock_generate: AsyncMock, transport: ASGITransport
    ) -> None:
        """POST /chat with a valid message returns 200 with JSON response and empty sources."""
        mock_generate.return_value = "Hello from AgentHub!"

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/chat", json={"message": "Hello!"})

        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello from AgentHub!"
        assert data["sources"] == []
        mock_generate.assert_called_once_with("Hello!", chunks=None)

    @pytest.mark.asyncio
    @patch("app.routers.chat.generate_response_full", new_callable=AsyncMock)
    @patch("app.routers.chat.retrieve_top_k", new_callable=AsyncMock)
    @patch("app.routers.chat.embed_text", new_callable=AsyncMock)
    async def test_chat_with_document_id_success(
        self, mock_embed: AsyncMock, mock_retrieve: AsyncMock, mock_generate: AsyncMock, transport: ASGITransport
    ) -> None:
        """POST /chat with document_id retrieves chunks and returns JSON response with sources."""
        import uuid
        from app.services.retrieval import ScoredChunk
        from app.models.document import Chunk
        
        doc_id = str(uuid.uuid4())
        
        mock_embed.return_value = [0.1, 0.2]
        
        c1 = Chunk(chunk_index=0, text="chunk 1", source_filename="test.pdf")
        c2 = Chunk(chunk_index=1, text="chunk 2", source_filename="test.pdf")
        mock_retrieve.return_value = [ScoredChunk(chunk=c1, score=0.9), ScoredChunk(chunk=c2, score=0.8)]
        
        mock_generate.return_value = "Based on the document..."
        
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/chat", json={"message": "Hi", "document_id": doc_id})
            
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Based on the document..."
        assert len(data["sources"]) == 2
        assert data["sources"][0]["text"] == "chunk 1"
        assert data["sources"][0]["score"] == 0.9
        
        mock_embed.assert_called_once_with("Hi")
        mock_retrieve.assert_called_once()
        mock_generate.assert_called_once_with("Hi", chunks=["chunk 1", "chunk 2"])

    @pytest.mark.asyncio
    @patch("app.routers.chat.retrieve_top_k", new_callable=AsyncMock)
    @patch("app.routers.chat.embed_text", new_callable=AsyncMock)
    async def test_chat_with_invalid_document_id(
        self, mock_embed: AsyncMock, mock_retrieve: AsyncMock, transport: ASGITransport
    ) -> None:
        """POST /chat with document_id not found returns 404."""
        import uuid
        doc_id = str(uuid.uuid4())
        
        mock_embed.return_value = [0.1, 0.2]
        mock_retrieve.return_value = []
        
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/chat", json={"message": "Hi", "document_id": doc_id})
            
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "DOCUMENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_chat_rejects_empty_message(self, transport: ASGITransport) -> None:
        """POST /chat with an empty message returns 422 validation error."""
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/chat", json={"message": ""})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_rejects_missing_message(self, transport: ASGITransport) -> None:
        """POST /chat with no message field returns 422 validation error."""
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/chat", json={})

        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch("app.routers.chat.generate_response_full", new_callable=AsyncMock)
    async def test_chat_returns_503_on_config_error(
        self, mock_generate: AsyncMock, transport: ASGITransport
    ) -> None:
        """POST /chat returns 503 when the LLM client is not configured."""
        mock_generate.side_effect = LLMConfigError("not configured")

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/chat", json={"message": "Hi"})

        assert response.status_code == 503
        body = response.json()
        assert body["detail"]["code"] == "LLM_NOT_CONFIGURED"

    @pytest.mark.asyncio
    @patch("app.routers.chat.generate_response_full", new_callable=AsyncMock)
    async def test_chat_returns_502_on_generation_error(
        self, mock_generate: AsyncMock, transport: ASGITransport
    ) -> None:
        """POST /chat returns 502 when the LLM fails to generate."""
        mock_generate.side_effect = LLMGenerationError("rate limited")

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/chat", json={"message": "Hi"})

        assert response.status_code == 502
        body = response.json()
        assert body["detail"]["code"] == "LLM_GENERATION_FAILED"
