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
