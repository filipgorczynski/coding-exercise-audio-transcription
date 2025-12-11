"""Mock transcription service."""

import uuid

import whisper

from models.transcription import (
    Transcription,
    TranscriptionSegment,
    TranscriptionStatus,
)


def process_transcription(
    file_path: str,
    file_name: str,
    file_type: str,
    duration: float,
    language: str = "en",
    detect_speakers: bool = False,
    source_url: str = None,
) -> Transcription:
    """Process transcription synchronously and return complete transcription."""
    transcription_id = str(uuid.uuid4())

    transcription = Transcription(
        id=transcription_id,
        status=TranscriptionStatus.PROCESSING,
        file_name=file_name,
        file_type=file_type,
        duration=round(duration, 2),
        language=language,
        segments=[],
    )

    try:
        model = whisper.load_model("turbo")
        result = model.transcribe(file_path)

        segments = []
        for index, whisper_seg in enumerate(result["segments"]):
            segments.append(
                TranscriptionSegment(
                    id=f"seg-{index}",
                    start_time=round(whisper_seg["start"], 2),
                    end_time=round(whisper_seg["end"], 2),
                    text=whisper_seg["text"].strip(),
                    speaker=None,  # Whisper doesn't provide speaker diarization
                )
            )

        transcription.segments = segments
        transcription.status = TranscriptionStatus.COMPLETED
        return transcription

    except Exception as e:
        print(f"Transcription failed for {transcription.id}: {e}")
        transcription.status = TranscriptionStatus.FAILED
        transcription.metadata.error = str(e)
        return transcription
