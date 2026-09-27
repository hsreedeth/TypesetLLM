"""End-to-end Streamable HTTP MCP checks against the FastAPI app."""

import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import pytest
from httpx import ASGITransport, AsyncClient
import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from src.api import app, download_store, renderer_lifespan
import src.conversion as conversion
from src.conversion import MAX_REQUEST_BYTES

HEADERS = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
    "MCP-Protocol-Version": "2025-03-26",
}


async def call(client, method, params=None, request_id=1):
    response = await client.post(
        "/mcp", headers=HEADERS,
        json={"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}},
    )
    assert response.status_code == 200, response.text
    return response.json()["result"]


@pytest.mark.asyncio
async def test_hosted_mcp_protocol_render_and_download(monkeypatch):
    markdown = """# Integration report

| Item | Value |
|:-----|------:|
| Alpha | 42 |

$$E = mc^2$$

```python
print('hello')
```
"""
    # The SDK manager is single-use, matching the app's process lifespan.
    async with renderer_lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            guide = await client.get("/integrations")
            assert guide.status_code == 200
            assert "codex mcp add typesetllm --url https://typesetllm.onrender.com/mcp" in guide.text
            initialized = await call(client, "initialize", {
                "protocolVersion": "2025-03-26", "capabilities": {},
                "clientInfo": {"name": "integration-test", "version": "1"},
            })
            assert initialized["serverInfo"]["name"] == "TypesetLLM"
            names = {tool["name"] for tool in (await call(client, "tools/list"))["tools"]}
            assert names == {"convert_markdown_to_pdf", "typesetllm_status"}
            renderer = await call(client, "tools/call", {"name": "typesetllm_status", "arguments": {}})
            assert renderer["isError"] is False

            result = await call(client, "tools/call", {
                "name": "convert_markdown_to_pdf", "arguments": {"markdown_text": markdown},
            })
            assert result["isError"] is False
            delivery = result["structuredContent"]
            assert delivery["download_url"].startswith("https://typesetllm.onrender.com/downloads/")
            assert delivery["filename"] == "integration-report.pdf"
            assert datetime.fromisoformat(delivery["expires_at"]) > datetime.now(timezone.utc)
            assert isinstance(delivery["warnings"], list)
            assert "download" in delivery["message"].lower()
            assert "base64" not in json.dumps(result).lower()

            path = urlparse(delivery["download_url"]).path
            pdf = await client.get(path)
            assert pdf.status_code == 200
            assert pdf.headers["content-type"].startswith("application/pdf")
            assert len(pdf.content) > 1000
            assert pdf.content.startswith(b"%PDF-")
            assert pdf.content.rstrip().endswith(b"%%EOF")
            assert (await client.get("/downloads/" + "a" * 64 + ".pdf")).status_code == 404
            assert (await client.get("/downloads/..%2Fsecret.pdf")).status_code == 404

            token = path.rsplit("/", 1)[1].removesuffix(".pdf")
            item = download_store._files[token]
            download_store._files[token] = replace(item, expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))
            assert (await client.get(path)).status_code == 404
            assert not item.path.exists()

            malformed = await call(client, "tools/call", {
                "name": "convert_markdown_to_pdf",
                "arguments": {"markdown_text": "# Invalid\n\n$$\n\\frac{1}{\n$$"},
            })
            assert malformed["isError"] is True
            assert "Reference ID:" in malformed["content"][0]["text"]
            assert "equation" in malformed["content"][0]["text"]

            too_large = await call(client, "tools/call", {
                "name": "convert_markdown_to_pdf",
                "arguments": {"markdown_text": "x" * (MAX_REQUEST_BYTES + 1)},
            })
            assert too_large["isError"] is True
            assert "size limit" in too_large["content"][0]["text"]
            assert "Reference ID:" in too_large["content"][0]["text"]

            # A website/API conversion uses the same client budget as MCP.
            conversion._requests.clear()
            monkeypatch.setattr(conversion, "CONVERSION_RATE_LIMIT_PER_HOUR", 1)
            try:
                rest = await client.post("/convert", json={"markdown_text": "# Budget"})
                assert rest.status_code == 200
                limited = await call(client, "tools/call", {
                    "name": "convert_markdown_to_pdf", "arguments": {"markdown_text": "# Budget again"},
                })
                assert limited["isError"] is True
                assert "rate limit" in limited["content"][0]["text"]
            finally:
                conversion._requests.clear()

        # Also negotiate and call a tool through the official MCP client.
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app), base_url="http://localhost:8000"
        ) as http_client:
            async with streamable_http_client("http://localhost:8000/mcp", http_client=http_client) as (read, write):
                async with ClientSession(read, write) as session:
                    initialized = await session.initialize()
                    assert initialized.server_info.name == "TypesetLLM"
                    assert {tool.name for tool in (await session.list_tools()).tools} == {
                        "convert_markdown_to_pdf", "typesetllm_status"
                    }
                    assert (await session.call_tool("typesetllm_status")).is_error is False
