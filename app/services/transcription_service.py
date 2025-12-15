"""Mock transcription service."""

from typing import List
import uuid

from pyannote.audio import Pipeline
import torch
import whisper

from config import settings
from models.transcription import (
    SpeakerTurn,
    Transcription,
    TranscriptionSegment,
    TranscriptionStatus,
)


def interval_overlap(
    segment_start: float,
    segment_end: float,
    turn_start: float,
    turn_end: float,
) -> float:
    """Return overlap duration (in seconds) between a transcription segment
    and a speaker turn."""
    return max(
        0.0,
        min(segment_end, turn_end) - max(segment_start, turn_start),
    )


def transcribe_with_whisper(file_path: str) -> List[TranscriptionSegment]:
    """
    Transcribe audio file using OpenAI Whisper model.

    Args:
        file_path: Path to the audio file

    Returns:
        List of TranscriptionSegment objects with timestamps and text
    """
    model = whisper.load_model("turbo")
    result = model.transcribe(file_path)

    # Convert Whisper segments to TranscriptionSegment objects
    segments = []
    for index, whisper_seg in enumerate(result["segments"]):
        segments.append(
            TranscriptionSegment(
                id=f"seg-{index}",
                start_time=round(whisper_seg["start"], 2),
                end_time=round(whisper_seg["end"], 2),
                text=whisper_seg["text"].strip(),
                speaker="",  # Will be assigned by diarization
            )
        )

    return segments


def diarize_with_pyannote(file_path: str) -> List[SpeakerTurn]:
    """
    Perform speaker diarization using pyannote.audio.

    Args:
        file_path: Path to the audio file

    Returns:
        List of SpeakerTurn objects containing speaker turns with timestamps
    """
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-community-1",
        token=settings.HUGGING_FACE_TOKEN,
    )
    pipeline.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    output = pipeline(file_path)

    # Convert pyannote Annotation to list of SpeakerTurn objects
    speaker_turns = []
    for segment, track, speaker in output.speaker_diarization.itertracks(
        yield_label=True
    ):
        speaker_turns.append(
            SpeakerTurn(start=segment.start, end=segment.end, speaker=speaker)
        )

    return speaker_turns


def assign_speaker_by_overlap(
    transcription_segments,
    speaker_turns,
    min_overlap_seconds: float = 0.10,
    unknown_speaker_label: str = "UNKNOWN",
):
    """
    Assign a speaker to each transcription segment based on maximum
    time overlap with diarization speaker turns.
    """
    speaker_turns = sorted(
        speaker_turns,
        key=lambda turn: (turn.start, turn.end),
    )
    annotated_segments: List[TranscriptionSegment] = []
    speaker_turn_cursor = 0

    for transcription_segment in transcription_segments:
        segment_start_time = float(transcription_segment.start_time)
        segment_end_time = float(transcription_segment.end_time)

        # move cursor to the first speaker turn that could overlap this segment
        while (
            speaker_turn_cursor < len(speaker_turns)
            and speaker_turns[speaker_turn_cursor].end <= segment_start_time
        ):
            speaker_turn_cursor += 1

        selected_speaker = unknown_speaker_label
        max_overlap_seconds = 0.0

        overlapping_turn_cursor = speaker_turn_cursor

        # scan all speaker turns that overlap the transcription segment
        while (
            overlapping_turn_cursor < len(speaker_turns)
            and speaker_turns[overlapping_turn_cursor].start < segment_end_time
        ):
            speaker_turn = speaker_turns[overlapping_turn_cursor]

            overlap_seconds = interval_overlap(
                segment_start_time,
                segment_end_time,
                speaker_turn.start,
                speaker_turn.end,
            )

            if overlap_seconds > max_overlap_seconds:
                max_overlap_seconds = overlap_seconds
                selected_speaker = speaker_turn.speaker

            overlapping_turn_cursor += 1

        # Reject "weak" or "accidental" overlaps
        if max_overlap_seconds < min_overlap_seconds:
            selected_speaker = unknown_speaker_label

        annotated_segments.append(
            TranscriptionSegment(
                id=transcription_segment.id,
                start_time=segment_start_time,
                end_time=segment_end_time,
                speaker=selected_speaker,
                overlap_seconds=max_overlap_seconds,
                text=transcription_segment.text,
            )
        )

    return annotated_segments


def process_transcription(
    file_path: str,
    file_name: str,
    file_type: str,
    duration: float,
    language: str = "en",
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

    # Whisper transcription (returns TranscriptionSegment objects)
    segments = transcribe_with_whisper(file_path)

    # Diarization with pyannote-audio (community-1 open-source speaker diarization)
    speaker_diarization = diarize_with_pyannote(file_path)

    print("SEGMENTS: ", segments)
    print("DIARIZATION: ", speaker_diarization)

    # Assign speakers to segments based on diarization
    try:
        annotated_segments = assign_speaker_by_overlap(segments, speaker_diarization)
        transcription.segments = annotated_segments
        transcription.status = TranscriptionStatus.COMPLETED
    except Exception as e:
        print(f"Speaker assignment failed: {e}", e)
        transcription.status = TranscriptionStatus.FAILED

    return transcription
