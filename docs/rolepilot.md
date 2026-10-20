# RolePilot application documents

TypesetLLM only renders reviewed Markdown. It does not call a language model, rewrite text, add facts, or set an answer-length limit. The three A4, single-column themes are `rolepilot-resume`, `rolepilot-letter`, and `rolepilot-criteria`, each at template version `1.0.0`. They are designed for straightforward parsing; no universal ATS compatibility or ATS score is claimed.

## Input contract, version 1

Use standard Markdown with this YAML front matter:

```yaml
---
rolepilot_contract: 1
target_role: Senior Health Data Analyst       # optional, tracking only
target_employer: North Coast Health Network   # optional, tracking only
---
```

Only these three YAML keys are accepted. Unknown keys, malformed YAML, and other contract versions fail explicitly. Metadata is never printed in the PDF. Keep evidence IDs, review comments, internal provenance, and other private application data outside the Markdown; if placed in YAML they are rejected. **Everything in the Markdown body is visible** and is rendered in source order. The renderer never silently removes or shortens it.

| Field | Put it in | Convention |
| --- | --- | --- |
| Candidate name | Body | One first-level heading, `# Avery Chen`, at the start. Do not repeat it in metadata. |
| Contact details and links | Body | Ordinary paragraph below the name. Use Markdown links, including `mailto:` and `tel:` where helpful. |
| Target role and employer | YAML for tracking; body if visible | Optional metadata values do not print. Include the role/employer in a resume role line or letter subject when the reader should see them. |
| Resume sections | Body | `## Profile`, `## Experience`, `## Skills`, etc. Use `### Role · Employer · Dates` for each experience entry, followed by paragraphs or bullets. |
| Letter fields | Body | Date, recipient, **Re: subject**, salutation, paragraphs, and sign-off in reading order. A repeated name in the sign-off is intentional. |
| Criteria | Body | `## Selection criteria`, then each question as a numbered `### 1. ...` heading followed by its answer. Do not put answers in YAML. |

The visible body is trusted reviewed application copy. Do not include raw LaTeX or layout instructions; hosted requests disable raw TeX. Pandoc handles escaping of ordinary characters, links, currency, underscores, and ampersands. Images, sidebars, skill bars, and layout tables are outside this contract. Long entries and answers flow across pages; the renderer does not enforce a page count. Changing template styling or re-rendering a document does not require regenerating its Markdown content.

## Render locally

From the repository root, with Pandoc and XeLaTeX installed:

```sh
python -m src.cli examples/rolepilot/health-data-resume.md --theme rolepilot-resume -o resume.pdf
python -m src.cli examples/rolepilot/cover-letter.md --theme rolepilot-letter -o letter.pdf
python -m src.cli examples/rolepilot/selection-criteria.md --theme rolepilot-criteria -o criteria.pdf
python -m src.cli --list-themes
```

`--template /path/to/custom.tex` still works for local custom templates. Omit `--theme` to retain the vintage layout. The built-in `--theme` and custom `--template` options cannot be combined.

## REST and MCP

The REST endpoint returns PDF bytes. The theme defaults to `vintage`; unknown themes return a structured error. Theme and version are also returned in `X-Typeset-Theme` and `X-Typeset-Theme-Version` response headers.

```sh
python - <<'PYCODE' > /tmp/rolepilot-request.json
import json
from pathlib import Path
print(json.dumps({
    "markdown_text": Path("examples/rolepilot/health-data-resume.md").read_text(),
    "theme": "rolepilot-resume",
}))
PYCODE
curl -X POST https://typesetllm.onrender.com/convert \
  -H 'Content-Type: application/json' \
  --data-binary @/tmp/rolepilot-request.json \
  -o resume.pdf
```

Hosted MCP tool arguments:

```json
{"markdown_text":"---\nrolepilot_contract: 1\n---\n\n# Avery Chen\n\n[avery.chen@example.org](mailto:avery.chen@example.org)\n\n## Profile\n\nHealth data analyst.","filename":"avery-chen-resume.pdf","theme":"rolepilot-resume"}
```

The hosted `convert_markdown_to_pdf` tool accepts optional `theme` and `filename` arguments and returns a temporary HTTPS download URL, filename, expiry, warnings, theme, and template version. The optional local stdio adapter accepts the same `theme` argument, calls REST, and keeps the downloaded PDF in its configured output directory. `typesetllm_status` and `GET /ready` list supported themes and versions.

## RolePilot integration note

Record the selected theme and returned template version in RolePilot's application metadata, not inside the applicant-facing body. Check rendering warnings and review the PDF before delivery. Hosted download links expire after 900 seconds by default and may disappear on server restart; download the PDF into RolePilot's own storage promptly. The local adapter's file remains until the local owner deletes it. Both paths preserve reviewed content; retain the original Markdown for later re-rendering. No RolePilot repository changes are needed here.

## Examples and fonts

The committed [examples](../examples/rolepilot/) use fictional applicants. Each Markdown file has a PDF and one PNG preview per page. `overflow-*` examples exercise long names, links, entries, and page continuation. The PDFs use bundled static Source Sans 3 files; see [font provenance](../fonts/SOURCE_SANS_3.md) and the bundled licence. The fallback is the repository's bundled Inter sans-serif if a Source Sans file is unavailable.
