# tests/test_cli.py

import sys
from pathlib import Path

# add the project root (one level up) to sys.path so `import src` works
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess
import sys as _sys
import pytest

CLI_MODULE = "src.cli"


def run_cli(args, **kwargs):
    cmd = [sys.executable, "-m", CLI_MODULE, *args]
    return subprocess.run(cmd, **kwargs)


def test_help_flag_shows_usage():
    result = run_cli(["--help"],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     text=True)
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_missing_source_aborts(tmp_path):
    missing = tmp_path / "nope.md"
    result = run_cli([str(missing)],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     text=True)
    assert result.returncode != 0
    # stderr >>> stdout. any day.
    assert "does not exist" in result.stderr.lower()


@pytest.mark.parametrize("content", ["# Hi", "Hello **World**"])
def test_convert_creates_pdf(tmp_path, content):
    md = tmp_path / "demo.md"
    md.write_text(content, encoding="utf-8")
    pdf = tmp_path / "demo.pdf"

    result = run_cli([str(md), "-o", str(pdf)],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     text=True)

    assert result.returncode == 0, f"stderr={result.stderr}"
    assert pdf.exists(), "PDF file was not created"
    # lower threshold  accommodate ~9 KB pds
    assert pdf.stat().st_size > 5_000, f"PDF too small ({pdf.stat().st_size} bytes)"


def test_convert_direct_call(tmp_path):
    from src.cli import convert

    md = tmp_path / "direct.md"
    md.write_text("Direct call test", encoding="utf-8")
    pdf = tmp_path / "direct.pdf"
    convert(md, pdf)

    assert pdf.exists(), "Direct convert didn’t make a PDF"
    assert pdf.stat().st_size > 5_000
