"""Bounded local rerun of every supplied audit fixture."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.cli import ConversionError, DEFAULT_TEMPLATE, WEB_MARKDOWN_FORMAT, convert_with_diagnostics

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "audit"
OUTPUT = ROOT / "evidence" / "audit"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for source in sorted(FIXTURES.glob("*.md")):
        pdf = OUTPUT / f"{source.stem}-current.pdf"
        item: dict = {"case": source.stem}
        try:
            result = convert_with_diagnostics(source, pdf, WEB_MARKDOWN_FORMAT, DEFAULT_TEMPLATE)
            document = fitz.open(pdf)
            text = "\n".join(page.get_text() for page in document)
            sentinels = re.findall(r"END_[A-Z_0-9]+", source.read_text(encoding="utf-8"))
            item.update(
                status="compiled",
                pages=len(document),
                missing_sentinels=[value for value in sentinels if value not in text],
                warnings=list(result.warnings),
            )
        except ConversionError as exc:
            item.update(status="input_error" if exc.input_error else "renderer_error", error=str(exc))
        rows.append(item)
        print(f"{item['case']}: {item['status']}", flush=True)
    (OUTPUT / "current-all-results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
