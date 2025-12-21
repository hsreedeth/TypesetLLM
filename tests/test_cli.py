"""
Smoke-tests for the md2pdf CLI (src/cli.py)

Run:
    python -m pytest -q
"""

import sys
import subprocess
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# 1) missing source → non-zero exit + helpful stderr
# ---------------------------------------------------------------------------
def test_missing_source_aborts():
    result = subprocess.run(
        [sys.executable, "-m", "src.cli"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    stderr = result.stderr.lower()
    assert "source file" in stderr and "does not exist" in stderr


# ---------------------------------------------------------------------------
# 2) CLI converts Markdown file → valid PDF
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("content", ["# Hi", "Hello **World**"])
def test_cli_converts_file(tmp_path: Path, content: str):
    md = tmp_path / "sample.md"
    md.write_text(content)
    pdf = tmp_path / "sample.pdf"

    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(md), "-o", str(pdf)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"stderr:\n{result.stderr}"
    assert pdf.is_file()
    assert pdf.read_bytes().startswith(b"%PDF-")


# ---------------------------------------------------------------------------
# 3) stdin flag works
# ---------------------------------------------------------------------------
def test_cli_converts_stdin(tmp_path: Path):
    pdf = tmp_path / "stdin.pdf"
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli", "--stdin", "-o", str(pdf)],
        input="# From STDIN\n\n*Bullet*",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert pdf.is_file()
    assert pdf.read_bytes().startswith(b"%PDF-")


# ---------------------------------------------------------------------------
# 4) direct convert() invocation
# ---------------------------------------------------------------------------
def test_convert_direct_call(tmp_path: Path):
    from src.cli import convert

    md = tmp_path / "x.md"
    md.write_text("# Title")
    pdf = tmp_path / "x.pdf"

    tpl = Path("templates") / "vintage.tex"
    assert tpl.is_file(), "templates/vintage.tex missing for tests"

    convert(md, pdf, "gfm", tpl)
    assert pdf.is_file()
    assert pdf.read_bytes().startswith(b"%PDF-")
