"""Semantic retrieval service.

Responsibilities:
- Compute cosine similarity between vectors using numpy
- Retrieve and rank chunks from the database
"""

import uuid
import logging
from typing import NamedTuple

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Chunk

logger = logging.getLogger(__name__)


class ScoredChunk(NamedTuple):
    """A chunk paired with its semantic similarity score."""
    chunk: Chunk
    score: float


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute the cosine similarity between two vectors.

    Args:
        a: First vector.
        b: Second vector.

    Returns:
        Cosine similarity score between -1.0 and 1.0.
    """
    vec_a = np.array(a, dtype=np.float32)
    vec_b = np.array(b, dtype=np.float32)
    
    # Avoid division by zero
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


async def retrieve_top_k(
    query_embedding: list[float],
    document_id: uuid.UUID,
    session: AsyncSession,
    top_k: int = 5,
) -> list[ScoredChunk]:
    """Retrieve the top-k most semantically relevant chunks for a document.

    Args:
        query_embedding: The embedding vector of the query.
        document_id: The ID of the document to search within.
        session: Database session.
        top_k: Number of chunks to retrieve.

    Returns:
        A list of ScoredChunk objects sorted by descending score.
    """
    if not query_embedding:
        return []

    # Get all chunks for the document
    # In V5 this will be a Qdrant search, but for V4 we do it in memory
    result = await session.execute(
        select(Chunk).where(Chunk.document_id == document_id)
    )
    all_chunks = list(result.scalars().all())
    
    scored_chunks: list[ScoredChunk] = []
    
    for chunk in all_chunks:
        # Skip chunks that haven't been embedded (e.g. from before V4 migration)
        if chunk.embedding is None:
            continue
            
        score = cosine_similarity(query_embedding, chunk.embedding)
        scored_chunks.append(ScoredChunk(chunk=chunk, score=score))
        
    # Sort by descending score
    scored_chunks.sort(key=lambda x: x.score, reverse=True)
    
    return scored_chunks[:top_k]
