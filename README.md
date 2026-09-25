# TypesetLLM*

Render Markdown to PDF with Pandoc + XeLaTeX. *(For MacOS & Linus)

## Setup

Requires `pandoc` and `xelatex`.
Note: Deactivate any active conda environments before starting up.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python run_local.py
```

## Convert a file

```bash
python -m src.cli path/to/file.md -o path/to/file.pdf
./convert.sh path/to/file.md
```

The converter uses the bundled template, Lua filter, and bundled fonts directly.

## Run the API

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

If the `uvicorn` CLI is slow to start on your machine, use:

```bash
python run_local.py
```

Open `http://localhost:8000` for the local web app.

POST Markdown text to `/convert` and it returns a PDF.

## Deploy on Render

This repository includes a Dockerfile with Pandoc, XeLaTeX, the web UI, and all
bundled assets. To deploy it:

1. Create a Render **Web Service** from this GitHub repository.
2. Select the Docker runtime (the root `Dockerfile` is detected automatically).
3. Set the health check path to `/health`.
4. Start with one instance. A 1 CPU / 2 GB instance is recommended for
   production PDF conversion; the free instance is suitable for evaluation.
5. Deploy and open the generated service URL.

No persistent disk or database is required. Input and output files are temporary
and are deleted after each response.

### Runtime settings

The following optional environment variables are supported:

| Variable | Default | Purpose |
| --- | ---: | --- |
| `PORT` | `8000` | Listening port; hosting platforms normally set this. |
| `MAX_REQUEST_BYTES` | `1048576` | Maximum Markdown request size in bytes. |
| `MAX_CONCURRENT_CONVERSIONS` | `1` | Maximum simultaneous Pandoc/XeLaTeX jobs per instance. |
| `ALLOW_RAW_TEX` | `false` | Enables raw TeX input. Leave disabled for a public service. |

Verify a deployment with:

```bash
curl https://YOUR-SERVICE.example/health
curl -X POST https://YOUR-SERVICE.example/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown_text":"# Hello from the web"}' \
  --output test.pdf
```
