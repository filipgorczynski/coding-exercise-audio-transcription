"""Tests for transcription service functions."""

import pytest
from unittest.mock import patch, MagicMock


from services.transcription_service import (
    transcribe_with_whisper,
    assign_speaker_by_overlap,
    process_transcription,
    SpeakerTurn,
)
from models.transcription import TranscriptionSegment, TranscriptionStatus


class TestTranscribeWithWhisper:
    """Test Whisper transcription functionality."""

    @patch("services.transcription_service.whisper.load_model")
    def test_transcribe_basic(self, mock_load_model, mock_whisper_model):
        """Test basic transcription with mock Whisper model."""
        mock_load_model.return_value = mock_whisper_model

        result = transcribe_with_whisper("/fake/path/audio.mp3")

        # Verify model was loaded with correct model name
        mock_load_model.assert_called_once_with("turbo")

        # Verify transcribe was called with file path
        mock_whisper_model.transcribe.assert_called_once_with("/fake/path/audio.mp3")

        # Verify segments were created correctly
        assert len(result) == 3
        assert isinstance(result[0], TranscriptionSegment)
        assert result[0].id == "seg-0"
        assert result[0].start_time == 0.0
        assert result[0].end_time == 2.5
        assert result[0].text == "Hello world"
        assert result[0].speaker == ""

    @patch("services.transcription_service.whisper.load_model")
    @pytest.mark.parametrize(
        "whisper_segments,expected_count,expected_texts",
        [
            # Empty result
            ([], 0, []),
            # Single segment
            ([{"start": 0.0, "end": 1.0, "text": " Test"}], 1, ["Test"]),
            # Multiple segments with whitespace
            (
                [
                    {"start": 0.0, "end": 1.0, "text": "  Leading space  "},
                    {"start": 1.0, "end": 2.0, "text": "\nNewline\n"},
                ],
                2,
                ["Leading space", "Newline"],
            ),
            # Long transcription (10 segments)
            (
                [
                    {"start": i, "end": i + 1, "text": f" Segment {i}"}
                    for i in range(10)
                ],
                10,
                [f"Segment {i}" for i in range(10)],
            ),
        ],
        ids=["empty", "single", "whitespace", "long"],
    )
    def test_transcribe_various_outputs(
        self, mock_load_model, whisper_segments, expected_count, expected_texts
    ):
        """Test transcription with various Whisper outputs."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"segments": whisper_segments}
        mock_load_model.return_value = mock_model

        result = transcribe_with_whisper("/fake/path/audio.mp3")

        assert len(result) == expected_count
        for i, expected_text in enumerate(expected_texts):
            assert result[i].text == expected_text

    @patch("services.transcription_service.whisper.load_model")
    def test_transcribe_rounds_timestamps(self, mock_load_model):
        """Test that timestamps are rounded to 2 decimal places."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "segments": [{"start": 1.234567, "end": 3.987654, "text": "Test"}]
        }
        mock_load_model.return_value = mock_model

        result = transcribe_with_whisper("/fake/path/audio.mp3")

        assert result[0].start_time == 1.23
        assert result[0].end_time == 3.99


class TestAssignSpeakerByOverlap:
    """Test speaker assignment logic."""

    @pytest.mark.parametrize(
        "segments,turns,min_overlap,expected_speakers",
        [
            # Perfect alignment - each segment maps to one turn
            (
                [
                    TranscriptionSegment(
                        id="seg-0", start_time=0.0, end_time=2.0, text="A", speaker=""
                    ),
                    TranscriptionSegment(
                        id="seg-1", start_time=2.0, end_time=4.0, text="B", speaker=""
                    ),
                ],
                [
                    SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
                    SpeakerTurn(start=2.0, end=4.0, speaker="SPEAKER_01"),
                ],
                0.1,
                ["SPEAKER_00", "SPEAKER_01"],
            ),
            # Partial overlap - segment spans multiple turns
            (
                [
                    TranscriptionSegment(
                        id="seg-0",
                        start_time=0.0,
                        end_time=5.0,
                        text="Long",
                        speaker="",
                    ),
                ],
                [
                    SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
                    SpeakerTurn(start=2.0, end=5.0, speaker="SPEAKER_01"),
                ],
                0.1,
                ["SPEAKER_01"],  # SPEAKER_01 has 3s overlap vs SPEAKER_00's 2s
            ),
            # No overlap - segment between turns
            (
                [
                    TranscriptionSegment(
                        id="seg-0", start_time=2.5, end_time=3.5, text="Gap", speaker=""
                    ),
                ],
                [
                    SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
                    SpeakerTurn(start=4.0, end=6.0, speaker="SPEAKER_01"),
                ],
                0.1,
                ["UNKNOWN"],
            ),
            # Weak overlap - below min_overlap_seconds threshold
            (
                [
                    TranscriptionSegment(
                        id="seg-0",
                        start_time=1.95,
                        end_time=2.05,
                        text="Brief",
                        speaker="",
                    ),
                ],
                [
                    SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
                    SpeakerTurn(start=2.0, end=4.0, speaker="SPEAKER_01"),
                ],
                0.1,  # min_overlap = 0.1s, but actual overlap is only 0.05s
                ["UNKNOWN"],
            ),
            # Empty turns
            (
                [
                    TranscriptionSegment(
                        id="seg-0", start_time=0.0, end_time=2.0, text="A", speaker=""
                    ),
                ],
                [],
                0.1,
                ["UNKNOWN"],
            ),
            # Empty segments
            ([], [SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00")], 0.1, []),
            # Multiple segments with same speaker
            (
                [
                    TranscriptionSegment(
                        id="seg-0", start_time=0.0, end_time=1.0, text="A", speaker=""
                    ),
                    TranscriptionSegment(
                        id="seg-1", start_time=1.0, end_time=2.0, text="B", speaker=""
                    ),
                ],
                [
                    SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
                ],
                0.1,
                ["SPEAKER_00", "SPEAKER_00"],
            ),
        ],
        ids=[
            "perfect_alignment",
            "partial_overlap_chooses_max",
            "no_overlap_unknown",
            "weak_overlap_below_threshold",
            "empty_turns",
            "empty_segments",
            "same_speaker_multiple_segments",
        ],
    )
    def test_assign_speaker_scenarios(
        self, segments, turns, min_overlap, expected_speakers
    ):
        """Test speaker assignment with various scenarios."""
        result = assign_speaker_by_overlap(
            segments, turns, min_overlap_seconds=min_overlap
        )

        assert len(result) == len(expected_speakers)
        for i, expected_speaker in enumerate(expected_speakers):
            assert result[i].speaker == expected_speaker

    def test_assign_speaker_preserves_segment_data(
        self, sample_transcription_segments, sample_speaker_turns
    ):
        """Test that speaker assignment preserves original segment data."""
        result = assign_speaker_by_overlap(
            sample_transcription_segments, sample_speaker_turns
        )

        # Check that text, start_time, end_time are preserved
        assert result[0].text == sample_transcription_segments[0].text
        assert result[0].start_time == sample_transcription_segments[0].start_time
        assert result[0].end_time == sample_transcription_segments[0].end_time

        # Check that overlap_seconds is populated
        assert result[0].overlap_seconds > 0.0

    def test_assign_speaker_custom_unknown_label(self, sample_transcription_segments):
        """Test custom unknown speaker label."""
        result = assign_speaker_by_overlap(
            sample_transcription_segments,
            [],  # No speaker turns
            unknown_speaker_label="NO_SPEAKER",
        )

        assert all(seg.speaker == "NO_SPEAKER" for seg in result)

    def test_assign_speaker_unsorted_turns(self):
        """Test that function handles unsorted speaker turns correctly."""
        segments = [
            TranscriptionSegment(
                id="seg-0", start_time=0.0, end_time=2.0, text="A", speaker=""
            ),
        ]

        # Provide unsorted turns
        turns = [
            SpeakerTurn(start=4.0, end=6.0, speaker="SPEAKER_01"),
            SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
        ]

        result = assign_speaker_by_overlap(segments, turns)

        # Should still correctly assign SPEAKER_00
        assert result[0].speaker == "SPEAKER_00"


class TestProcessTranscription:
    """Test end-to-end transcription processing."""

    @patch("services.transcription_service.diarize_with_pyannote")
    @patch("services.transcription_service.transcribe_with_whisper")
    def test_process_transcription_success(
        self,
        mock_transcribe,
        mock_diarize,
        sample_transcription_segments,
        sample_speaker_turns,
    ):
        """Test successful transcription processing."""
        mock_transcribe.return_value = sample_transcription_segments
        mock_diarize.return_value = sample_speaker_turns

        result = process_transcription(
            file_path="/fake/path/audio.mp3",
            file_name="audio.mp3",
            file_type="audio/mpeg",
            duration=10.5,
            language="en",
        )

        # Verify transcription was created
        assert result.status == TranscriptionStatus.COMPLETED
        assert result.file_name == "audio.mp3"
        assert result.file_type == "audio/mpeg"
        assert result.duration == 10.5
        assert result.language == "en"
        assert len(result.segments) == 3

        # Verify speakers were assigned
        assert result.segments[0].speaker != ""

    @patch("services.transcription_service.diarize_with_pyannote")
    @patch("services.transcription_service.transcribe_with_whisper")
    @patch("services.transcription_service.assign_speaker_by_overlap")
    def test_process_transcription_speaker_assignment_failure(
        self,
        mock_assign,
        mock_diarize,
        mock_transcribe,
        sample_transcription_segments,
        sample_speaker_turns,
    ):
        """Test transcription when speaker assignment fails."""
        mock_transcribe.return_value = sample_transcription_segments
        mock_diarize.return_value = sample_speaker_turns
        mock_assign.side_effect = Exception("Speaker assignment error")

        result = process_transcription(
            file_path="/fake/path/audio.mp3",
            file_name="audio.mp3",
            file_type="audio/mpeg",
            duration=10.5,
        )

        # Should mark as FAILED when speaker assignment fails
        assert result.status == TranscriptionStatus.FAILED

    @patch("services.transcription_service.diarize_with_pyannote")
    @patch("services.transcription_service.transcribe_with_whisper")
    def test_process_transcription_generates_unique_id(
        self, mock_transcribe, mock_diarize
    ):
        """Test that each transcription gets a unique ID."""
        mock_transcribe.return_value = []
        mock_diarize.return_value = []

        result1 = process_transcription("/path1.mp3", "file1.mp3", "audio/mpeg", 10.0)
        result2 = process_transcription("/path2.mp3", "file2.mp3", "audio/mpeg", 10.0)

        assert result1.id != result2.id

    @patch("services.transcription_service.diarize_with_pyannote")
    @patch("services.transcription_service.transcribe_with_whisper")
    def test_process_transcription_rounds_duration(self, mock_transcribe, mock_diarize):
        """Test that duration is rounded to 2 decimal places."""
        mock_transcribe.return_value = []
        mock_diarize.return_value = []

        result = process_transcription(
            "/path.mp3", "file.mp3", "audio/mpeg", duration=10.456789
        )

        assert result.duration == 10.46
