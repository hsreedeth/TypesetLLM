![TypesetLLM](assets/typesetllm-header.png)

# TypesetLLM

Turns Markdown into a decent PDF. Uses Pandoc and XeLaTeX.

There is a command-line tool, a small web interface, and an HTTP API.

## Requirements

- Python 3.11+
- Pandoc
- XeLaTeX

Docker includes everything.

## Install

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
python run_local.py
```

Open <http://localhost:8000>.

## Convert a file

```sh
./convert.sh document.md document.pdf
```

Or:

```sh
python -m src.cli document.md -o document.pdf
```

## HTTP API

```sh
curl -X POST http://localhost:8000/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown_text":"# Hello"}' \
  --output hello.pdf
```

Useful endpoints:

- `POST /convert` — make a PDF
- `GET /health` — process check
- `GET /ready` — renderer check

Raw TeX is disabled on the web service. The local command-line tool accepts it for trusted files.

## Docker

```sh
docker build -t typesetllm .
docker run --rm -p 8000:8000 typesetllm
```

The included `render.yaml` can be used to deploy the same image on Render.

## MCP

The MCP server lets Claude Code, Codex CLI, and other MCP clients call the hosted converter.

See [mcp/README.md](mcp/README.md).

## Tests

```sh
python -m pytest -q
```

## Notes

- Maximum web request size: 1 MB by default.
- Conversions time out after 45 seconds by default.
- Mermaid diagrams are not rendered.
- Files created by the web API are temporary.

MIT License.
