"""Pydantic models for file upload."""

from typing import Optional
from pydantic import BaseModel, Field


class UrlUploadRequest(BaseModel):
    """Request model for URL-based upload."""

    url: str = Field(..., description="Media URL")
    language: Optional[str] = "en"


class UploadResponse(BaseModel):
    """Response model for upload operations."""

    transcription_id: str
    status: str
    message: str
