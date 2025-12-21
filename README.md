<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://i.postimg.cc/X76gBdjB/typeset-LLM.jpg" />
</div>

## **Typeset LLM generated notes/reports (or GitHub flavored markdown (GFM))**

This repo turns Markdown into publication-style PDFs with Pandoc + XeLaTeX. You get a small CLI for quick renders and a FastAPI endpoint for programmatic jobs. Fonts, a template, and a Lua filter ship with the tree so the output looks consistent without hunting for assets.

## What’s here
- `latexit/` — active code: `src/cli.py`, `src/api.py`, template, Lua filter, Dockerfiles, tests, samples, fonts.
- `latexit copy/` — backup snapshot of the same tree.
- Planning artifacts (`coreIdea.txt`, `conceptmap.txt`, `md2pdf.ipynb`, PDF exports) that show the early roadmap (now removed, can be requested over email).

## Prereqs (host)
- Python 3.11
- Pandoc ≥ 3.x on PATH
- XeLaTeX toolchain (TinyTeX works. see `latexit/tlpkgs.txt` for the tested package set) [Note: latexit was the local repo name I used]
- Fontconfig can see the bundled fonts (`assets/fonts/IBM_Plex_Serif_re`, `assets/fonts/Fira_Code`, `assets/fonts/Latin-Modern-Roman`)
- Docker optional if you prefer everything pre-baked

## Quick start (local)
```bash
cd latexit
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Make sure pandoc and xelatex run (install TinyTeX if needed).
# On Linux/macOS, copy fonts and refresh cache:
#   cp assets/fonts/*/*.{ttf,otf} ~/.local/share/fonts && fc-cache -fv
```

## CLI usage
- Basic: `python -m src.cli samples/sample.md -o out/sample.pdf`
- STDIN: `echo '# Title' | python -m src.cli --stdin -o out/stdin.pdf`
- Pick a template: `python -m src.cli note.md -t templates/vintage.tex -o out/note.pdf`
- Wrapper script: `./convert.sh path/to/file.md` → `out/<name>.pdf`

The CLI insists on real files, uses `filters/landscape-6col.lua` for wide tables, and raises clear errors if the source/template/filter is missing.

## FastAPI service
```bash
cd latexit
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```
- `/health` → `{ "status": "ok" }`
- `/convert` accepts JSON, form data, or raw body with `markdown_text` (or `text`) and optional `theme`; returns `application/pdf`.
- Guardrails: 10 kB payload cap, LaTeX sanitiser strips `\\write18`/`\\input`/`openin`/`openout`, SlowAPI rate limit of 60 req/hour/IP.

Example:
```bash
curl -o out/api.pdf \
  -H "Content-Type: application/json" \
  -d '{"markdown_text":"# Hi\n\nConverted by the API","theme":"vintage"}' \
  http://localhost:8000/convert
```

## Docker (self contained)
Includes Pandoc, TinyTeX, fonts.
```bash
cd latexit
docker build -t gptnotes-pdf .
docker run --rm -p 8000:8000 gptnotes-pdf
```
Run the CLI inside the image:
```bash
docker run --rm -v "$PWD/samples":/data gptnotes-pdf \
  python -m src.cli /data/sample.md -o /data/sample.pdf
```

## Tests
```bash
cd latexit
python -m pytest -q
```
The suite exercises both the CLI and API. Pandoc + XeLaTeX must be installed or the PDF assertions will fail.

## Customisation
- Drop new `.tex` templates into `templates/`. pass `-t` (CLI) or `theme=<name>` (API). Unknown themes fall back to `vintage.tex`.
- Edit `filters/landscape-6col.lua` if you want different table widths or to disable the landscape flip.
- `quickscripts/` holds small demo commands. `samples/` contains real Markdown fixtures to tweak.
- `Dockerfile.probe` plus `tlpkgs.txt` capture the minimal TeX packages that successfully compile the template.

## Notes
- Keep inputs under 10 kB to stay within the API limit and avoid long TeX runs.
- If PDFs come out blank, verify font availability and that `xelatex` works from your shell.
- Two trees (`latexit` and `latexit copy`) exist—do your work in `latexit` to match tests and Docker context.

## Samples (Generated)
<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://i.postimg.cc/TwBdkT7T/Screenshot_2025_12_22_at_5_41_28_AM.png" />
</div>
<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://i.postimg.cc/V62f7zGJ/Screenshot_2025_12_22_at_5_40_15_AM.png" />
</div>
<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://i.postimg.cc/mkMbJKJF/Screenshot_2025_12_22_at_5_37_51_AM.png" />
</div>
