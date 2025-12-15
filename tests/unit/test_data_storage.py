"""Tests for data storage functions."""

import pytest
import json
import os
from unittest.mock import patch
import fcntl


from storage.data_storage import DataStorage
from models.transcription import Transcription, TranscriptionStatus


class TestDataStorage:
    """Test JSON data storage with file locking."""

    def test_init_creates_data_file(self, temp_dir):
        """Test that initialization creates data directory and file."""
        data_file = os.path.join(temp_dir, "transcriptions.json")

        with patch("storage.data_storage.settings") as mock_settings:
            mock_settings.DATA_DIR = temp_dir
            DataStorage()

        assert os.path.exists(data_file)
        with open(data_file, "r") as f:
            data = json.load(f)
            assert data == {}

    def test_save_transcription(self, temp_dir, sample_transcription):
        """Test saving a transcription."""
        with patch("storage.data_storage.settings") as mock_settings:
            mock_settings.DATA_DIR = temp_dir
            storage = DataStorage()

        result = storage.save(sample_transcription)

        assert result.id == sample_transcription.id

        # Verify it was saved to file
        saved_data = storage._load_data()
        assert sample_transcription.id in saved_data
        assert saved_data[sample_transcription.id]["file_name"] == "test_audio.mp3"

    def test_get_transcription_exists(self, temp_dir, sample_transcription):
        """Test retrieving an existing transcription."""
        with patch("storage.data_storage.settings") as mock_settings:
            mock_settings.DATA_DIR = temp_dir
            storage = DataStorage()

        storage.save(sample_transcription)

        result = storage.get(sample_transcription.id)

        assert result is not None
        assert result.id == sample_transcription.id
        assert result.file_name == sample_transcription.file_name

    def test_get_transcription_not_exists(self, temp_dir):
        """Test retrieving a non-existent transcription."""
        with patch("storage.data_storage.settings") as mock_settings:
            mock_settings.DATA_DIR = temp_dir
            storage = DataStorage()

        result = storage.get("non-existent-id")

        assert result is None

    def test_list_all_empty(self, temp_dir):
        """Test listing when no transcriptions exist."""
        with patch("storage.data_storage.settings") as mock_settings:
            mock_settings.DATA_DIR = temp_dir
            storage = DataStorage()

        result = storage.list_all()

        assert result == []

    def test_list_all_multiple(self, temp_dir):
        """Test listing multiple transcriptions."""
        with patch("storage.data_storage.settings") as mock_settings:
            mock_settings.DATA_DIR = temp_dir
            storage = DataStorage()

        # Create and save multiple transcriptions
        transcriptions = []
        for i in range(3):
            t = Transcription(
                id=f"id-{i}",
                status=TranscriptionStatus.COMPLETED,
                file_name=f"file{i}.mp3",
                file_type="audio/mpeg",
                duration=10.0,
                segments=[],
            )
            storage.save(t)
            transcriptions.append(t)

        result = storage.list_all()

        assert len(result) == 3
        result_ids = [t.id for t in result]
        for t in transcriptions:
            assert t.id in result_ids

    @pytest.mark.parametrize(
        "lock_mode,expected_flag",
        [
            ("read", fcntl.LOCK_SH),
            ("write", fcntl.LOCK_EX),
        ],
        ids=["read_lock", "write_lock"],
    )
    def test_file_locking(self, temp_dir, lock_mode, expected_flag):
        """Test that file locking is applied correctly."""
        with patch("storage.data_storage.settings") as mock_settings:
            mock_settings.DATA_DIR = temp_dir
            storage = DataStorage()

        with patch("fcntl.flock") as mock_flock:
            if lock_mode == "read":
                storage._load_data()
                # First call is LOCK_SH, second is LOCK_UN
                assert mock_flock.call_count == 2
                assert mock_flock.call_args_list[0][0][1] == fcntl.LOCK_SH
            else:
                storage._save_data({})
                # First call is LOCK_EX, second is LOCK_UN
                assert mock_flock.call_count == 2
                assert mock_flock.call_args_list[0][0][1] == fcntl.LOCK_EX

    def test_save_overwrites_existing(self, temp_dir, sample_transcription):
        """Test that saving with same ID overwrites existing data."""
        with patch("storage.data_storage.settings") as mock_settings:
            mock_settings.DATA_DIR = temp_dir
            storage = DataStorage()

        # Save initial
        storage.save(sample_transcription)

        # Modify and save again
        sample_transcription.status = TranscriptionStatus.FAILED
        storage.save(sample_transcription)

        # Verify it was updated
        result = storage.get(sample_transcription.id)
        assert result.status == TranscriptionStatus.FAILED

        # Verify only one entry exists
        all_items = storage.list_all()
        assert len(all_items) == 1

    def test_model_dump_serialization(self, temp_dir):
        """Test that transcriptions are serialized correctly using model_dump."""
        with patch("storage.data_storage.settings") as mock_settings:
            mock_settings.DATA_DIR = temp_dir
            storage = DataStorage()

        t = Transcription(
            id="test-id",
            status=TranscriptionStatus.COMPLETED,
            file_name="test.mp3",
            file_type="audio/mpeg",
            duration=10.5,
            segments=[],
        )

        storage.save(t)

        # Read raw JSON
        with open(storage.data_file, "r") as f:
            raw_data = json.load(f)

        # Verify enum is serialized as string
        assert raw_data["test-id"]["status"] == "completed"
