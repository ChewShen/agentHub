"""Integration tests for the documents router."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def mock_ingest_document():
    with patch("app.routers.documents.ingest_document", new_callable=AsyncMock) as mock:
        yield mock


@pytest.mark.asyncio
async def test_upload_document_success(mock_ingest_document):
    """Test successful document upload and DB ingestion."""
    import uuid
    from datetime import datetime, timezone
    from unittest.mock import ANY
    
    class MockDoc:
        id = uuid.uuid4()
        filename = "test.pdf"
        created_at = datetime.now(timezone.utc)
        
    mock_ingest_document.return_value = (MockDoc(), 2)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.pdf", b"dummy pdf content", "application/pdf")}
        
        response = await client.post("/documents/upload", files=files)
        
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.pdf"
    assert data["chunk_count"] == 2
    
    mock_ingest_document.assert_called_once_with(b"dummy pdf content", "test.pdf", ANY)


@pytest.mark.asyncio
async def test_upload_document_invalid_type():
    """Test uploading a non-PDF file returns 415."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.txt", b"dummy text", "text/plain")}
        
        response = await client.post("/documents/upload", files=files)
        
    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


@pytest.mark.asyncio
async def test_upload_document_empty_file():
    """Test uploading an empty file returns 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.pdf", b"", "application/pdf")}
        
        response = await client.post("/documents/upload", files=files)
        
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMPTY_FILE"


@pytest.mark.asyncio
async def test_upload_document_too_large():
    """Test uploading an oversized file returns 413."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # max_upload_size_mb is 5 by default, so 6 MB will fail
        large_content = b"0" * (6 * 1024 * 1024)
        files = {"file": ("large.pdf", large_content, "application/pdf")}
        
        response = await client.post("/documents/upload", files=files)
        
    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "PAYLOAD_TOO_LARGE"
