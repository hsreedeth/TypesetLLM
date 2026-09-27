# TypesetLLM MCP

TypesetLLM hosts a Streamable HTTP MCP server at `https://typesetllm.onrender.com/mcp`.

## Codex

```sh
codex mcp add typesetllm --url https://typesetllm.onrender.com/mcp
codex mcp list
```

Reconnect or start a new Codex session if the tools do not appear. Example prompt: “Use TypesetLLM to convert report.md into a PDF and save it here.” Codex reads the file, calls the remote tool, and can download the result into its workspace. Rendering happens on TypesetLLM's server.

## Claude Code

```sh
claude mcp add --transport http typesetllm https://typesetllm.onrender.com/mcp
claude mcp list
```

This syntax follows [Claude Code's official remote HTTP MCP documentation](https://code.claude.com/docs/en/mcp#option-1-add-a-remote-http-server).

## Tools

- `convert_markdown_to_pdf(markdown_text, filename?)` returns a structured HTTPS download URL, safe filename, expiration timestamp, warnings, and a download instruction. It does not return a server path or PDF base64.
- `typesetllm_status()` returns renderer readiness.

The web app, REST endpoint and MCP tool share a per-process conversion semaphore and per-client rate limit. Defaults: 1 MB of Markdown, 45 seconds rendering, one concurrent conversion, 60 conversions per hour per client. `MAX_REQUEST_BYTES`, `CONVERSION_TIMEOUT_SECONDS`, `MAX_CONCURRENT_CONVERSIONS`, and `CONVERSION_RATE_LIMIT_PER_HOUR` configure these limits.

`TYPESETLLM_PUBLIC_BASE_URL` must be the deployment's HTTPS origin and controls download URLs (default `https://typesetllm.onrender.com`). `TYPESETLLM_DOWNLOAD_RETENTION_SECONDS` controls expiration (default `900`). `TYPESETLLM_ALLOWED_HOSTS` can add comma-separated public hostnames when a reverse proxy uses another Host header. PDF downloads use unguessable tokens and return 404 when invalid or expired.

Downloads live in temporary local storage. They disappear on restart, and tokens only work on the instance that rendered the PDF. Multiple instances require shared PDF storage, shared token metadata, and coordinated concurrency and rate limits.

## Optional local adapter

The existing `server.py` stdio adapter still calls the hosted `/convert` endpoint and writes the response to local disk. It is only needed if you prefer a local MCP process.

```sh
cd mcp
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
codex mcp add typesetllm-local -- python /absolute/path/to/mcp/server.py
```

Its optional environment variables are `TYPESETLLM_URL`, `TYPESETLLM_OUTDIR`, `TYPESETLLM_TIMEOUT`, and `TYPESETLLM_MAX_BYTES`.
