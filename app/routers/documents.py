"""Documents router — POST /documents/upload endpoint."""

import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.services.document import DocumentEmptyError, DocumentExtractionError, extract_text_from_pdf
from app.services.llm import LLMConfigError, LLMGenerationError, generate_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/upload",
    response_class=StreamingResponse,
    summary="Upload a PDF and ask a question",
    description="Upload a PDF file and provide a message. The AI will answer based on the document's content.",
)
async def upload_document(
    file: UploadFile = File(..., description="The PDF file to upload (max 5 MB)."),
    message: str = Form(..., description="The user's question about the document."),
) -> StreamingResponse:
    """Accept a PDF file and a user message, extract text, and stream a grounded response."""
    
    # 1. Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=415,
            detail={
                "code": "UNSUPPORTED_MEDIA_TYPE",
                "message": "Only PDF files are supported.",
            },
        )
        
    # 2. Read and validate file size
    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    
    file_bytes = await file.read()
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "PAYLOAD_TOO_LARGE",
                "message": f"File exceeds the maximum allowed size of {settings.max_upload_size_mb} MB.",
            },
        )
        
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "EMPTY_FILE",
                "message": "The uploaded file is empty.",
            },
        )

    # 3. Extract text from PDF
    try:
        extracted_text = await extract_text_from_pdf(file_bytes)
    except DocumentEmptyError as exc:
        logger.warning("Empty document uploaded: %s", file.filename)
        raise HTTPException(
            status_code=422,
            detail={
                "code": "DOCUMENT_EMPTY",
                "message": "The PDF contains no extractable text. Scanned or image-only PDFs are not supported.",
            },
        ) from exc
    except DocumentExtractionError as exc:
        logger.error("Failed to extract text from %s: %s", file.filename, exc)
        raise HTTPException(
            status_code=400,
            detail={
                "code": "DOCUMENT_EXTRACTION_FAILED",
                "message": "Could not parse the PDF file. It may be corrupt.",
            },
        ) from exc

    # 4. Generate grounded response
    try:
        return StreamingResponse(
            generate_response(message=message, context=extracted_text),
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
