"""Application configuration."""
import os
from typing import List


class Settings:
    """Application settings."""

    # API Configuration
    API_TITLE: str = "Audio/Video Transcription API"
    API_DESCRIPTION: str = "API for transcribing audio and video files"
    API_VERSION: str = "1.0.0"

    # File Upload Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 524288000))  # 500MB default

    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:4173,http://127.0.0.1:5173",
    ).split(",")

    # Supported File Types
    SUPPORTED_AUDIO_FORMATS: List[str] = [
        "audio/mpeg",  # mp3
        "audio/wav",  # wav
        "audio/ogg",  # ogg
        "audio/mp4",  # m4a
        "audio/flac",  # flac
        "audio/aac",  # aac
    ]

    SUPPORTED_VIDEO_FORMATS: List[str] = [
        "video/mp4",  # mp4
        "video/quicktime",  # mov
        "video/webm",  # webm
        "video/x-msvideo",  # avi
        "video/x-matroska",  # mkv
    ]


settings = Settings()
