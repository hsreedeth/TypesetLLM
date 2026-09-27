"""Shared, bounded rendering for the web API and hosted MCP tools."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass
import logging
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
import uuid

from src.cli import CONVERSION_TIMEOUT_SECONDS, ConversionError, ConversionResult, WEB_MARKDOWN_FORMAT, convert_with_diagnostics

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
MAX_REQUEST_BYTES = int(os.environ.get("MAX_REQUEST_BYTES", "1048576"))
MAX_CONCURRENT_CONVERSIONS = int(os.environ.get("MAX_CONCURRENT_CONVERSIONS", "1"))
CONVERSION_RATE_LIMIT_PER_HOUR = int(os.environ.get("CONVERSION_RATE_LIMIT_PER_HOUR", "60"))
ALLOW_RAW_TEX = os.environ.get("ALLOW_RAW_TEX", "false").lower() in {"1", "true", "yes"}
_slots = asyncio.Semaphore(MAX_CONCURRENT_CONVERSIONS)
_rate_lock = asyncio.Lock()
_requests: dict[str, deque[float]] = defaultdict(deque)
_theme_re = re.compile(r"^[A-Za-z0-9_-]+$")


@dataclass
class RenderedPDF:
    path: Path
    warnings: tuple[str, ...]
    directory: Path

    def cleanup(self) -> None:
        shutil.rmtree(self.directory, ignore_errors=True)


class ConversionFailure(Exception):
    def __init__(self, message: str, status_code: int, reference: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.reference = reference or uuid.uuid4().hex[:12]


async def _check_rate_limit(client_key: str) -> None:
    now = time.monotonic()
    async with _rate_lock:
        calls = _requests[client_key]
        while calls and calls[0] <= now - 3600:
            calls.popleft()
        if len(calls) >= CONVERSION_RATE_LIMIT_PER_HOUR:
            raise ConversionFailure("Conversion rate limit exceeded; try again later.", 429)
        calls.append(now)


async def render_markdown(markdown: str, theme: str, client_key: str) -> RenderedPDF:
    if not isinstance(markdown, str) or not markdown.strip():
        raise ConversionFailure("Markdown text is required.", 422)
    if len(markdown.encode("utf-8")) > MAX_REQUEST_BYTES:
        raise ConversionFailure("Markdown exceeds the input size limit.", 413)
    if not isinstance(theme, str) or not _theme_re.fullmatch(theme):
        raise ConversionFailure("Invalid theme name.", 400)
    template = TEMPLATES_DIR / f"{theme}.tex"
    if not template.is_file():
        template = TEMPLATES_DIR / "vintage.tex"
    if not template.is_file():
        raise ConversionFailure("Template missing on server.", 500)
    await _check_rate_limit(client_key)

    directory = Path(tempfile.mkdtemp(prefix="typesetllm-render-"))
    source = directory / "input.md"
    output = directory / "output.pdf"
    acquired = False
    try:
        source.write_text(markdown, encoding="utf-8")
        try:
            await asyncio.wait_for(_slots.acquire(), timeout=CONVERSION_TIMEOUT_SECONDS)
            acquired = True
        except asyncio.TimeoutError as exc:
            raise ConversionFailure("Renderer is busy; try again later.", 503) from exc
        fmt = WEB_MARKDOWN_FORMAT if not ALLOW_RAW_TEX else WEB_MARKDOWN_FORMAT.replace("-raw_tex", "+raw_tex")
        worker = asyncio.create_task(asyncio.to_thread(convert_with_diagnostics, source, output, fmt, template))
        try:
            result: ConversionResult = await asyncio.shield(worker)
        except asyncio.CancelledError:
            # A disconnected client must not release the shared slot while TeX runs.
            await asyncio.shield(worker)
            raise
        if not output.is_file() or output.stat().st_size == 0:
            raise ConversionError("The renderer produced an empty PDF.")
        return RenderedPDF(output, result.warnings, directory)
    except ConversionFailure:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    except asyncio.CancelledError:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    except Exception as exc:
        reference = uuid.uuid4().hex[:12]
        logging.exception("Conversion failed [%s]", reference)
        shutil.rmtree(directory, ignore_errors=True)
        user_error = isinstance(exc, ConversionError) and exc.input_error
        message = str(exc) if isinstance(exc, ConversionError) else "Could not generate PDF."
        raise ConversionFailure(message, 422 if user_error else 500, reference) from exc
    finally:
        if acquired:
            _slots.release()
