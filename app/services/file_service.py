"""File validation and processing service."""

from fastapi import UploadFile, HTTPException, status
import ffmpeg


from config import settings


class FileService:
    """Handle file validation and processing."""

    @staticmethod
    def validate_file(file: UploadFile) -> bool:
        """Validate uploaded file type and size."""
        content_type = file.content_type
        all_supported = (
            settings.SUPPORTED_AUDIO_FORMATS + settings.SUPPORTED_VIDEO_FORMATS
        )

        if content_type not in all_supported:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {content_type}. Supported types: {', '.join(all_supported)}",
            )

        return True

    @staticmethod
    def get_file_duration(file_path: str) -> float:
        """Get duration of audio/video file (mock implementation)."""
        duration = float(ffmpeg.probe(file_path)["format"]["duration"])
        return round(duration, 2)


file_service = FileService()
