"""Tests for file service functions."""

import pytest
from unittest.mock import patch

from services.file_service import file_service


class TestFileServiceDuration:
    """Test file duration extraction."""

    @patch("services.file_service.ffmpeg.probe")
    @pytest.mark.parametrize(
        "duration_str,expected",
        [
            ("10.5", 10.5),
            ("0.5", 0.5),
            ("120.123456", 120.12),
            # ("3600.99", 3601.0),  # 1 hour
            ("0.0", 0.0),
            ("5", 5.0),
        ],
        ids=["normal", "short", "precise", "zero", "integer"],
    )
    def test_get_file_duration(self, mock_probe, duration_str, expected):
        """Test duration extraction with various values."""
        mock_probe.return_value = {"format": {"duration": duration_str}}

        result = file_service.get_file_duration("/fake/path/audio.mp3")

        assert result == expected
        mock_probe.assert_called_once_with("/fake/path/audio.mp3")

    @patch("services.file_service.ffmpeg.probe")
    def test_get_file_duration_missing_format(self, mock_probe):
        """Test duration extraction when format info is missing."""
        mock_probe.return_value = {}

        with pytest.raises(KeyError):
            file_service.get_file_duration("/fake/path/audio.mp3")

    @patch("services.file_service.ffmpeg.probe")
    def test_get_file_duration_probe_error(self, mock_probe):
        """Test duration extraction when ffmpeg probe fails."""
        mock_probe.side_effect = Exception("FFmpeg error")

        with pytest.raises(Exception, match="FFmpeg error"):
            file_service.get_file_duration("/fake/path/audio.mp3")
