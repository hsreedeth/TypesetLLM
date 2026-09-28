"""
TypesetLLM MCP server.

Wraps the TypesetLLM web service (Pandoc + XeLaTeX behind a FastAPI /convert
endpoint) as a single MCP tool: convert_markdown_to_pdf.

Repo:    https://github.com/hsreedeth/TypesetLLM
Default deployment: https://typesetllm.onrender.com

Run (stdio transport, for Claude Desktop / Claude Code):
    python server.py

Environment variables:
    TYPESETLLM_URL     Base URL of the deployed service.
                        Default: https://typesetllm.onrender.com
    TYPESETLLM_OUTDIR  Directory to write returned PDFs into.
                        Default: ~/typesetllm-output
    TYPESETLLM_TIMEOUT Client-side request timeout in seconds.
                        Default: 90 (covers Render free-tier cold starts;
                        the server's own conversion timeout is 45s once warm)
"""

import os
import re
import unicodedata
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

TYPESETLLM_URL = os.environ.get("TYPESETLLM_URL", "https://typesetllm.onrender.com").rstrip("/")
OUTDIR = Path(os.environ.get("TYPESETLLM_OUTDIR", str(Path.home() / "typesetllm-output")))
TIMEOUT = float(os.environ.get("TYPESETLLM_TIMEOUT", "90"))

# Mirrors the service's own default cap (MAX_REQUEST_BYTES), so we can fail
# fast locally with a clear message instead of waiting on a 413 round trip.
MAX_REQUEST_BYTES = int(os.environ.get("TYPESETLLM_MAX_BYTES", "1048576"))

mcp = FastMCP("typesetllm")


def _slugify(text: str, fallback: str = "output") -> str:
    """Turn a doc title / first heading into a safe filename stem."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:80] or fallback


def _derive_stem(markdown_text: str) -> str:
    for line in markdown_text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return _slugify(line.lstrip("#").strip())
    return "output"


@mcp.tool()
def convert_markdown_to_pdf(markdown_text: str, filename: str | None = None) -> str:
    """
    Render Markdown into a handout-style, typeset PDF (via Pandoc + XeLaTeX)
    and save it to disk.

    Good for turning an LLM-generated report, note, or short-form writeup
    into a properly typeset document (tables, math, code blocks, scientific
    superscripts all supported). Mermaid diagrams and unresolved citation
    keys are not supported and will come back as warnings, not silent
    failures.

    Args:
        markdown_text: The Markdown source to render.
        filename: Optional output filename (without extension). If omitted,
            it's derived from the document's first heading.

    Returns:
        A message with the local path the PDF was saved to, plus any
        quality warnings the renderer reported.
    """
    size = len(markdown_text.encode("utf-8"))
    if size > MAX_REQUEST_BYTES:
        return (
            f"Markdown is {size} bytes, which exceeds the service's "
            f"{MAX_REQUEST_BYTES}-byte request limit. Shorten the document "
            f"or split it and convert in parts."
        )

    try:
        resp = httpx.post(
            f"{TYPESETLLM_URL}/convert",
            json={"markdown_text": markdown_text},
            timeout=TIMEOUT,
        )
    except httpx.TimeoutException:
        return (
            f"Request to {TYPESETLLM_URL} timed out after {TIMEOUT}s. "
            "If this is a Render free-tier instance, it may have been "
            "asleep and needed a cold start — try again."
        )
    except httpx.RequestError as e:
        return f"Could not reach {TYPESETLLM_URL}: {e}"

    if resp.status_code != 200:
        detail = resp.text[:500]
        return f"Conversion failed (HTTP {resp.status_code}): {detail}"

    stem = _slugify(filename) if filename else _derive_stem(markdown_text)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTDIR / f"{stem}.pdf"
    n = 1
    while out_path.exists():
        out_path = OUTDIR / f"{stem}-{n}.pdf"
        n += 1
    out_path.write_bytes(resp.content)

    warnings = resp.headers.get("X-Typeset-Warnings")
    msg = f"Saved PDF to {out_path}"
    if warnings:
        msg += f"\n\nQuality warnings from the renderer: {warnings}"
    return msg


@mcp.tool()
def typesetllm_status() -> str:
    """Check whether the TypesetLLM service is reachable and ready (hits /ready)."""
    try:
        resp = httpx.get(f"{TYPESETLLM_URL}/ready", timeout=15)
    except httpx.RequestError as e:
        return f"Could not reach {TYPESETLLM_URL}: {e}"
    if resp.status_code == 200:
        return f"{TYPESETLLM_URL} is ready."
    return f"{TYPESETLLM_URL} returned HTTP {resp.status_code} from /ready (not ready yet — may be cold-starting)."


if __name__ == "__main__":
    mcp.run(transport="stdio")
