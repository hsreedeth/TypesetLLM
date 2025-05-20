# Publication Ready PDF Renderer for Large Language Models

One-click, vintage-style PDFs from any ChatGPT notes — directly in your browser.

## Problem

ChatGPT is great for taking notes, but turning those into beautiful, readable PDFs is a hassle. This tool lets you paste or upload Markdown, click “Render,” and instantly get a vintage-styled PDF — no server, no fuss.

## MVP Features

- ✅ Paste or upload Markdown
- ✅ One-click “Render” to PDF
- ✅ Vintage stylesheet applied automatically
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
