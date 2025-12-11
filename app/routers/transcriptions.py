"""API router for transcription endpoints."""

from typing import Optional
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from models.transcription import Transcription, TranscriptionItem, Transcriptions
from models.upload import UrlUploadRequest
from services.transcription_service import process_transcription
from services.file_service import file_service
from services.url_service import url_service

from storage.data_storage import storage
from storage.file_storage import file_storage


router = APIRouter()


@router.post("/upload", response_model=Transcription)
async def upload_file(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en"),
):
    """Upload and transcribe an audio/video file."""
    file_service.validate_file(file)
    file_path = file_storage.save_file(str(uuid.uuid4()), file.filename, file.file)
    duration = file_service.get_file_duration(file_path)

    transcription = process_transcription(
        file_path=file_path,
        file_name=file.filename,
        file_type=file.content_type,
        duration=duration,
        language=language,
    )

    storage.save(transcription)

    return transcription


@router.post("/upload-url", response_model=Transcription)
async def upload_from_url(
    request: UrlUploadRequest,
):
    """Upload and transcribe from a URL."""
    try:
        file_path, content_type = await url_service.download_from_url(
            request.url, file_storage.upload_dir
        )
        duration = file_service.get_file_duration(file_path)

        transcription = process_transcription(
            file_path=file_path,
            file_name=request.url.split("/")[-1],
            file_type=content_type,
            duration=duration,
            language=request.language,
            detect_speakers=request.detect_speakers,
            source_url=request.url,
        )

        storage.save(transcription)
        print("Transcription completed and saved:", transcription.id)

        return transcription
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=Transcriptions)
async def list_transcriptions():
    """List all transcriptions with summary information."""
    transcriptions = storage.list_all()
    return [
        TranscriptionItem(
            id=t.id, status=t.status, file_name=t.file_name, duration=t.duration
        )
        for t in transcriptions
    ]


@router.get("/{transcription_id}", response_model=Transcription)
async def get_transcription(transcription_id: str):
    """Get a transcription by ID."""
    transcription = storage.get(transcription_id)
    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found"
        )
    return transcription
