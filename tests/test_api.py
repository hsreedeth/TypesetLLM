# tests/test_api.py

import sys
from pathlib import Path

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

# make sure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import app, MAX_SIZE



# 1. client fixture as a normal (synchronous) factory

@pytest.fixture
def client() -> AsyncClient:
    """
    Return an AsyncClient bound to the FastAPI app.
    Tests will call `await client.post(...)` directly.
    """
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# -------------------------------------------------------------------- ##
@pytest.mark.asyncio
async def test_convert_form_success(client: AsyncClient):
    """
    Sending form-encoded `markdown_text` + `theme` should return 200 + application/pdf.
    """
    resp = await client.post(
        "/convert",
        data={
            "markdown_text": "# Hi\n\n**Form payload**",
            "theme": "vintage",
        },
    )
    if resp.status_code != status.HTTP_200_OK:
        # Debug output if it fails
        print("➡️  DEBUG status:", resp.status_code)
        print("➡️  DEBUG body:", resp.text)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"].startswith("application/pdf")
    assert resp.content.startswith(b"%PDF-")


# -------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_convert_json_success(client: AsyncClient):
    """
    Sending JSON with `markdown_text` + `theme` should return 200 + application/pdf.
    """
    payload = {
        "markdown_text": "# JSON\n\n*payload*",
        "theme": "vintage",
    }
    resp = await client.post("/convert", json=payload)
    if resp.status_code != status.HTTP_200_OK:
        print("➡️  DEBUG status:", resp.status_code)
        print("➡️  DEBUG body:", resp.text)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"].startswith("application/pdf")
    assert resp.content.startswith(b"%PDF-")


# -------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_payload_too_large(client: AsyncClient):
    """
    One byte over MAX_SIZE (10,000) should be rejected with 422 + 'too large'.
    """
    long_text = "a" * (MAX_SIZE + 1)
    resp = await client.post(
        "/convert",
        data={
            "markdown_text": long_text,
            "theme": "vintage",
        },
    )
    if resp.status_code != status.HTTP_422_UNPROCESSABLE_ENTITY:
        print("➡️  DEBUG status:", resp.status_code)
        print("➡️  DEBUG body:", resp.text)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    detail = resp.json().get("detail")
    # detail might be a string (our custom HTTPException) or a list (default validation)
    if isinstance(detail, str):
        assert "too large" in detail.lower()
    else:
        # Join all error messages and check
        combined = " ".join(map(str, detail)).lower()
        assert "too large" in combined


## -------------------------------------------------------------------- ##
@pytest.mark.asyncio
async def test_latex_injection_sanitised(client: AsyncClient):
    """
    Malicious LaTeX commands (e.g. \write18) should be stripped,
    and the conversion should still succeed.
    """
    malicious = "# Title\n\nHello \\write18{rm -rf /}"
    resp = await client.post(
        "/convert",
        data={
            "markdown_text": malicious,
            "theme": "vintage",
        },
    )
    if resp.status_code != status.HTTP_200_OK:
        print("➡️  DEBUG status:", resp.status_code)
        print("➡️  DEBUG body:", resp.text)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"].startswith("application/pdf")
    assert resp.content.startswith(b"%PDF-")


# -------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_missing_markdown_field(client: AsyncClient):
    """
    Omitting 'markdown_text' (or 'text') entirely should yield 422.
    """
    resp = await client.post(
        "/convert",
        data={"theme": "vintage"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
