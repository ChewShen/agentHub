"""Chat router — POST /chat endpoint with streaming response."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.chat import ChatRequest
from app.services.document import get_document_chunks
from app.services.llm import LLMConfigError, LLMGenerationError, generate_response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    response_class=StreamingResponse,
    summary="Chat with the AI assistant",
    description="Send a message and receive a streamed text response from Gemini.",
)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
    """Accept a user message and stream the LLM response back.

    If document_id is provided, loads the document's chunks as context.
    Returns chunked text/plain — each chunk is a piece of the model's
    response as it is generated.
    """
    chunks = None
    if request.document_id:
        db_chunks = await get_document_chunks(request.document_id, session)
        if not db_chunks:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": "Document not found or has no chunks.",
                },
            )
        chunks = [c.text for c in db_chunks]

    try:
        return StreamingResponse(
            generate_response(request.message, chunks=chunks),
            media_type="text/plain",
        )
    except LLMConfigError as exc:
        logger.error("LLM configuration error: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={
                "code": "LLM_NOT_CONFIGURED",
                "message": "The AI service is not properly configured.",
            },
        ) from exc
    except LLMGenerationError as exc:
        logger.error("LLM generation error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail={
                "code": "LLM_GENERATION_FAILED",
                "message": "The AI service failed to generate a response.",
            },
        ) from exc
