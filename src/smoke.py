"""A representative renderer smoke test used by Docker and API readiness."""

from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from src.cli import DEFAULT_TEMPLATE, WEB_MARKDOWN_FORMAT, convert_with_diagnostics


SMOKE_MARKDOWN = """---
title: "Renderer readiness"
author: "TypesetLLM"
date: "2026-09-25"
---

Text with a scientific value of 10⁻³ and inline math \\(x=2\\).

| Group | Estimate |
|---|---:|
| A | 1.43 |

```python
result = "renderer-ready"
```
"""


def _version(command: str) -> str:
    try:
        completed = subprocess.run(
            [command, "--version"], capture_output=True, text=True, timeout=5, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    return (completed.stdout or completed.stderr).splitlines()[0] if completed.returncode == 0 else "unavailable"


def run_smoke_check() -> dict[str, Any]:
    with TemporaryDirectory(prefix="typesetllm-ready-") as directory:
        root = Path(directory)
        source = root / "readiness.md"
        output = root / "readiness.pdf"
        source.write_text(SMOKE_MARKDOWN, encoding="utf-8")
        result = convert_with_diagnostics(source, output, WEB_MARKDOWN_FORMAT, DEFAULT_TEMPLATE)
        if not output.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError("Renderer smoke test did not produce a PDF.")
        return {
            "status": "ready",
            "pandoc": _version("pandoc"),
            "xelatex": _version("xelatex"),
            "warnings": list(result.warnings),
        }


if __name__ == "__main__":
    run_smoke_check()
