#!/usr/bin/env python
"""
FastAPI service – Markdown → PDF (rev B)
======================================
Fixes a bug where JSON requests were mistakenly treated as form-data first.,
consuming the body and yielding a 422e. Now we branch on Content-Type
once + we never read the body twice.
"""

from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Final, Tuple

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse

try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.util import get_remote_address
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    Limiter = None
    RateLimitExceeded = None
    SlowAPIMiddleware = None
    get_remote_address = None

# logging.basicConfig(level=logging.INFO)  # enable locally if you're chasing request flow
logger = logging.getLogger(__name__)

app = FastAPI(title="Markdown → PDF API", version="0.5.1")

def _no_limit(func: Callable[..., Any]) -> Callable[..., Any]:
    return func


if Limiter is not None and get_remote_address is not None and SlowAPIMiddleware is not None:
    # simple rate limit so someone can't spam LaTeX and pin the CPU
    limiter = Limiter(key_func=get_remote_address, default_limits=["60/hour"])
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    convert_limit = limiter.limit("60/hour")
else:  # pragma: no cover - depends on local environment
    limiter = None
    app.state.limiter = None
    convert_limit = _no_limit


if RateLimitExceeded is not None:
    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):  # noqa: D401
        # slowapi raises its own exception; we just return something consistent
        return JSONResponse({"detail": "Rate limit exceeded"}, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
TEMPLATES_DIR: Final[Path] = BASE_DIR / "templates"
DEFAULT_TEMPLATE: Final[Path] = TEMPLATES_DIR / "vintage.tex"

# guardrails: LaTeX can read/write files and spawn commands depending on config.
# this is not a sandbox, it's just removing the obvious foot-guns.
_DANGEROUS_RE = re.compile(r"\\(?:write18|input|include|openin|openout)")

# themes map to template filenames. don't accept paths or funny business.
_THEME_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _sanitize(md: str) -> str:
    # strip a few commands we never want making it into the template
    return _DANGEROUS_RE.sub("", md)


async def _extract_payload(request: Request) -> Tuple[str, str]:
    """Return (markdown_text, theme) or raise 422.

    Supported request styles:
      - JSON: {"markdown_text": "...", "theme": "vintage"}  (or "text")
      - Form: markdown_text=...&theme=...
      - Raw body: send markdown as-is (curl --data-binary @file.md)
    """

    ct = request.headers.get("content-type", "").lower()
    markdown_text = None
    theme = "vintage"

    if ct.startswith("application/json"):
        # request.json() consumes the body stream; call it once and only here
        try:
            body: Any = await request.json()
        except Exception:
            body = None
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


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:  # noqa: D401
    # liveness probe (don't overthink it)
    return {"status": "ok"}


@app.post("/convert", response_class=FileResponse, tags=["conversion"])
@convert_limit
async def convert_endpoint(request: Request, background_tasks: BackgroundTasks):  # noqa: D401
    # loud on purpose while this service is still settling down
    logger.critical("CRITICAL_LOG: convert_endpoint has been entered!")
    markdown_text, theme = await _extract_payload(request)

    md_clean = _sanitize(markdown_text)

    # theme is a template name, not user-controlled filesystem access
    if not _THEME_RE.fullmatch(theme):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid theme name.")

    tpl_path = (TEMPLATES_DIR / f"{theme}.tex").resolve()
    if not tpl_path.is_file():
        tpl_path = DEFAULT_TEMPLATE

    # if this triggers, the container/image is broken (or the deploy missed templates)
    if not tpl_path.is_file():
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Template missing on server.")

    # the converter works with file paths, so we materialize both ends
    md_tmp = NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
    md_tmp.write(md_clean)
    md_tmp.close()
    md_path = Path(md_tmp.name)

    pdf_tmp = NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_tmp.close()
    pdf_path = Path(pdf_tmp.name)

    # imports here so the module loads fast and errors are localized to conversion
    from src.cli import DEFAULT_MARKDOWN_FORMAT, convert as _convert_md_to_pdf

    try:
        # run the blocking conversion off the event loop
        await asyncio.to_thread(_convert_md_to_pdf, md_path, pdf_path, DEFAULT_MARKDOWN_FORMAT, tpl_path)

        # cheap sanity check; empty output usually means a LaTeX/pandoc failure upstream
        if pdf_path.stat().st_size == 0:
            raise RuntimeError("Empty PDF generated.")
    except Exception:
        logging.exception("Conversion failed.")
        md_path.unlink(missing_ok=True)
        pdf_path.unlink(missing_ok=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate PDF.")

    # FileResponse streams the file; cleanup has to happen after the response is sent
    background_tasks.add_task(md_path.unlink, missing_ok=True)
    background_tasks.add_task(pdf_path.unlink, missing_ok=True)

    return FileResponse(path=str(pdf_path), media_type="application/pdf", filename="converted_document.pdf")
