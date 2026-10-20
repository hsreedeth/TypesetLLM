"""RolePilot contract, CLI and local adapter checks."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import subprocess
import sys

import pytest

from src.themes import get_theme, theme_catalog, validate_rolepilot_markdown

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples" / "rolepilot"


def test_contract_and_theme_registry():
    assert theme_catalog()["rolepilot-resume"] == {"version": "1.0.0", "contract_version": 1}
    with pytest.raises(ValueError, match="Unknown theme"):
        get_theme("../vintage")
    with pytest.raises(ValueError, match="Unsupported RolePilot metadata"):
        validate_rolepilot_markdown("---\nrolepilot_contract: 1\nreview_comment: private\n---\n\n# Avery", get_theme("rolepilot-resume"))
    with pytest.raises(ValueError, match="contract version"):
        validate_rolepilot_markdown("---\nrolepilot_contract: 2\n---\n\n# Avery", get_theme("rolepilot-resume"))
    validate_rolepilot_markdown((EXAMPLES / "health-data-resume.md").read_text(), get_theme("rolepilot-resume"))


@pytest.mark.parametrize("source,theme", [
    ("health-data-resume.md", "rolepilot-resume"),
    ("cover-letter.md", "rolepilot-letter"),
    ("selection-criteria.md", "rolepilot-criteria"),
])
def test_cli_renders_rolepilot_examples(tmp_path, source, theme):
    output = tmp_path / "application.pdf"
    proc = subprocess.run([sys.executable, "-m", "src.cli", str(EXAMPLES / source),
                           "--theme", theme, "-o", str(output)], cwd=ROOT,
                          capture_output=True, text=True, timeout=90)
    assert proc.returncode == 0, proc.stderr
    assert output.read_bytes().startswith(b"%PDF-")


def test_local_adapter_passes_theme_and_keeps_file(monkeypatch, tmp_path):
    spec = spec_from_file_location("typesetllm_local_adapter", ROOT / "mcp" / "server.py")
    adapter = module_from_spec(spec)
    spec.loader.exec_module(adapter)
    sent = {}
    class Response:
        status_code = 200
        content = b"%PDF-1.7\nexample\n%%EOF"
        headers = {"X-Typeset-Theme-Version": "1.0.0"}
    def post(url, *, json, timeout):
        sent.update(json)
        return Response()
    monkeypatch.setattr(adapter.httpx, "post", post)
    monkeypatch.setattr(adapter, "OUTDIR", tmp_path)
    message = adapter.convert_markdown_to_pdf("# Avery", theme="rolepilot-resume")
    assert sent["theme"] == "rolepilot-resume"
    assert "rolepilot-resume v1.0.0" in message
    assert (tmp_path / "avery.pdf").is_file()
