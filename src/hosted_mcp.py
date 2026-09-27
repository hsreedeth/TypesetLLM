"""Hosted Streamable HTTP MCP tools."""

from __future__ import annotations

from contextvars import ContextVar
import logging
from typing import TypedDict
from urllib.parse import urlparse
import uuid

from fastapi import FastAPI
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings

from src.conversion import ConversionFailure, MAX_REQUEST_BYTES, render_markdown
from src.downloads import DownloadStore
from src.naming import output_filename

client_ip: ContextVar[str] = ContextVar("typesetllm_client_ip", default="unknown")


class ConversionDelivery(TypedDict):
    download_url: str
    filename: str
    expires_at: str
    warnings: list[str]
    message: str


class ClientAddressMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        address = scope.get("client")
        token = client_ip.set(address[0] if address else "unknown")
        try:
            await self.app(scope, receive, send)
        finally:
            client_ip.reset(token)


def build_mcp(app: FastAPI, store: DownloadStore, public_base_url: str, extra_hosts: str = ""):
    parsed = urlparse(public_base_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path not in ("", "/"):
        raise ValueError("TYPESETLLM_PUBLIC_BASE_URL must be an HTTPS origin")

    server = MCPServer("TypesetLLM", instructions="Render Markdown to PDF. Download the returned URL into the client's workspace when the user requests a local file.")

    @server.tool(structured_output=True)
    async def convert_markdown_to_pdf(markdown_text: str, filename: str | None = None) -> ConversionDelivery:
        """Render Markdown as a PDF. Read local .md files into markdown_text first; download the returned HTTPS URL into the client's workspace when a local PDF is requested."""
        try:
            rendered = await render_markdown(markdown_text, "vintage", client_ip.get())
        except ConversionFailure as exc:
            raise ToolError(f"{exc} Reference ID: {exc.reference}") from exc
        try:
            token, item = store.put(rendered.path, output_filename(markdown_text, filename))
        except Exception as exc:
            reference = uuid.uuid4().hex[:12]
            logging.exception("PDF delivery failed [%s]", reference)
            raise ToolError(f"Could not prepare the PDF download. Reference ID: {reference}") from exc
        finally:
            rendered.cleanup()
        return {
            "download_url": f"{public_base_url}/downloads/{token}.pdf",
            "filename": item.filename,
            "expires_at": item.expires_at.isoformat(),
            "warnings": list(rendered.warnings),
            "message": "The PDF was rendered on TypesetLLM's server. Download the URL into your own workspace to save it here.",
        }

    @server.tool()
    async def typesetllm_status() -> dict:
        """Check whether the TypesetLLM renderer is ready."""
        return dict(app.state.renderer_readiness)

    allowed_hosts = [parsed.netloc, "localhost:*", "127.0.0.1:*", "[::1]:*"]
    allowed_hosts.extend(host.strip() for host in extra_hosts.split(",") if host.strip())
    transport_security = TransportSecuritySettings(
        allowed_hosts=allowed_hosts,
        allowed_origins=[public_base_url, "http://localhost:*", "http://127.0.0.1:*"],
    )
    http_app = server.streamable_http_app(
        json_response=True, stateless_http=True,
        max_request_body_size=MAX_REQUEST_BYTES + 16 * 1024,
        transport_security=transport_security,
    )
    return server, ClientAddressMiddleware(http_app)
