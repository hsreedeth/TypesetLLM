"""A render deadline must terminate Pandoc's child processes too."""

import os
from pathlib import Path
import sys
import time

import pytest

from src import cli


@pytest.mark.skipif(not hasattr(os, "killpg"), reason="requires POSIX process groups")
def test_timeout_kills_renderer_children(tmp_path: Path, monkeypatch):
    spawned = tmp_path / "spawned"
    survived = tmp_path / "survived"
    fake_pandoc = tmp_path / "pandoc"
    child_code = f"import time; from pathlib import Path; time.sleep(2); Path({str(survived)!r}).write_text('alive')"
    fake_pandoc.write_text(
        f"#!{sys.executable}\n"
        "import subprocess, sys, time\n"
        f"subprocess.Popen([sys.executable, '-c', {child_code!r}])\n"
        f"open({str(spawned)!r}, 'w').close()\n"
        "time.sleep(20)\n"
    )
    fake_pandoc.chmod(0o755)
    source = tmp_path / "input.md"
    source.write_text("# Timeout")
    monkeypatch.setattr(cli.pypandoc, "get_pandoc_path", lambda: str(fake_pandoc))
    monkeypatch.setattr(cli, "CONVERSION_TIMEOUT_SECONDS", 1)

    with pytest.raises(cli.ConversionError, match="timed out"):
        cli.convert_with_diagnostics(source, tmp_path / "output.pdf", cli.WEB_MARKDOWN_FORMAT, cli.DEFAULT_TEMPLATE)
    assert spawned.exists(), "the fake renderer did not spawn a child"
    time.sleep(2.2)
    assert not survived.exists(), "a renderer child survived the timeout"
