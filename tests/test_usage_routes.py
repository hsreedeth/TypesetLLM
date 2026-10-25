"""Exercise API and MCP outcome instrumentation without running TeX."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from src import api, hosted_mcp
from src.conversion import ConversionFailure


@pytest.mark.asyncio
async def test_browser_events_are_validated_and_bounded(monkeypatch):
    capture = Mock()
    monkeypatch.setattr(api, 'capture', capture)
    identity = str(uuid4())
    async with AsyncClient(transport=ASGITransport(app=api.app), base_url='http://test') as client:
        good = await client.post('/analytics/events', json={'event': 'page_view', 'visitor_id': identity, 'markdown': 'private'})
        assert good.status_code == 204
        capture.assert_called_once_with('page_view', identity, 'web')
        capture.reset_mock()
        for payload in ({'event': 'conversion_succeeded', 'visitor_id': identity}, {'event': 'page_view', 'visitor_id': 'private'}, []):
            assert (await client.post('/analytics/events', json=payload)).status_code == 400
        assert (await client.post('/analytics/events', content='x' * 513)).status_code == 413
        await client.post('/analytics/events', headers={'DNT': '1'}, json={'event': 'page_view', 'visitor_id': identity})
        capture.assert_not_called()


@pytest.mark.asyncio
async def test_api_outcomes_and_opt_out(monkeypatch, tmp_path):
    capture = Mock()
    monkeypatch.setattr(api, 'capture', capture)
    path = tmp_path / 'output.pdf'
    path.write_bytes(b'%PDF-mocked')
    renderer = AsyncMock(return_value=SimpleNamespace(path=path, cleanup=lambda: None, warnings=[]))
    monkeypatch.setattr(api, 'render_markdown', renderer)
    identity = str(uuid4())
    async with AsyncClient(transport=ASGITransport(app=api.app), base_url='http://test') as client:
        assert (await client.post('/convert', headers={'X-Analytics-ID': identity}, json={'markdown_text': '# Private'})).status_code == 200
        capture.assert_called_with('conversion_succeeded', identity, 'web', 200)
        capture.reset_mock()
        await client.post('/convert', headers={'X-Analytics-Opt-Out': '1'}, json={'markdown_text': '# Private'})
        capture.assert_not_called()
        assert (await client.post('/convert', json={})).status_code == 422
        assert capture.call_args.args[0::2] == ('conversion_failed', 'api')
        renderer.side_effect = ConversionFailure('private error', 503)
        assert (await client.post('/convert', json={'markdown_text': '# Private'})).status_code == 503
        assert capture.call_args.args[-1] == 503


@pytest.mark.asyncio
async def test_mcp_outcomes_including_delivery_failure(monkeypatch):
    tools = {}
    class Server:
        def __init__(self, *args, **kwargs): pass
        def tool(self, **kwargs):
            def register(fn):
                tools[fn.__name__] = fn
                return fn
            return register
        def streamable_http_app(self, **kwargs): return Mock()
    monkeypatch.setattr(hosted_mcp, 'MCPServer', Server)
    capture = Mock()
    monkeypatch.setattr(hosted_mcp, 'capture', capture)
    rendered = SimpleNamespace(path='unused', cleanup=Mock(), warnings=[])
    renderer = AsyncMock(return_value=rendered)
    monkeypatch.setattr(hosted_mcp, 'render_markdown', renderer)
    item = SimpleNamespace(filename='report.pdf', expires_at=SimpleNamespace(isoformat=lambda: 'date'))
    store = Mock()
    store.put.return_value = ('token', item)
    hosted_mcp.build_mcp(Mock(), store, 'https://typesetllm.onrender.com')
    convert = tools['convert_markdown_to_pdf']
    await convert('# Private')
    assert capture.call_args.args[0::2] == ('conversion_succeeded', 'mcp')
    store.put.side_effect = RuntimeError('private filename')
    with pytest.raises(hosted_mcp.ToolError): await convert('# Private')
    assert capture.call_args.args[0::2] == ('conversion_failed', 'mcp')
    renderer.side_effect = ConversionFailure('private text', 400)
    with pytest.raises(hosted_mcp.ToolError): await convert('# Private')
    assert capture.call_args.args[-1] == 400
