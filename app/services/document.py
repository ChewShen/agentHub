"""Document processing service.

Responsibilities:
- Extract plain text from PDF documents using PyMuPDF.
- Validate that the document contains extractable text.
"""

import logging
import uuid

import fitz  # PyMuPDF
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Chunk, Document
from app.services.chunking import chunk_text

logger = logging.getLogger(__name__)


class DocumentError(Exception):
    """Base exception for document processing errors."""


class DocumentExtractionError(DocumentError):
    """Raised when the document cannot be parsed or read (e.g. corrupt)."""


class DocumentEmptyError(DocumentError):
    """Raised when the document contains no extractable text (e.g. image-only PDF)."""


async def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file.

    Args:
        file_bytes: The raw bytes of the PDF file.

    Returns:
        The extracted text as a single string, with pages separated by newlines.

    Raises:
        DocumentExtractionError: If the PDF is corrupt or cannot be opened.
        DocumentEmptyError: If the PDF contains no extractable text.
    """
    try:
        # Open the PDF from memory
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        logger.error("Failed to open PDF from bytes: %s", exc)
        raise DocumentExtractionError("Could not parse the PDF file. It may be corrupt or invalid.") from exc

    text_parts = []
    
    with doc:
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Extract text (preserves basic layout with newlines)
            page_text = page.get_text()
            if page_text:
                text_parts.append(page_text.strip())

    full_text = "\n\n".join(text_parts).strip()

    if not full_text:
        logger.warning("PDF extraction yielded no text (possible scanned/image-only PDF).")
        raise DocumentEmptyError(
            "The PDF contains no extractable text. Scanned or image-only PDFs are not supported."
        )

    return full_text


async def ingest_document(file_bytes: bytes, filename: str, session: AsyncSession) -> tuple[Document, int]:
    """Extract text from PDF, chunk it, and store in database.
    
    Args:
        file_bytes: The raw bytes of the PDF file.
        filename: The original filename.
        session: Database session.
        
    Returns:
        A tuple of (created Document object, number of chunks created).
    """
    full_text = await extract_text_from_pdf(file_bytes)
    chunk_strings = chunk_text(full_text)
    
    document = Document(filename=filename)
    session.add(document)
    await session.flush()  # to get document.id
    
    for i, text in enumerate(chunk_strings):
        chunk = Chunk(
            document_id=document.id,
            chunk_index=i,
            text=text,
            source_filename=filename,
        )
        session.add(chunk)
        
    await session.commit()
    await session.refresh(document)
    
    return document, len(chunk_strings)


async def get_document_chunks(document_id: uuid.UUID, session: AsyncSession) -> list[Chunk]:
    """Retrieve all chunks for a given document.
    
    Args:
        document_id: The UUID of the document.
        session: Database session.
        
    Returns:
        List of chunks ordered by chunk_index.
    """
    result = await session.execute(
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index)
    )
    return list(result.scalars().all())
