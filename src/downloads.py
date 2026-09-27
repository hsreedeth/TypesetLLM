"""Short-lived PDF downloads for remote MCP clients."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import re
import shutil
import tempfile
import uuid


@dataclass(frozen=True)
class Download:
    path: Path
    filename: str
    expires_at: datetime


class DownloadStore:
    def __init__(self) -> None:
        self.directory = Path(tempfile.mkdtemp(prefix="typesetllm-downloads-"))
        self.retention_seconds = int(os.environ.get("TYPESETLLM_DOWNLOAD_RETENTION_SECONDS", "900"))
        if self.retention_seconds <= 0:
            raise ValueError("TYPESETLLM_DOWNLOAD_RETENTION_SECONDS must be positive")
        self._files: dict[str, Download] = {}

    def put(self, source: Path, filename: str) -> tuple[str, Download]:
        self.purge()
        self.directory.mkdir(parents=True, exist_ok=True)
        token = uuid.uuid4().hex + uuid.uuid4().hex
        target = self.directory / f"{token}.pdf"
        shutil.move(str(source), target)
        item = Download(target, filename, datetime.now(timezone.utc) + timedelta(seconds=self.retention_seconds))
        self._files[token] = item
        return token, item

    def get(self, token: str) -> Download | None:
        if not re.fullmatch(r"[0-9a-f]{64}", token):
            return None
        self.purge()
        item = self._files.get(token)
        return item if item and item.path.is_file() else None

    def purge(self) -> None:
        now = datetime.now(timezone.utc)
        for token, item in list(self._files.items()):
            if item.expires_at <= now:
                item.path.unlink(missing_ok=True)
                del self._files[token]

    def close(self) -> None:
        shutil.rmtree(self.directory, ignore_errors=True)
        self._files.clear()
