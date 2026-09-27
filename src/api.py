#!/usr/bin/env python
"""FastAPI web, REST, and hosted MCP service for Markdown-to-PDF rendering."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Final, Tuple

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.conversion import ALLOW_RAW_TEX, ConversionFailure, MAX_REQUEST_BYTES, render_markdown
from src.downloads import DownloadStore
from src.hosted_mcp import build_mcp
from src.naming import output_filename

@asynccontextmanager
async def renderer_lifespan(application: FastAPI):
    from src.smoke import run_smoke_check

    try:
        application.state.renderer_readiness = await asyncio.to_thread(run_smoke_check)
    except Exception:
        reference = uuid.uuid4().hex[:12]
        logging.exception("Renderer readiness failed [%s]", reference)
        application.state.renderer_readiness = {"status": "unavailable", "reference": reference}
    async with mcp_server.session_manager.run():
        cleanup_task = asyncio.create_task(_purge_downloads())
        try:
            yield
        finally:
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass
            download_store.close()


async def _purge_downloads() -> None:
    while True:
        await asyncio.sleep(60)
        download_store.purge()


app = FastAPI(title="Markdown → PDF API", version="0.5.1", lifespan=renderer_lifespan)


app.state.renderer_readiness = {"status": "starting"}


BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
WEB_DIR: Final[Path] = BASE_DIR / "web"
INDEX_HTML: Final[Path] = WEB_DIR / "index.html"
FONTS_DIR: Final[Path] = BASE_DIR / "fonts"

async def _extract_payload(request: Request) -> Tuple[str, str]:
    """Return (markdown_text, theme) or raise 422.

    Supported request styles:
      - JSON: {"markdown_text": "...", "theme": "vintage"}  (or "text")
      - Form: markdown_text=...&theme=...
      - Raw body: send markdown as-is (curl --data-binary @file.md)
    """

    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_REQUEST_BYTES:
                raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Request body too large.")
        except ValueError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid Content-Length header.")

    chunks: list[bytes] = []
    received = 0
    async for chunk in request.stream():
        received += len(chunk)
        if received > MAX_REQUEST_BYTES:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Request body too large.")
        chunks.append(chunk)
    # Starlette's JSON and form parsers can safely reuse this bounded body.
    request._body = b"".join(chunks)  # type: ignore[attr-defined]

    ct = request.headers.get("content-type", "").lower()
    markdown_text = None
    theme = "vintage"

    if ct.startswith("application/json"):
        # request.json() consumes the body stream; call it once and only here
        try:
            body: Any = json.loads(request._body)  # type: ignore[attr-defined]
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body.")
        if isinstance(body, dict):
            markdown_text = body.get("markdown_text") or body.get("text")
            theme = body.get("theme", theme)

    elif ct.startswith("application/x-www-form-urlencoded") or ct.startswith("multipart/form-data"):
        # same deal: request.form() consumes the stream
        try:
            form = await request.form()
        except Exception:
            form = None
        if form is not None:
            markdown_text = form.get("markdown_text") or form.get("text")  # type: ignore[arg-type]
            theme = form.get("theme") or theme  # type: ignore[arg-type]

    else:
        # last resort: treat whatever we got as bytes of markdown
        markdown_text = (await request.body()).decode()

    if not isinstance(markdown_text, str) or markdown_text.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="`markdown_text` (or `text`) required.",
        )

    return markdown_text, theme


if WEB_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

if FONTS_DIR.is_dir():
    app.mount("/fonts", StaticFiles(directory=FONTS_DIR), name="fonts")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    if not INDEX_HTML.is_file():
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Web app missing on server.")
    return FileResponse(INDEX_HTML, media_type="text/html")


MCP_HTML: Final[Path] = WEB_DIR / "mcp.html"


@app.get("/integrations", include_in_schema=False)
async def integrations_page() -> FileResponse:
    if not MCP_HTML.is_file():
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="MCP page missing on server.")
    return FileResponse(MCP_HTML, media_type="text/html")


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:  # noqa: D401
    # liveness probe (don't overthink it)
    return {"status": "ok"}


@app.get("/ready", tags=["meta"])
async def ready() -> JSONResponse:
    result = app.state.renderer_readiness
    code = status.HTTP_200_OK if result.get("status") == "ready" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(result, status_code=code)


@app.post("/convert", response_class=FileResponse, tags=["conversion"])
async def convert_endpoint(request: Request):  # noqa: D401
    markdown_text, theme = await _extract_payload(request)
    try:
        rendered = await render_markdown(markdown_text, theme, request.client.host if request.client else "unknown")
    except ConversionFailure as exc:
        raise HTTPException(
            exc.status_code, detail={"message": str(exc), "reference": exc.reference},
        ) from exc

    background_tasks = BackgroundTasks()
    background_tasks.add_task(rendered.cleanup)

    response = FileResponse(
        path=str(rendered.path),
        media_type="application/pdf",
        filename=output_filename(markdown_text),
        background=background_tasks,
    )
    response.headers["X-Typeset-Warnings"] = json.dumps(rendered.warnings, ensure_ascii=True)
    return response


download_store = DownloadStore()
PUBLIC_BASE_URL = os.environ.get("TYPESETLLM_PUBLIC_BASE_URL", "https://typesetllm.onrender.com").rstrip("/")


@app.get("/downloads/{token}.pdf", include_in_schema=False)
async def download_pdf(token: str):
    item = download_store.get(token)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Download not found or expired.")
    return FileResponse(item.path, media_type="application/pdf", filename=item.filename,
                        headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})


mcp_server, mcp_http_app = build_mcp(app, download_store, PUBLIC_BASE_URL,
                                     os.environ.get("TYPESETLLM_ALLOWED_HOSTS", ""))
app.mount("/", mcp_http_app, name="mcp")
