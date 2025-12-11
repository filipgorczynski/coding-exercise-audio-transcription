"""JSON-based storage for transcription data."""

import fcntl
import json
import os
from contextlib import contextmanager
from typing import Dict, List, Optional

from models.transcription import Transcription
from config import settings


class DataStorage:
    """Simple JSON file-based storage for transcriptions."""

    def __init__(self):
        self.data_file = os.path.join(settings.DATA_DIR, "transcriptions.json")
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Ensure data directory and file exist."""
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f:
                json.dump({}, f)

    @contextmanager
    def _lock_file(self, file_handle, mode):
        """Context manager for file locking."""
        fcntl.flock(file_handle, mode)
        try:
            yield file_handle
        finally:
            fcntl.flock(file_handle, fcntl.LOCK_UN)

    def _load_data(self) -> Dict:
        """Load all data from JSON file with read lock."""
        with open(self.data_file, "r") as f:
            with self._lock_file(f, fcntl.LOCK_SH):
                return json.load(f)

    def _save_data(self, data: Dict):
        """Save all data to JSON file with write lock."""
        with open(self.data_file, "w") as f:
            with self._lock_file(f, fcntl.LOCK_EX):
                json.dump(data, f, indent=2, default=str)

    def save(self, transcription: Transcription) -> Transcription:
        """Save a transcription."""
        data = self._load_data()
        data[transcription.id] = transcription.model_dump(mode="json")
        self._save_data(data)
        return transcription

    def get(self, transcription_id: str) -> Optional[Transcription]:
        """Retrieve a transcription by ID."""
        data = self._load_data()
        if transcription_id in data:
            return Transcription(**data[transcription_id])
        return None

    # TODO(fgorczynski): Ensure it is still needed
    # def update(
    #     self, transcription_id: str, transcription: Transcription
    # ) -> Transcription:
    #     """Update an existing transcription."""
    #     data = self._load_data()
    #     if transcription_id not in data:
    #         raise ValueError(f"Transcription {transcription_id} not found")
    #     data[transcription_id] = transcription.model_dump(mode="json")
    #     self._save_data(data)
    #     return transcription

    def list_all(self) -> List[Transcription]:
        """List all transcriptions."""
        data = self._load_data()
        return [Transcription(**t) for t in data.values()]


storage = DataStorage()
