"""Documents router — POST /documents/upload endpoint."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db_session
from app.schemas.document import DocumentUploadResponse
from app.services.document import DocumentEmptyError, DocumentExtractionError, ingest_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    summary="Upload a PDF document",
    description="Upload a PDF file, extract text, split into chunks, and store in the database.",
)
async def upload_document(
    file: UploadFile = File(..., description="The PDF file to upload (max 5 MB)."),
    session: AsyncSession = Depends(get_db_session),
) -> DocumentUploadResponse:
    """Accept a PDF file, chunk it, and store chunks in PostgreSQL."""
    
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

    # 3. Extract, chunk, and store text
    try:
        document, chunk_count = await ingest_document(file_bytes, file.filename, session)
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

    return DocumentUploadResponse(
        document_id=document.id,
        filename=document.filename,
        chunk_count=chunk_count,
        created_at=document.created_at,
    )
