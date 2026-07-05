"""Chat router — POST /chat endpoint."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.chat import ChatRequest, ChatResponse, RetrievedChunk
from app.services.embedding import embed_text
from app.services.retrieval import retrieve_top_k
from app.services.llm import LLMConfigError, LLMGenerationError, generate_response_full

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with the AI assistant",
    description="Send a message and receive a JSON response from Gemini, including semantic retrieval sources if a document is provided.",
)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_db_session)
) -> ChatResponse:
    """Accept a user message, retrieve relevant chunks, and return the LLM response."""
    chunks = None
    sources = []
    
    if request.document_id:
        try:
            query_embedding = await embed_text(request.message)
            scored_chunks = await retrieve_top_k(
                query_embedding=query_embedding,
                document_id=request.document_id,
                session=session,
                top_k=request.top_k,
            )
        except Exception as exc:
            logger.error("Failed to retrieve chunks for document %s: %s", request.document_id, exc)
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "RETRIEVAL_FAILED",
                    "message": "Failed to retrieve relevant document chunks.",
                },
            ) from exc

        if not scored_chunks:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": "Document not found or has no embedded chunks.",
                },
            )
            
        chunks = [sc.chunk.text for sc in scored_chunks]
        sources = [
            RetrievedChunk(
                chunk_index=sc.chunk.chunk_index,
                text=sc.chunk.text,
                score=sc.score,
                source_filename=sc.chunk.source_filename,
            )
            for sc in scored_chunks
        ]

    try:
        answer = await generate_response_full(request.message, chunks=chunks)
        return ChatResponse(response=answer, sources=sources)
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
