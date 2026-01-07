"""File storage service for PVC-backed storage."""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import BinaryIO

import structlog

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException

logger = structlog.get_logger()


class FileStorage:
    """Store files on a shared PVC mounted path."""

    def __init__(self):
        if settings.STORAGE_MODE.lower() != "pvc":
            raise ServiceUnavailableException("Only STORAGE_MODE=pvc is supported")
        self.base_path = Path(settings.FILE_STORAGE_PATH)
        self.upload_dir = self.base_path / "uploads"
        self.images_dir = self.base_path / "ocr_images"

    def ensure_dirs(self) -> None:
        """Ensure required directories exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def _safe_filename(self, filename: str) -> str:
        name = os.path.basename(filename).replace(" ", "_")
        return "".join(ch for ch in name if ch.isalnum() or ch in ("_", "-", "."))

    def _safe_path(self, path: Path) -> Path:
        resolved = path.resolve()
        if not str(resolved).startswith(str(self.base_path.resolve())):
            raise ServiceUnavailableException("Invalid file path")
        return resolved

    def save_upload(self, file_obj: BinaryIO, filename: str) -> str:
        """Save uploaded file and return absolute path."""
        self.ensure_dirs()
        safe_name = self._safe_filename(filename)
        ext = Path(safe_name).suffix
        target = self.upload_dir / f"{uuid.uuid4().hex}{ext}"
        target = self._safe_path(target)
        with target.open("wb") as out:
            file_obj.seek(0)
            out.write(file_obj.read())
        logger.info("File saved", path=str(target))
        return str(target)

    def read_file(self, file_path: str) -> bytes:
        """Read file bytes from storage."""
        target = self._safe_path(Path(file_path))
        return target.read_bytes()

    def delete_file(self, file_path: str) -> None:
        """Delete file from storage."""
        target = self._safe_path(Path(file_path))
        if target.exists():
            target.unlink()
            logger.info("File deleted", path=str(target))
