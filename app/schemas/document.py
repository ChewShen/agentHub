"""Pydantic schemas for the documents endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response body for POST /documents/upload."""

    document_id: uuid.UUID = Field(..., description="The unique ID of the uploaded document.")
    filename: str = Field(..., description="The name of the uploaded PDF file.")
    chunk_count: int = Field(..., description="Number of text chunks generated.")
    created_at: datetime = Field(..., description="Timestamp of when the document was uploaded.")
