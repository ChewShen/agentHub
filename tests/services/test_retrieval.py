"""Unit tests for the retrieval service."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.retrieval import cosine_similarity, retrieve_top_k
from app.models.document import Chunk


class TestCosineSimilarity:
    
    def test_identical_vectors(self):
        vec = [1.0, 2.0, 3.0]
        score = cosine_similarity(vec, vec)
        assert pytest.approx(score) == 1.0
        
    def test_orthogonal_vectors(self):
        vec_a = [1.0, 0.0]
        vec_b = [0.0, 1.0]
        score = cosine_similarity(vec_a, vec_b)
        assert pytest.approx(score) == 0.0
        
    def test_opposite_vectors(self):
        vec_a = [1.0, 2.0]
        vec_b = [-1.0, -2.0]
        score = cosine_similarity(vec_a, vec_b)
        assert pytest.approx(score) == -1.0
        
    def test_zero_vector(self):
        vec_a = [0.0, 0.0]
        vec_b = [1.0, 1.0]
        score = cosine_similarity(vec_a, vec_b)
        assert score == 0.0


@pytest.mark.asyncio
class TestRetrieveTopK:
    
    async def test_returns_empty_if_no_query_embedding(self):
        session = AsyncMock()
        result = await retrieve_top_k([], uuid.uuid4(), session)
        assert result == []
        
    async def test_retrieves_top_k_chunks(self):
        session = AsyncMock()
        
        # Create some mock chunks
        doc_id = uuid.uuid4()
        c1 = Chunk(id=uuid.uuid4(), document_id=doc_id, chunk_index=0, text="a", source_filename="f", embedding=[1.0, 0.0])
        c2 = Chunk(id=uuid.uuid4(), document_id=doc_id, chunk_index=1, text="b", source_filename="f", embedding=[0.707, 0.707])
        c3 = Chunk(id=uuid.uuid4(), document_id=doc_id, chunk_index=2, text="c", source_filename="f", embedding=[0.0, 1.0])
        
        # Mock session.execute().scalars().all() to return [c1, c2, c3]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [c1, c2, c3]
        session.execute.return_value = mock_result
        
        # Query vector is [1.0, 0.0] -> perfectly matches c1, orthogonal to c3
        query_embedding = [1.0, 0.0]
        
        # Ask for top 2
        scored_chunks = await retrieve_top_k(query_embedding, doc_id, session, top_k=2)
        
        assert len(scored_chunks) == 2
        
        # c1 should be first with score 1.0
        assert scored_chunks[0].chunk == c1
        assert pytest.approx(scored_chunks[0].score) == 1.0
        
        # c2 should be second with score ~0.707
        assert scored_chunks[1].chunk == c2
        assert pytest.approx(scored_chunks[1].score, rel=1e-3) == 0.707

    async def test_skips_chunks_without_embeddings(self):
        session = AsyncMock()
        
        doc_id = uuid.uuid4()
        c1 = Chunk(id=uuid.uuid4(), document_id=doc_id, chunk_index=0, text="a", source_filename="f", embedding=None)
        c2 = Chunk(id=uuid.uuid4(), document_id=doc_id, chunk_index=1, text="b", source_filename="f", embedding=[1.0, 1.0])
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [c1, c2]
        session.execute.return_value = mock_result
        
        scored_chunks = await retrieve_top_k([1.0, 1.0], doc_id, session)
        
        # Only c2 has an embedding
        assert len(scored_chunks) == 1
        assert scored_chunks[0].chunk == c2
