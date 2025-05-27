**Roadmap — “Vintage-PDF-from-ChatGPT”**

> **Goal** Launch a zero-cost public MVP that turns pasted Markdown/ plain-text into a PDF with a 1950-era layout.
> Constraints: no user accounts, no database, run on free hosting.

---

## Phase 0  Project framing  (½ day)

| Task                                                                                      | Deliverable                                               |
| ----------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Choose a repo name & OSS licence (MIT).                                                   | `README.md` skeleton with problem statement & tech stack. |
| Collect fonts (e.g., *IBM Plex Serif* + *Fira Code*) and verify licences allow embedding. | `assets/fonts/`                                           |

---

## Phase 1  Local proof of concept  (1 day)

1. **Set up Python 3.11 virtual-env**
   `pip install fastapi uvicorn pypandoc`
2. **Install TinyTeX** (`install-tinytex --no-path`) — a 100–150 MB LaTeX distro suitable for XeLaTeX ([yihui.org][1])
3. **Vintage template** → `templates/vintage.tex` (page geometry, fonts, running headers).
4. **CLI script** replicating your snippet, plus unit tests (`pytest`).

Deliverable: `make demo` converts sample note to `out/sample.pdf`.

---

## Phase 2  API service  (1 day)

| Step             | Detail                                                                                        |
| ---------------- | --------------------------------------------------------------------------------------------- |
| FastAPI endpoint | `POST /convert` accepts JSON `{text: "...", theme: "vintage"}` and streams `application/pdf`. |
| Input limits     | `len(text) ≤ 10 000` chars, reject otherwise (422).                                           |
| Security         | Strip dangerous LaTeX with regex (`\\write18`, `\\input`, etc.).                              |
| Rate limiter     | `slowapi` middleware (60 req/h per IP).                                                       |
| Unit tests       | Happy path, large-input rejection, LaTeX injection.                                           |

---

## Phase 3  Containerisation  (½ day)

* **Dockerfile** (≈ 300 MB):
  `FROM python:3.11-slim` → install pandoc binary + TinyTeX minimal profile.
  Build-arg `TL_PACKAGES="fontspec microtype geometry"` keeps size down (the naive TinyTeX image is \~750 MB ([Docker Hub][2])).

* **Make targets**

  * `make build` (Docker)
  * `make dev` (uvicorn hot-reload)

---

## Phase 4  Deploy API  (½–1 day)

1. **Render.com** (or Fly/Railway) free web service. Render gives **750 instance-hours/month** and idles after 15 min ([Render][3]).
2. Add environment `PORT` & health-check route.
3. Push; verify cold-start < 10 s. (Hack: GitHub Action `curl` every 10 min to keep warm if desired.)

---

## Phase 5  Static front-end (GitHub Pages)  (1 day)

| Component    | Detail                                                                                        |
| ------------ | --------------------------------------------------------------------------------------------- |
| HTML         | `index.html` with `<textarea id="src">` and two buttons (“Preview HTML”, “Download PDF”).     |
| JS fetch     | `fetch("https://your-api.onrender.com/convert",{method:"POST",...})` and download Blob.       |
| Live preview | Use `pandoc-wasm` for HTML only (PDF unsupported; GitHub issue #11 still open) ([GitHub][4]). |
| Styling      | Single CSS file; sepia background + monospace headings for vintage vibe.                      |

---

## Phase 6  Release & feedback  (½ day)

* Write launch post + demo GIF (README badge).
* Ask classmates to file issues; capture at least 5 bug reports before “v1.0”.

---

## Phase 7  Monitoring & hardening  (½ day)

| Tool                 | Purpose                         |
| -------------------- | ------------------------------- |
| Render logs + alerts | Watch 5XX errors/signup spikes. |
| GitHub Dependabot    | Auto-PR dependency bumps.       |
| Sentry (free tier)   | Capture uncaught exceptions.    |

---

## Phase 8  Stretch goals  (1–2 weeks, optional)

| Feature                                                                                                   | Rationale                                                                            |
| --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Theme gallery via query param (`?theme=pulp`).                                                            | Adds variety with minimal backend change (just swap `.tex`).                         |
| User drag-and-drop images → embed.                                                                        | Requires `multipart/form-data` parsing + Pandoc media bag.                           |
| Temporary S3/Backblaze bucket (+ pre-signed URL).                                                         | Lets users share PDFs for 24 h without email attachments; still stateless long-term. |
| Move to **browser-only** converter when `pandoc-wasm` gains full PDF/Typst support (watch the GH ticket). |                                                                                      |

---

### Indicative timeline (≈ 32 hours)

| Week  | Mon     | Tue     | Wed     | Thu     | Fri         |
| ----- | ------- | ------- | ------- | ------- | ----------- |
| **1** | Phase 0 | Phase 1 | Phase 1 | Phase 2 | Phase 2     |
| **2** | Phase 3 | Phase 4 | Phase 5 | Phase 5 | Phase 6 & 7 |

---

### Final checklist

* [ ] Local script produces vintage PDF identical to your prototype.
* [ ] `/convert` capped at 10 k chars & 10 MB output.
* [ ] Docker image < 350 MB compressed.
* [ ] Render deploy green, CORS OK.
* [ ] GitHub Pages site loads and downloads PDF on first try.
* [ ] README shows one-click deploy & licence.

Follow this roadmap and you can demo a polished, cost-free MVP within **two working weeks**—future-proofed for heavier traffic or a full browser-side rewrite. Good luck, and enjoy the retro typesetting!

[1]: https://yihui.org/tinytex/?utm_source=chatgpt.com "TinyTeX - Yihui Xie - 谢益辉"
[2]: https://hub.docker.com/layers/muzili/tinytex/latest/images/sha256-26c0d4e2b5e029d8135f448cc01640415645da3f187492a76ccd9f77dbd4e0a4?utm_source=chatgpt.com "Image Layer Details - muzili/tinytex:latest - Docker Hub"
[3]: https://render.com/docs/free?utm_source=chatgpt.com "Deploy for Free – Render Docs"
[4]: https://github.com/tweag/pandoc-wasm/issues?utm_source=chatgpt.com "Issues · tweag/pandoc-wasm - GitHub"
