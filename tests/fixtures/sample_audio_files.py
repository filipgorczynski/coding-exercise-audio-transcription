"""Generators for sample test data."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../app'))

from models.transcription import TranscriptionSegment
from services.transcription_service import SpeakerTurn


def generate_segments(count: int, duration_per_segment: float = 2.0):
    """Generate sample transcription segments.

    Args:
        count: Number of segments to generate
        duration_per_segment: Duration of each segment in seconds

    Returns:
        List of TranscriptionSegment objects
    """
    segments = []
    for i in range(count):
        start = i * duration_per_segment
        end = (i + 1) * duration_per_segment
        segments.append(
            TranscriptionSegment(
                id=f"seg-{i}",
                start_time=start,
                end_time=end,
                text=f"Sample text segment {i}",
                speaker=""
            )
        )
    return segments


def generate_speaker_turns(count: int, duration_per_turn: float = 3.0, num_speakers: int = 2):
    """Generate sample speaker turns.

    Args:
        count: Number of speaker turns to generate
        duration_per_turn: Duration of each turn in seconds
        num_speakers: Number of unique speakers to cycle through

    Returns:
        List of SpeakerTurn objects
    """
    turns = []
    for i in range(count):
        start = i * duration_per_turn
        end = (i + 1) * duration_per_turn
        speaker = f"SPEAKER_{i % num_speakers:02d}"
        turns.append(
            SpeakerTurn(start=start, end=end, speaker=speaker)
        )
    return turns


def generate_overlapping_scenario():
    """Generate a complex overlapping scenario for testing.

    Returns:
        Tuple of (segments, turns) for testing overlap assignment
    """
    segments = [
        TranscriptionSegment(id="seg-0", start_time=0.0, end_time=2.5, text="First", speaker=""),
        TranscriptionSegment(id="seg-1", start_time=2.5, end_time=5.5, text="Second", speaker=""),
        TranscriptionSegment(id="seg-2", start_time=5.5, end_time=7.0, text="Third", speaker=""),
    ]

    turns = [
        SpeakerTurn(start=0.0, end=3.0, speaker="SPEAKER_00"),
        SpeakerTurn(start=3.0, end=6.0, speaker="SPEAKER_01"),
        SpeakerTurn(start=6.0, end=10.0, speaker="SPEAKER_00"),
    ]

    return segments, turns
