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
3. Set the health check path to `/ready`. `/health` is process liveness only.
4. Start with one instance. A 1 CPU / 2 GB instance is recommended for
   production PDF conversion; the free instance is suitable for evaluation.
5. Deploy and open the generated service URL.

No persistent disk or database is required. Input and output files are temporary
and are deleted after each response.

The Docker build compiles a representative Markdown report containing text,
a table, math, code and scientific superscripts. Startup repeats this check.
`/ready` returns 503 until the renderer passes it; `/health` returns the
independent process status. A conversion error includes a reference code that
can be matched with server logs.

The UI accepts pasted Markdown or an uploaded `.md` file, shows an in-page PDF
preview, and downloads with a filename based on the document title or heading.
Changing the source cancels a pending conversion and disables the old download.
On each page load, a four-slide branding introduction opens over the dimmed,
blurred app. It advances automatically, supports swipe, arrows and keyboard
navigation, and can be closed with the × button or Escape. The fourth slide is
a prerendered Remotion video; see `branding-video/README.md` to regenerate it.
Successful PDF responses include any quality notices in the
`X-Typeset-Warnings` header. The public API retains JSON, form and raw body
input modes and returns a PDF body on success.

Mermaid diagrams and unresolved citation keys remain unsupported and are
reported as warnings. Missing images and unsupported glyphs are reported,
never silently replaced without a notice. The web endpoint has raw TeX disabled
by default; the local CLI still permits it for trusted input. This service is
not an isolation boundary for untrusted TeX when `ALLOW_RAW_TEX=true`.

### Runtime settings

The following optional environment variables are supported:

| Variable | Default | Purpose |
| --- | ---: | --- |
| `PORT` | `8000` | Listening port; hosting platforms normally set this. |
| `MAX_REQUEST_BYTES` | `1048576` | Maximum Markdown request size in bytes. |
| `MAX_CONCURRENT_CONVERSIONS` | `1` | Maximum simultaneous Pandoc/XeLaTeX jobs per instance. |
| `ALLOW_RAW_TEX` | `false` | Enables raw TeX input. Leave disabled for a public service. |
| `CONVERSION_TIMEOUT_SECONDS` | `45` | Maximum Pandoc/XeLaTeX runtime per request. |

Verify a deployment with:

```bash
curl https://YOUR-SERVICE.example/health
curl https://YOUR-SERVICE.example/ready
curl -X POST https://YOUR-SERVICE.example/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown_text":"# Hello from the web"}' \
  --output test.pdf
```

Audit fixtures and reviewable before/after PDFs are in
[`evidence/audit/`](evidence/audit/README.md). To run the visual regression
checks, install `PyMuPDF` in a development environment and run
`python -m pytest tests/test_audit_regressions.py`.
