"""Document processing service.

Responsibilities:
- Extract plain text from PDF documents using PyMuPDF.
- Validate that the document contains extractable text.
"""

import logging

import fitz  # PyMuPDF

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
