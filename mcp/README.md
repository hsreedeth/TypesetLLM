# typesetllm-mcp

A minimal MCP server that wraps the [TypesetLLM](https://github.com/hsreedeth/TypesetLLM)
`/convert` endpoint, so any MCP client can turn Markdown into a typeset PDF
as a tool call.

It talks to your deployed instance (default: `https://typesetllm.onrender.com`)
over plain HTTP — no changes to TypesetLLM itself are needed.

## Install

```bash
cd typesetllm-mcp
python -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run it directly (sanity check)

```bash
python server.py
```

It will sit waiting on stdio — that's expected, it's meant to be launched
by an MCP client, not run standalone.

## Add to Claude Code

```bash
claude mcp add typesetllm -- python /absolute/path/to/typesetllm-mcp/server.py
```

## Add to Claude Desktop

Edit your `claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "typesetllm": {
      "command": "python",
      "args": ["/absolute/path/to/typesetllm-mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop afterward.

## Configuration (optional environment variables)

| Variable             | Default                            | Purpose                                   |
| --------------------- | ----------------------------------- | ------------------------------------------ |
| `TYPESETLLM_URL`      | `https://typesetllm.onrender.com`   | Which deployment to call                   |
| `TYPESETLLM_OUTDIR`   | `~/typesetllm-output`               | Where PDFs get saved locally               |
| `TYPESETLLM_TIMEOUT`  | `90`                                | Client-side request timeout (seconds)      |
| `TYPESETLLM_MAX_BYTES`| `1048576`                           | Local pre-check, mirrors the service cap   |

Set these in the `env` block of the client config if you need to point at a
different deployment, e.g.:

```json
{
  "mcpServers": {
    "typesetllm": {
      "command": "python",
      "args": ["/absolute/path/to/typesetllm-mcp/server.py"],
      "env": { "TYPESETLLM_URL": "https://your-instance.example" }
    }
  }
}
```

## Tools exposed

- **convert_markdown_to_pdf(markdown_text, filename?)** — renders Markdown
  to PDF via the service and saves it to `TYPESETLLM_OUTDIR`, returning the
  path and any renderer quality warnings (e.g. unsupported Mermaid blocks or
  citation keys).
- **typesetllm_status()** — pings `/ready` on the deployment, useful since
  the Render free tier cold-starts after idling.

## Notes

- The public `/convert` endpoint runs with raw TeX disabled
  (`ALLOW_RAW_TEX=false`), same as the hosted service.
- Requests over ~1MB or that take longer than the service's 45s conversion
  timeout will fail server-side; this wrapper surfaces those as readable
  error messages instead of a raw HTTP error.
