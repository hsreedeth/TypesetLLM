import sys
from pathlib import Path
import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

# ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import app

@pytest.mark.asyncio
async def test_happy_path(tmp_path):
    payload = {"text": "# Hello API\n\nTest content.", "theme": "vintage"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/convert", json=payload)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers.get("content-type") == "application/pdf"
    assert len(resp.content) > 5000

@pytest.mark.asyncio
async def test_large_input_rejected():
    # 10,001 characters should exceed limit
    long_text = "a" * 10001
    payload = {"text": long_text, "theme": "vintage"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/convert", json=payload)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_latex_injection_sanitized(tmp_path):
    malicious = "# Title\n\nHello \\write18{rm -rf /}"  # text contains dangerous command
    payload = {"text": malicious, "theme": "vintage"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/convert", json=payload)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers.get("content-type") == "application/pdf"
    assert len(resp.content) > 5000

@pytest.mark.asyncio
async def test_missing_text_field_400():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # omit 'text'
        resp = await ac.post("/convert", json={"theme": "vintage"})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
