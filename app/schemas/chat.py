"""Pydantic schemas for the chat endpoint."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for POST /chat."""

    message: str = Field(..., min_length=1, description="The user's message to send to the LLM.")


class ChatResponse(BaseModel):
    """Non-streaming response body (used for OpenAPI docs and test assertions)."""

    response: str = Field(..., description="The LLM's complete response text.")
