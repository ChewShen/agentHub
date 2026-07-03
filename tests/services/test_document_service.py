"""Unit tests for the document service."""

import fitz  # PyMuPDF
import pytest

from app.services.document import (
    DocumentEmptyError,
    DocumentExtractionError,
    extract_text_from_pdf,
)


def create_sample_pdf_bytes(text: str = "Hello, World!") -> bytes:
    """Helper to create an in-memory PDF with the given text."""
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((50, 50), text)
    return doc.write()


@pytest.mark.asyncio
async def test_extract_text_from_pdf_success():
    """Test extracting text from a valid PDF."""
    pdf_bytes = create_sample_pdf_bytes("Test document content.\nLine 2.")
    text = await extract_text_from_pdf(pdf_bytes)
    
    assert "Test document content." in text
    assert "Line 2." in text


@pytest.mark.asyncio
async def test_extract_text_from_pdf_empty():
    """Test extracting text from a PDF with no text (raises DocumentEmptyError)."""
    # Create a PDF with no text inserted
    pdf_bytes = create_sample_pdf_bytes(text="")
    
    with pytest.raises(DocumentEmptyError) as exc_info:
        await extract_text_from_pdf(pdf_bytes)
        
    assert "no extractable text" in str(exc_info.value)


@pytest.mark.asyncio
async def test_extract_text_from_pdf_corrupt():
    """Test extracting text from invalid/corrupt bytes (raises DocumentExtractionError)."""
    corrupt_bytes = b"This is not a PDF file."
    
    with pytest.raises(DocumentExtractionError) as exc_info:
        await extract_text_from_pdf(corrupt_bytes)
        
    assert "Could not parse the PDF file" in str(exc_info.value)
