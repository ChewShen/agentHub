"""Integration tests for the documents router."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def mock_extract_text():
    with patch("app.routers.documents.extract_text_from_pdf", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_generate_response():
    with patch("app.routers.documents.generate_response") as mock:
        # Mock an async generator
        async def mock_generator(*args, **kwargs):
            yield "This "
            yield "is "
            yield "a mock "
            yield "answer."
        
        mock.return_value = mock_generator()
        yield mock


@pytest.mark.asyncio
async def test_upload_document_success(mock_extract_text, mock_generate_response):
    """Test successful document upload and grounded response generation."""
    mock_extract_text.return_value = "Mocked PDF content."
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # We need to send multipart/form-data with a file and a message
        files = {"file": ("test.pdf", b"dummy pdf content", "application/pdf")}
        data = {"message": "What is this about?"}
        
        response = await client.post("/documents/upload", data=data, files=files)
        
    assert response.status_code == 200
    assert response.text == "This is a mock answer."
    
    # Verify the text extraction was called
    mock_extract_text.assert_called_once_with(b"dummy pdf content")
    
    # Verify generate_response was called with the message AND the extracted context
    mock_generate_response.assert_called_once_with(
        message="What is this about?",
        context="Mocked PDF content."
    )


@pytest.mark.asyncio
async def test_upload_document_invalid_type():
    """Test uploading a non-PDF file returns 415."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.txt", b"dummy text", "text/plain")}
        data = {"message": "Question"}
        
        response = await client.post("/documents/upload", data=data, files=files)
        
    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


@pytest.mark.asyncio
async def test_upload_document_empty_file():
    """Test uploading an empty file returns 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.pdf", b"", "application/pdf")}
        data = {"message": "Question"}
        
        response = await client.post("/documents/upload", data=data, files=files)
        
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMPTY_FILE"


@pytest.mark.asyncio
async def test_upload_document_too_large():
    """Test uploading an oversized file returns 413."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # max_upload_size_mb is 5 by default, so 6 MB will fail
        large_content = b"0" * (6 * 1024 * 1024)
        files = {"file": ("large.pdf", large_content, "application/pdf")}
        data = {"message": "Question"}
        
        response = await client.post("/documents/upload", data=data, files=files)
        
    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "PAYLOAD_TOO_LARGE"
