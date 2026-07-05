"""Pydantic schemas for the chat endpoint."""

import uuid

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for POST /chat."""

    message: str = Field(..., min_length=1, description="The user's message to send to the LLM.")
    document_id: uuid.UUID | None = Field(None, description="Optional document ID to query against.")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of document chunks to retrieve.")


class RetrievedChunk(BaseModel):
    """Metadata for a retrieved document chunk."""
    
    chunk_index: int = Field(..., description="The chunk's original index in the document.")
    text: str = Field(..., description="The content of the chunk.")
    score: float = Field(..., description="Cosine similarity score.")
    source_filename: str = Field(..., description="Original filename of the chunk's document.")


class ChatResponse(BaseModel):
    """Non-streaming response body (used for OpenAPI docs and test assertions)."""

    response: str = Field(..., description="The LLM's complete response text.")
    sources: list[RetrievedChunk] = Field(default_factory=list, description="Chunks retrieved and used as context.")
