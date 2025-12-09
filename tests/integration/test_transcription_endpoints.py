"""Integration tests for transcription API endpoints."""

import pytest
import sys
import os
from unittest.mock import patch, AsyncMock
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../app'))

from models.transcription import Transcription, TranscriptionStatus


class TestUploadEndpoint:
    """Test POST /api/transcriptions/upload endpoint."""

    @patch('routers.transcriptions.process_transcription')
    @patch('routers.transcriptions.file_service.get_file_duration')
    @patch('routers.transcriptions.file_storage.save_file')
    @patch('routers.transcriptions.storage.save')
    def test_upload_success(
        self, mock_storage_save, mock_save_file, mock_get_duration,
        mock_process, test_client, sample_transcription
    ):
        """Test successful file upload and transcription."""
        mock_save_file.return_value = "/uploads/test_audio.mp3"
        mock_get_duration.return_value = 10.5
        mock_process.return_value = sample_transcription
        mock_storage_save.return_value = sample_transcription

        # Create file data
        files = {"file": ("test.mp3", BytesIO(b"fake audio"), "audio/mpeg")}
        data = {"language": "en"}

        response = test_client.post("/api/transcriptions/upload", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == sample_transcription.id
        assert result["status"] == "completed"
        assert result["file_name"] == "test_audio.mp3"

    @pytest.mark.parametrize(
        "content_type,status_code",
        [
            ("audio/mpeg", 200),
            ("audio/wav", 200),
            ("video/mp4", 200),
            ("application/pdf", 400),
            ("image/jpeg", 400),
        ],
        ids=["audio_mpeg", "audio_wav", "video_mp4", "pdf", "jpeg"]
    )
    @patch('routers.transcriptions.process_transcription')
    @patch('routers.transcriptions.file_service.get_file_duration')
    @patch('routers.transcriptions.file_storage.save_file')
    @patch('routers.transcriptions.storage.save')
    def test_upload_content_type_validation(
        self, mock_storage_save, mock_save_file, mock_get_duration,
        mock_process, test_client, sample_transcription, content_type, status_code
    ):
        """Test file upload with various content types."""
        if status_code == 200:
            mock_save_file.return_value = "/uploads/test_file"
            mock_get_duration.return_value = 10.5
            mock_process.return_value = sample_transcription
            mock_storage_save.return_value = sample_transcription

        files = {"file": ("test_file", BytesIO(b"data"), content_type)}
        data = {"language": "en"}

        response = test_client.post("/api/transcriptions/upload", files=files, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "language",
        ["en", "es", "fr", "de", "zh", None],
        ids=["english", "spanish", "french", "german", "chinese", "none"]
    )
    @patch('routers.transcriptions.process_transcription')
    @patch('routers.transcriptions.file_service.get_file_duration')
    @patch('routers.transcriptions.file_storage.save_file')
    @patch('routers.transcriptions.storage.save')
    def test_upload_language_parameter(
        self, mock_storage_save, mock_save_file, mock_get_duration,
        mock_process, test_client, sample_transcription, language
    ):
        """Test upload with different language parameters."""
        mock_save_file.return_value = "/uploads/test.mp3"
        mock_get_duration.return_value = 10.5
        mock_process.return_value = sample_transcription
        mock_storage_save.return_value = sample_transcription

        files = {"file": ("test.mp3", BytesIO(b"data"), "audio/mpeg")}
        data = {"language": language} if language else {}

        response = test_client.post("/api/transcriptions/upload", files=files, data=data)

        assert response.status_code == 200
        # Verify language was passed to process_transcription
        call_kwargs = mock_process.call_args.kwargs
        expected_lang = language if language else "en"
        assert call_kwargs["language"] == expected_lang

    def test_upload_missing_file(self, test_client):
        """Test upload without file."""
        data = {"language": "en"}

        response = test_client.post("/api/transcriptions/upload", data=data)

        assert response.status_code == 422  # Unprocessable Entity


class TestUploadFromUrlEndpoint:
    """Test POST /api/transcriptions/upload-url endpoint."""

    @patch('routers.transcriptions.process_transcription')
    @patch('routers.transcriptions.file_service.get_file_duration')
    @patch('routers.transcriptions.url_service.download_from_url')
    @patch('routers.transcriptions.storage.save')
    def test_upload_url_success(
        self, mock_storage_save, mock_download, mock_get_duration,
        mock_process, test_client, sample_transcription
    ):
        """Test successful upload from URL."""
        mock_download.return_value = ("/uploads/audio.mp3", "audio/mpeg")
        mock_get_duration.return_value = 10.5
        mock_process.return_value = sample_transcription
        mock_storage_save.return_value = sample_transcription

        payload = {
            "url": "https://example.com/audio.mp3",
            "language": "en"
        }

        response = test_client.post("/api/transcriptions/upload-url", json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == sample_transcription.id
        assert result["status"] == "completed"

    @pytest.mark.parametrize(
        "url,language",
        [
            ("https://example.com/audio.mp3", "en"),
            ("https://cdn.example.com/path/to/file.wav", "es"),
            ("https://example.com/file.mp3?key=value", "fr"),
        ],
        ids=["simple", "path", "query_params"]
    )
    @patch('routers.transcriptions.process_transcription')
    @patch('routers.transcriptions.file_service.get_file_duration')
    @patch('routers.transcriptions.url_service.download_from_url')
    @patch('routers.transcriptions.storage.save')
    def test_upload_url_various_urls(
        self, mock_storage_save, mock_download, mock_get_duration,
        mock_process, test_client, sample_transcription, url, language
    ):
        """Test URL upload with various URL formats."""
        mock_download.return_value = ("/uploads/file", "audio/mpeg")
        mock_get_duration.return_value = 10.5
        mock_process.return_value = sample_transcription
        mock_storage_save.return_value = sample_transcription

        payload = {"url": url, "language": language}

        response = test_client.post("/api/transcriptions/upload-url", json=payload)

        assert response.status_code == 200

    @patch('routers.transcriptions.url_service.download_from_url')
    def test_upload_url_download_failure(self, mock_download, test_client):
        """Test URL upload when download fails."""
        from fastapi import HTTPException
        mock_download.side_effect = HTTPException(status_code=400, detail="Download failed")

        payload = {"url": "https://example.com/bad.mp3", "language": "en"}

        response = test_client.post("/api/transcriptions/upload-url", json=payload)

        assert response.status_code == 400

    def test_upload_url_missing_url(self, test_client):
        """Test URL upload without URL parameter."""
        payload = {"language": "en"}

        response = test_client.post("/api/transcriptions/upload-url", json=payload)

        assert response.status_code == 422


class TestListTranscriptionsEndpoint:
    """Test GET /api/transcriptions endpoint."""

    @patch('routers.transcriptions.storage.list_all')
    def test_list_empty(self, mock_list_all, test_client):
        """Test listing when no transcriptions exist."""
        mock_list_all.return_value = []

        response = test_client.get("/api/transcriptions")

        assert response.status_code == 200
        assert response.json() == []

    @patch('routers.transcriptions.storage.list_all')
    def test_list_multiple(self, mock_list_all, test_client):
        """Test listing multiple transcriptions."""
        transcriptions = [
            Transcription(
                id=f"id-{i}",
                status=TranscriptionStatus.COMPLETED,
                file_name=f"file{i}.mp3",
                file_type="audio/mpeg",
                duration=10.0 + i,
                segments=[]
            )
            for i in range(3)
        ]
        mock_list_all.return_value = transcriptions

        response = test_client.get("/api/transcriptions")

        assert response.status_code == 200
        result = response.json()
        assert len(result) == 3

        # Verify TranscriptionItem fields (no segments)
        for i, item in enumerate(result):
            assert item["id"] == f"id-{i}"
            assert item["status"] == "completed"
            assert item["file_name"] == f"file{i}.mp3"
            assert item["duration"] == 10.0 + i
            assert "segments" not in item

    @patch('routers.transcriptions.storage.list_all')
    @pytest.mark.parametrize(
        "status",
        [
            TranscriptionStatus.PENDING,
            TranscriptionStatus.PROCESSING,
            TranscriptionStatus.COMPLETED,
            TranscriptionStatus.FAILED,
        ],
        ids=["pending", "processing", "completed", "failed"]
    )
    def test_list_various_statuses(self, mock_list_all, test_client, status):
        """Test listing transcriptions with various statuses."""
        transcriptions = [
            Transcription(
                id="test-id",
                status=status,
                file_name="test.mp3",
                file_type="audio/mpeg",
                duration=10.0,
                segments=[]
            )
        ]
        mock_list_all.return_value = transcriptions

        response = test_client.get("/api/transcriptions")

        assert response.status_code == 200
        result = response.json()
        assert result[0]["status"] == status.value


class TestGetTranscriptionEndpoint:
    """Test GET /api/transcriptions/{id} endpoint."""

    @patch('routers.transcriptions.storage.get')
    def test_get_existing(self, mock_get, test_client, sample_transcription):
        """Test getting an existing transcription."""
        mock_get.return_value = sample_transcription

        response = test_client.get(f"/api/transcriptions/{sample_transcription.id}")

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == sample_transcription.id
        assert result["file_name"] == sample_transcription.file_name
        assert len(result["segments"]) == len(sample_transcription.segments)

    @patch('routers.transcriptions.storage.get')
    def test_get_not_found(self, mock_get, test_client):
        """Test getting a non-existent transcription."""
        mock_get.return_value = None

        response = test_client.get("/api/transcriptions/non-existent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch('routers.transcriptions.storage.get')
    @pytest.mark.parametrize(
        "transcription_id",
        [
            "simple-id",
            "uuid-123-456-789",
            "with_underscore_123",
        ],
        ids=["simple", "uuid", "underscore"]
    )
    def test_get_various_id_formats(self, mock_get, test_client, sample_transcription, transcription_id):
        """Test getting transcriptions with various ID formats."""
        sample_transcription.id = transcription_id
        mock_get.return_value = sample_transcription

        response = test_client.get(f"/api/transcriptions/{transcription_id}")

        assert response.status_code == 200
        assert response.json()["id"] == transcription_id
