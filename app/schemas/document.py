"""Pydantic schemas for the documents endpoints."""

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response body for POST /documents/upload.
    
    Note: The actual endpoint returns a StreamingResponse, this model is mainly
    used for documentation purposes if we were to return a structured response.
    """

    filename: str = Field(..., description="The name of the uploaded PDF file.")
    pages: int = Field(..., description="Number of pages extracted from the PDF.")
    text_length: int = Field(..., description="Total length of the extracted text in characters.")
