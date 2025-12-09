"""Tests for file storage functions."""

import pytest
import os
from io import BytesIO
from unittest.mock import patch

from storage.file_storage import FileStorage


class TestFileStorage:
    """Test file system storage operations."""

    def test_init_creates_upload_dir(self, temp_dir):
        """Test that initialization creates upload directory."""
        with patch("storage.file_storage.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = temp_dir
            FileStorage()

        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)

    def test_save_file(self, temp_dir):
        """Test saving a file."""
        with patch("storage.file_storage.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = temp_dir
            storage = FileStorage()

        file_id = "test-id-123"
        filename = "audio.mp3"
        content = b"fake audio data"
        file_obj = BytesIO(content)

        file_path = storage.save_file(file_id, filename, file_obj)

        # Verify file was saved
        assert os.path.exists(file_path)
        assert file_path.endswith(f"{file_id}_{filename}")

        # Verify content
        with open(file_path, "rb") as f:
            saved_content = f.read()
        assert saved_content == content

    @pytest.mark.parametrize(
        "file_id,filename,expected_name",
        [
            ("id1", "test.mp3", "id1_test.mp3"),
            ("uuid-123", "my audio.wav", "uuid-123_my audio.wav"),
            ("abc", "file with spaces.mp4", "abc_file with spaces.mp4"),
        ],
        ids=["simple", "spaces_in_filename", "multiple_spaces"],
    )
    def test_save_file_naming(self, temp_dir, file_id, filename, expected_name):
        """Test filename generation."""
        with patch("storage.file_storage.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = temp_dir
            storage = FileStorage()

        file_obj = BytesIO(b"data")
        file_path = storage.save_file(file_id, filename, file_obj)

        assert file_path.endswith(expected_name)

    def test_get_file_path(self, temp_dir):
        """Test getting file path without saving."""
        with patch("storage.file_storage.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = temp_dir
            storage = FileStorage()

        file_id = "test-id"
        filename = "audio.mp3"

        file_path = storage.get_file_path(file_id, filename)

        assert file_path == os.path.join(temp_dir, f"{file_id}_{filename}")

    def test_save_large_file(self, temp_dir):
        """Test saving a large file."""
        with patch("storage.file_storage.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = temp_dir
            storage = FileStorage()

        # Create 10MB file
        large_content = b"x" * (10 * 1024 * 1024)
        file_obj = BytesIO(large_content)

        file_path = storage.save_file("large-id", "large.mp3", file_obj)

        # Verify size
        assert os.path.getsize(file_path) == len(large_content)

    def test_save_file_overwrites_existing(self, temp_dir):
        """Test that saving with same ID overwrites existing file."""
        with patch("storage.file_storage.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = temp_dir
            storage = FileStorage()

        file_id = "same-id"
        filename = "audio.mp3"

        # Save first file
        content1 = b"first content"
        storage.save_file(file_id, filename, BytesIO(content1))

        # Save second file with same ID
        content2 = b"second content"
        file_path = storage.save_file(file_id, filename, BytesIO(content2))

        # Verify second content was saved
        with open(file_path, "rb") as f:
            saved_content = f.read()
        assert saved_content == content2
