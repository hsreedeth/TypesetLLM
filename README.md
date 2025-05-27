# GPT2PDF (a.k.a. MD2PDF)

**Convert Markdown (e.g. ChatGPT notes) into publication-quality PDFs**  
via a simple CLI or HTTP API, powered by Pandoc + XeLaTeX and packaged in Docker.

---

## Alpha Build v1.0 (MVP)

1. **`md2pdf` CLI**  
   - `md2pdf input.md -o output.pdf --markdown-format gfm`  
   - Offline, reproducible Pandoc → XeLaTeX pipeline  
   - Custom vintage template + Lua filters for tables, multi-column layouts, fonts

2. **FastAPI HTTP Service**  
   - `POST /convert` accepts JSON `{ text, theme, markdown_format }` → returns PDF  
   - Rate-limited (60 reqs/hr/IP) with built-in `/health` endpoint for smoke tests  
   - Safe: strips dangerous LaTeX commands (e.g. `\input`, `\write18`)

3. **Containerisation**  
   - **Two-stage Docker build**  
     - Stage 1: install TinyTeX (“small” scheme) + exactly the LaTeX packages you need  
     - Stage 2: copy only the PDF runtime (TinyTeX + Pandoc + Python deps) → ~300 MB image  
   - Makefile shortcuts: `make build`, `make dev`, `make demo`  

---

## Tech Stack

- **Core**: Python 3.11, FastAPI, Pydantic, asyncio  
- **PDF Engine**: Pandoc 3.2 + XeLaTeX (TinyTeX “small” profile + Lua filters)  
- **Rate-Limiting**: slowapi (Redis-free, in-process)  
- **Container**: Docker (multi-stage build)  
- **CI/CD**: GitHub Actions (build, test, smoke-test, push to registry)  
- **Deployment**: Render.com / Fly.io / Railway (Docker)

---

## Getting Started

1. **Clone & configure**  
   ```bash
   git clone https://github.com/<you>/GPT2PDF.git
   cd GPT2PDF