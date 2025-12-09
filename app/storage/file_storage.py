"""File system storage for uploaded files."""

import os
import shutil
from typing import BinaryIO
from config import settings


class FileStorage:
    """Handle file system operations for uploads."""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Ensure upload directory exists."""
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file_id: str, filename: str, file_obj: BinaryIO) -> str:
        """Save an uploaded file."""
        print("Saving file:", file_id, filename)
        safe_filename = f"{file_id}_{filename}"
        file_path = os.path.join(self.upload_dir, safe_filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file_obj, f)

        return file_path

    def get_file_path(self, file_id: str, filename: str) -> str:
        """Get the full path for a file."""
        safe_filename = f"{file_id}_{filename}"
        return os.path.join(self.upload_dir, safe_filename)


file_storage = FileStorage()
