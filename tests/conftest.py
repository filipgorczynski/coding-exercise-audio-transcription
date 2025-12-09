"""Shared fixtures and configuration for tests."""

import pytest
import tempfile
import json
import os
import sys
from unittest.mock import Mock, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from io import BytesIO

# Add app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../app'))

from main import app
from models.transcription import (
    Transcription,
    TranscriptionSegment,
    TranscriptionStatus,
)
from services.transcription_service import SpeakerTurn


@pytest.fixture
def test_client():
    """FastAPI test client for integration tests."""
    return TestClient(app)


@pytest.fixture
def temp_dir():
    """Temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_data_file(temp_dir):
    """Temporary JSON file for storage tests."""
    data_file = os.path.join(temp_dir, "transcriptions.json")
    with open(data_file, 'w') as f:
        json.dump({}, f)
    return data_file


@pytest.fixture
def mock_whisper_model():
    """Mock whisper model with transcription results."""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {
        "segments": [
            {"start": 0.0, "end": 2.5, "text": " Hello world"},
            {"start": 2.5, "end": 5.0, "text": " How are you"},
            {"start": 5.0, "end": 8.0, "text": " I am fine"},
        ],
        "language": "en"
    }
    return mock_model


@pytest.fixture
def mock_whisper_load_model(mock_whisper_model):
    """Mock whisper.load_model function."""
    def _load_model(model_name):
        return mock_whisper_model
    return _load_model


@pytest.fixture
def mock_pyannote_pipeline():
    """Mock pyannote Pipeline for speaker diarization."""
    mock_pipeline = MagicMock()

    # Create mock annotation with speaker turns
    mock_segment_0 = MagicMock()
    mock_segment_0.start = 0.0
    mock_segment_0.end = 3.0

    mock_segment_1 = MagicMock()
    mock_segment_1.start = 3.0
    mock_segment_1.end = 6.0

    mock_segment_2 = MagicMock()
    mock_segment_2.start = 6.0
    mock_segment_2.end = 8.0

    mock_annotation = MagicMock()
    mock_annotation.itertracks.return_value = [
        (mock_segment_0, "track_0", "SPEAKER_00"),
        (mock_segment_1, "track_1", "SPEAKER_01"),
        (mock_segment_2, "track_2", "SPEAKER_00"),
    ]

    mock_pipeline.return_value = mock_annotation
    mock_pipeline.to = MagicMock(return_value=mock_pipeline)

    return mock_pipeline


@pytest.fixture
def mock_ffmpeg_probe():
    """Mock ffmpeg.probe for duration checking."""
    return {"format": {"duration": "10.5"}}


@pytest.fixture
def sample_upload_file():
    """Create a sample UploadFile for testing."""
    from fastapi import UploadFile

    def _create_file(filename="test.mp3", content_type="audio/mpeg", content=b"fake audio data"):
        return UploadFile(
            filename=filename,
            file=BytesIO(content),
            content_type=content_type
        )
    return _create_file


@pytest.fixture
def sample_transcription_segments():
    """Sample transcription segments for testing."""
    return [
        TranscriptionSegment(
            id="seg-0",
            start_time=0.0,
            end_time=2.5,
            text="Hello world",
            speaker=""
        ),
        TranscriptionSegment(
            id="seg-1",
            start_time=2.5,
            end_time=5.0,
            text="How are you",
            speaker=""
        ),
        TranscriptionSegment(
            id="seg-2",
            start_time=5.0,
            end_time=8.0,
            text="I am fine",
            speaker=""
        ),
    ]


@pytest.fixture
def sample_speaker_turns():
    """Sample speaker turns for testing."""
    return [
        SpeakerTurn(start=0.0, end=3.0, speaker="SPEAKER_00"),
        SpeakerTurn(start=3.0, end=6.0, speaker="SPEAKER_01"),
        SpeakerTurn(start=6.0, end=8.0, speaker="SPEAKER_00"),
    ]


@pytest.fixture
def sample_transcription():
    """Sample complete transcription object."""
    return Transcription(
        id="test-id-123",
        status=TranscriptionStatus.COMPLETED,
        file_name="test_audio.mp3",
        file_type="audio/mpeg",
        duration=10.5,
        language="en",
        segments=[
            TranscriptionSegment(
                id="seg-0",
                start_time=0.0,
                end_time=2.5,
                speaker="SPEAKER_00",
                overlap_seconds=2.5,
                text="Hello world"
            )
        ]
    )


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient for URL downloads."""
    mock_response = AsyncMock()
    mock_response.headers.get.return_value = "audio/mpeg"
    mock_response.content = b"fake downloaded audio data"
    mock_response.raise_for_status = AsyncMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = AsyncMock()

    return mock_client
