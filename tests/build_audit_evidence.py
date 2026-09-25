"""Generate reviewable before/after PDFs and page previews from audit fixtures."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.cli import DEFAULT_TEMPLATE, WEB_MARKDOWN_FORMAT, convert_with_diagnostics


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "audit"
ORIGINAL = Path("/private/tmp/typesetllm-audit/local-results")
OUTPUT = ROOT / "evidence" / "audit"
CASES = ("02_small_table", "03_wide_table", "05_math_brackets", "06_unicode", "07_long_code", "08_multipage_table", "13_metadata", "16_realistic_report")


def inspect(pdf: Path, stem: str) -> dict:
    document = fitz.open(pdf)
    text = "\n".join(page.get_text() for page in document)
    for index, page in enumerate(document):
        if index < 3:
            image = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            image.save(OUTPUT / f"{stem}-page-{index + 1}.png")
    return {
        "pages": len(document),
        "page_sizes": [[round(page.rect.width), round(page.rect.height)] for page in document],
        "text": text,
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    findings = {}
    for name in CASES:
        before = OUTPUT / f"{name}-before.pdf"
        after = OUTPUT / f"{name}-after.pdf"
        if (ORIGINAL / f"{name}.pdf").exists():
            shutil.copyfile(ORIGINAL / f"{name}.pdf", before)
            previous = inspect(before, f"{name}-before")
        else:
            previous = None
        result = convert_with_diagnostics(FIXTURES / f"{name}.md", after, WEB_MARKDOWN_FORMAT, DEFAULT_TEMPLATE)
        current = inspect(after, f"{name}-after")
        findings[name] = {
            "before": {"pages": previous["pages"], "page_sizes": previous["page_sizes"]} if previous else None,
            "after": {"pages": current["pages"], "page_sizes": current["page_sizes"]},
            "warnings": list(result.warnings),
        }
    (OUTPUT / "findings.json").write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(json.dumps(findings, indent=2))


if __name__ == "__main__":
    main()
