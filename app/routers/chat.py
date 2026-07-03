"""Chat router — POST /chat endpoint with streaming response."""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.llm import LLMConfigError, LLMGenerationError, generate_response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    response_class=StreamingResponse,
    summary="Chat with the AI assistant",
    description="Send a message and receive a streamed text response from Gemini.",
)
async def chat(request: ChatRequest) -> StreamingResponse:
    """Accept a user message and stream the LLM response back.

    Returns chunked text/plain — each chunk is a piece of the model's
    response as it is generated.
    """
    try:
        return StreamingResponse(
            generate_response(request.message),
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
