"""Render the fictional applications and verify PDF content, fonts, links and previews.

Run from the repository root after installing requirements-rolepilot-review.txt.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import unicodedata

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = Path(__file__).resolve().parent
PREVIEWS = EXAMPLES / "previews"
DOCUMENTS = {
    "health-data-resume": ("rolepilot-resume", 2),
    "cover-letter": ("rolepilot-letter", 1),
    "selection-criteria": ("rolepilot-criteria", 2),
    "overflow-resume": ("rolepilot-resume", 2),
    "overflow-letter": ("rolepilot-letter", 2),
    "overflow-criteria": ("rolepilot-criteria", 2),
}


def normalized(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKD", text).casefold() if char.isalnum())


def main() -> None:
    PREVIEWS.mkdir(exist_ok=True)
    for stale in PREVIEWS.glob("*-p*.png"):
        stale.unlink()
    for stem, (theme, expected_pages) in DOCUMENTS.items():
        source = EXAMPLES / f"{stem}.md"
        pdf = EXAMPLES / f"{stem}.pdf"
        subprocess.run([sys.executable, "-m", "src.cli", str(source), "--theme", theme, "-o", str(pdf)],
                       cwd=ROOT, check=True, capture_output=True, text=True, timeout=90)
        data = pdf.read_bytes()
        assert data.startswith(b"%PDF-") and data.rstrip().endswith(b"%%EOF"), stem
        document = pymupdf.open(pdf)
        assert len(document) == expected_pages, (stem, len(document))
        expected_text = subprocess.check_output(["pandoc", "-f", "markdown", "-t", "plain", "--wrap=none", str(source)], text=True)
        extracted = "\n".join(page.get_text() for page in document)
        assert normalized(expected_text) == normalized(extracted), f"Missing or reordered text in {stem}"
        assert not re.search(r"typesetllm|rolepilot", extracted, re.IGNORECASE), stem
        fonts = {font[0]: font[3] for page in document for font in page.get_fonts()}
        assert fonts and all("SourceSans3" in name for name in fonts.values()), (stem, fonts)
        assert all(len(document.extract_font(xref)[3]) > 0 for xref in fonts), stem
        links = [link.get("uri", "") for page in document for link in page.get_links()]
        assert any(link.startswith("mailto:") for link in links), stem
        expected_links = re.findall(r"\]\(([^)\s]+)\)", source.read_text(encoding="utf-8"))
        assert all(target in links for target in expected_links), (stem, "missing clickable link")
        for page_number, page in enumerate(document, 1):
            assert abs(page.rect.width - 595.28) < 1 and abs(page.rect.height - 841.89) < 1, stem
            spans = [span for block in page.get_text("dict")["blocks"] if "lines" in block
                     for line in block["lines"] for span in line["spans"]]
            assert spans and min(span["size"] for span in spans) >= 10.0, (stem, page_number)
            assert all(38 < span["bbox"][0] and span["bbox"][2] < page.rect.width - 38
                       and 35 < span["bbox"][1] and span["bbox"][3] < page.rect.height - 35
                       for span in spans), (stem, page_number, "text outside page margins")
            page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).save(PREVIEWS / f"{stem}-p{page_number}.png")
        print(f"{stem}: {len(document)} pages; text, links, embedded Source Sans 3 and margins verified")


if __name__ == "__main__":
    main()
