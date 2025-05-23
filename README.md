# GPT2PDF: Publication Ready PDF Renderer for Large Language Models

One-click, publication style hand-out PDFs from any ChatGPT notes — directly in your browser.

## Problem

ChatGPT is great for taking notes, but turning those into beautiful, publications style latex rendered PDFs is a hassle. This tool lets you paste or upload Markdown (ideally copied from any language model outputs), click “Render,” and instantly get an academic/publication styled PDF. No server, no fuss.

## MVP Features

The program as it stands now, qualifies as an MVP. It is currently under development and is undergoing iterative improvements. In the meantime, the following features are live and locked down.

- ✅ Paste or upload Markdown
- ✅ One-click “Render” to PDF
- ✅ Classic latex markdown stylesheet applied automatically. The rendering includes beautiful figures and tables. 
- ✅ Entirely client-side (no backend)

## Tech Stack

- **Front-end:** Vanilla JavaScript + [Paged.js](https://pagedjs.org/)
- **PDF engine:** Browser “Print to PDF”
- **Hosting:** GitHub Pages

## Folder Layout


- assets/fonts/      → Vintage-style fonts (+ their licenses)
- src/css/           → Stylesheets including vintage themes
- src/js/            → JavaScript logic for rendering
- index.html         → Entry point for the app
