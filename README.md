# TypesetLLM

Render Markdown to PDF with Pandoc + XeLaTeX.

## Setup

Requires `pandoc` and `xelatex`.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
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

POST Markdown text to `/convert` and it returns a PDF.
