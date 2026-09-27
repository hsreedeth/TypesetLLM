"""Safe names for PDFs returned by the web API and MCP."""

import re
import yaml


def output_filename(markdown: str, requested: str | None = None) -> str:
    title = requested
    if not title:
        match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", markdown, re.DOTALL)
        if match:
            try:
                metadata = yaml.safe_load(match.group(1))
                if isinstance(metadata, dict) and isinstance(metadata.get("title"), str):
                    title = metadata["title"]
            except yaml.YAMLError:
                pass
    if not title:
        heading = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        title = heading.group(1) if heading else "converted_document"
    title = re.sub(r"\.pdf$", "", title, flags=re.IGNORECASE)
    slug = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")[:64]
    return f"{slug or 'converted_document'}.pdf"
