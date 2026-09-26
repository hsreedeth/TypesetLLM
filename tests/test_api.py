# tests/test_api.py

import sys
from pathlib import Path

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

# make sure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import app



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
async def test_index_page_served(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == status.HTTP_200_OK
    assert "typesetllm" in resp.text.lower()
    assert "convert to pdf" in resp.text.lower()


@pytest.mark.asyncio
async def test_renderer_readiness_is_a_real_render(client: AsyncClient):
    from src.api import renderer_lifespan

    async with renderer_lifespan(app):
        response = await client.get("/ready")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ready"
    assert response.json()["pandoc"].startswith("pandoc")


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


@pytest.mark.asyncio
async def test_named_output_and_warnings(client: AsyncClient):
    resp = await client.post(
        "/convert",
        json={"markdown_text": "---\ntitle: Synthetic report\n---\n\n# Result\n\n[@missing2026]"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "synthetic-report.pdf" in resp.headers["content-disposition"]
    assert "missing2026" in resp.headers["x-typeset-warnings"]


@pytest.mark.asyncio
async def test_malformed_math_returns_reference(client: AsyncClient):
    resp = await client.post(
        "/convert",
        json={"markdown_text": "# Invalid\n\n$$\n\\frac{1}{\n$$"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.json()["detail"]["reference"]
    assert "equation" in resp.json()["detail"]["message"]


# -------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_large_payload_success(client: AsyncClient):
    """
    Large markdown bodies should still be converted.
    """
    paragraph = "This is a large markdown document with enough spaces to wrap correctly. " * 40
    long_text = "# Big\n\n" + "\n\n".join(paragraph for _ in range(80))
    resp = await client.post(
        "/convert",
        data={
            "markdown_text": long_text,
            "theme": "vintage",
        },
    )
    if resp.status_code != status.HTTP_200_OK:
        print("➡️  DEBUG status:", resp.status_code)
        print("➡️  DEBUG body:", resp.text)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"].startswith("application/pdf")
    assert resp.content.startswith(b"%PDF-")


## -------------------------------------------------------------------- ##
@pytest.mark.asyncio
async def test_raw_tex_disabled(client: AsyncClient):
    """Untrusted raw TeX commands should not prevent PDF conversion."""
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


@pytest.mark.asyncio
async def test_labeled_bidirectional_arrows_with_raw_tex_disabled(client: AsyncClient):
    """Supported math commands render through the public API's normal safe path."""
    from src.api import ALLOW_RAW_TEX

    assert ALLOW_RAW_TEX is False
    resp = await client.post(
        "/convert",
        json={"markdown_text": "# Weighted graph\n\n$$1 \\xleftrightarrow{2} 2$$"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    assert resp.headers["content-type"].startswith("application/pdf")
    assert resp.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_literal_tex_in_code_is_preserved(client: AsyncClient):
    resp = await client.post(
        "/convert",
        json={"markdown_text": "# Literal command\n\n```tex\n\\input{example.tex}\n```"},
    )
    assert resp.status_code == status.HTTP_200_OK
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


@pytest.mark.asyncio
async def test_oversized_payload_rejected(client: AsyncClient):
    from src.api import MAX_REQUEST_BYTES

    resp = await client.post(
        "/convert",
        content=b"x" * (MAX_REQUEST_BYTES + 1),
        headers={"content-type": "text/plain"},
    )
    assert resp.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


@pytest.mark.asyncio
async def test_invalid_json_rejected(client: AsyncClient):
    resp = await client.post(
        "/convert",
        content=b"{not-json}",
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
