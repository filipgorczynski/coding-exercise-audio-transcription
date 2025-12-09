"""Pydantic models for transcription data."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SpeakerTurn(BaseModel):
    """Represents a speaker turn with start/end times and speaker label."""

    start: float
    end: float
    speaker: str


class TranscriptionStatus(str, Enum):
    """Transcription processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptionSegment(BaseModel):
    """A single segment of transcribed text with timestamps."""

    id: str
    start_time: float = Field(ge=0, description="Start time in seconds")
    end_time: float = Field(ge=0, description="End time in seconds")
    speaker: Optional[str] = Field(default="")
    overlap_seconds: Optional[float] = Field(default=0.0)
    text: str


class Transcription(BaseModel):
    """Complete transcription data."""

    id: str
    status: TranscriptionStatus
    file_name: str
    file_type: str
    duration: Optional[float] = None
    language: Optional[str] = "en"
    segments: List[TranscriptionSegment] = []


class TranscriptionItem(BaseModel):
    """Simplified transcription data for list views."""

    id: str
    status: TranscriptionStatus
    file_name: str
    duration: Optional[float] = None


Transcriptions = List[TranscriptionItem]
