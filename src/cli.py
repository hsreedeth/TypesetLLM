#!/usr/bin/env python
"""
md2pdf – Render Markdown to PDF (Pandoc + XeLaTeX)
==================================================
A small helper that powers both the standalone CLI + the FastAPI backend.

Key design points (kept stable so tests & API remain unaffected):
---------------------------------------------------------------
* `convert()` sig stays put so existing imports don't break:

    def convert(src: Path, dst: Path, markdown_format: str, template_path: Path) -> None

* Failures raise FileNotFoundError (tests + API wrapper expect that).
* CLI entry (`python -m src.cli ...`) keeps same flags so smoke tests stay green.
* Missing src msg must contain "source file" + "does not exist" (tests are picky).
* Heavy work is in convert() so API can call it w/out caring about argparse.

Minor improvements in this rewrite
----------------------------------
* Exit codes: 0 ok, 1 user/IO, 2 "uh-oh"
* Logging via --verbose
* Optional --stdin (nice for piping from other tools)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Final

import pypandoc

# bundled stuff lives relative to repo root (keeps docker + tests happier)
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE: Final[Path] = BASE_DIR / "templates" / "vintage.tex"
LUA_FILTER: Final[Path] = BASE_DIR / "filters" / "content-aware-tables.lua"
FONTS_DIR: Final[Path] = BASE_DIR / "fonts"
DEFAULT_MARKDOWN_FORMAT: Final[str] = (
    "markdown+yaml_metadata_block+tex_math_dollars+tex_math_single_backslash+fenced_divs+bracketed_spans"
    "+fenced_code_attributes+pipe_tables+grid_tables+multiline_tables+simple_tables"
    "+table_captions+implicit_figures+link_attributes+task_lists+strikeout+footnotes"
    "+raw_tex+smart"
)
WEB_MARKDOWN_FORMAT: Final[str] = DEFAULT_MARKDOWN_FORMAT.replace("+raw_tex", "-raw_tex")
CONVERSION_TIMEOUT_SECONDS: Final[int] = int(os.environ.get("CONVERSION_TIMEOUT_SECONDS", "45"))


@dataclass(frozen=True)
class ConversionResult:
    warnings: tuple[str, ...] = ()
    diagnostics: str = ""


class ConversionError(RuntimeError):
    def __init__(self, message: str, diagnostics: str = "", *, input_error: bool = False) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics
        self.input_error = input_error


_MISSING_GLYPH_RE = re.compile(r"Missing character: There is no (.*?) \(U\+([0-9A-F]+)\)")


def _diagnostic_warnings(stderr: str) -> list[str]:
    warnings: list[str] = []
    missing = []
    for character, codepoint in _MISSING_GLYPH_RE.findall(stderr):
        label = character.strip() or "character"
        item = f"{label} (U+{codepoint})"
        if item not in missing:
            missing.append(item)
    if missing:
        warnings.append("Unsupported glyphs may be absent from the PDF: " + ", ".join(missing))
    if "Overfull \\hbox" in stderr:
        warnings.append("Some content may extend beyond its text area; review the PDF preview.")
    return warnings


def _preflight_warnings(markdown: str, source_dir: Path) -> list[str]:
    warnings: list[str] = []
    fenced = False
    visible_lines: list[str] = []
    for line in markdown.splitlines():
        fence = re.match(r"^\s*(```+|~~~+)\s*([^\s]*)", line)
        if fence:
            if not fenced and fence.group(2).lower() == "mermaid":
                warnings.append("Mermaid diagrams are not rendered; the source block is shown as code.")
            fenced = not fenced
            visible_lines.append("")
            continue
        visible_lines.append("" if fenced else re.sub(r"`[^`]*`", "", line))

    visible = "\n".join(visible_lines)
    citation_keys = sorted(set(re.findall(r"(?<!\\)\[@([A-Za-z0-9_:.+/-]+)", visible)))
    if citation_keys:
        warnings.append("Unresolved citation keys: " + ", ".join(citation_keys))

    for target in re.findall(r"!\[[^\]]*\]\(([^)\s]+)", visible):
        clean_target = target.strip("<>")
        if re.match(r"^(?:https?://|data:)", clean_target, re.IGNORECASE):
            warnings.append(f"External image was not validated: {clean_target}")
        elif not (source_dir / clean_target).is_file():
            warnings.append(f"Missing image: {clean_target}")
    return list(dict.fromkeys(warnings))


def _input_error(stderr: str) -> bool:
    markers = (
        "File ended while scanning",
        "Runaway argument",
        "Missing $ inserted",
        "Extra }, or forgotten",
    )
    return any(marker in stderr for marker in markers)


def convert_with_diagnostics(
    src: Path,
    dst: Path,
    markdown_format: str,
    template_path: Path,
) -> ConversionResult:
    """Convert Markdown and return bounded, user-facing diagnostics."""

    if not src.is_file():
        raise FileNotFoundError(f"source file does not exist: {src}")
    if not template_path.is_file():
        raise FileNotFoundError(f"template does not exist: {template_path}")
    if not LUA_FILTER.is_file():
        raise FileNotFoundError(f"lua filter does not exist: {LUA_FILTER}")
    if not FONTS_DIR.is_dir():
        raise FileNotFoundError(f"fonts directory does not exist: {FONTS_DIR}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    resource_paths = [src.parent.resolve(), Path.cwd().resolve(), BASE_DIR.resolve()]
    resource_path_arg = os.pathsep.join(dict.fromkeys(str(path) for path in resource_paths))
    command = [
        pypandoc.get_pandoc_path(),
        str(src),
        "-o",
        str(dst),
        f"--template={template_path}",
        "--pdf-engine=xelatex",
        "--pdf-engine-opt=-interaction=nonstopmode",
        "--lua-filter",
        str(LUA_FILTER),
        "--resource-path",
        resource_path_arg,
        "-V",
        f"fontdir={FONTS_DIR.resolve().as_posix()}/",
    ]
    if markdown_format and markdown_format.lower() != "auto":
        command.extend(["-f", markdown_format])

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=CONVERSION_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ConversionError("Conversion timed out.", str(exc)) from exc

    diagnostics = completed.stderr[-12_000:]
    if completed.returncode != 0:
        logging.error("pandoc failed with exit code %s: %s", completed.returncode, diagnostics)
        raise ConversionError(
            "The Markdown contains an equation or construct that could not be typeset."
            if _input_error(diagnostics)
            else "The renderer could not generate this PDF.",
            diagnostics,
            input_error=_input_error(diagnostics),
        )
    if not dst.is_file() or dst.stat().st_size == 0:
        raise ConversionError("The renderer produced an empty PDF.", diagnostics)

    markdown = src.read_text(encoding="utf-8")
    warnings = _preflight_warnings(markdown, src.parent)
    warnings.extend(_diagnostic_warnings(diagnostics))
    return ConversionResult(tuple(dict.fromkeys(warnings)), diagnostics)


def convert(src: Path, dst: Path, markdown_format: str, template_path: Path) -> None:  # noqa: D401 – keep signature untouched
    """Convert src md -> dst pdf.

    NOTE: tests + API import this directly, so don't get clever w/ args.
    """

    convert_with_diagnostics(src, dst, markdown_format, template_path)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    # keep parser separate so tests can poke it if needed
    parser = argparse.ArgumentParser(
        prog="md2pdf",
        description="Render Markdown → PDF (offline, no server).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # either a path OR stdin. no point supporting both at once.
    src_group = parser.add_mutually_exclusive_group(required=False)
    src_group.add_argument(
        "source",
        type=Path,
        nargs="?",
        help="Path to the Markdown file to render.",
    )
    src_group.add_argument(
        "--stdin",
        action="store_true",
        help="Read Markdown from STDIN instead of a file.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output PDF path (default: <source>.pdf or stdin.pdf).",
    )
    parser.add_argument(
        "--markdown-format",
        default=DEFAULT_MARKDOWN_FORMAT,
        help="Pandoc input format string. Use 'auto' to let pandoc detect it.",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="Path to LaTeX template (.tex).",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging.")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:  # noqa: D401 – CLI entry-point signature
    args = _parse_args(argv)

    # logging: default to INFO (quiet-ish); -v flips to DEBUG
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # resolve input
    if args.stdin:
        # read stdin into a temp file so we can reuse convert() as-is
        stdin_markdown = sys.stdin.read()
        if not stdin_markdown.strip():
            print("Empty input on STDIN", file=sys.stderr)
            sys.exit(1)

        tmp_src = NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
        tmp_src.write(stdin_markdown)
        tmp_src.close()
        src_path = Path(tmp_src.name)
        cleanup_tmp_src = True
    else:
        if args.source is None:
            # tests want the magic substrings even when arg is missing
            print("source file does not exist", file=sys.stderr)
            sys.exit(1)

        src_path = args.source.expanduser().resolve()
        cleanup_tmp_src = False

    if not src_path.is_file():
        print(f"source file does not exist: {src_path}", file=sys.stderr)
        sys.exit(1)

    # resolve output; default next to input
    dst_path = args.output or src_path.with_suffix(".pdf")

    # run it
    try:
        convert(src_path, dst_path, args.markdown_format, args.template)
    except FileNotFoundError as exc:
        # user/config error (missing file/template/filter)
        print(exc, file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        # unexpected: keep stderr message short, but log stack for debugging
        logging.exception("unhandled error in conversion")
        print(f"conversion error: {exc}", file=sys.stderr)
        sys.exit(2)
    finally:
        # stdin mode drops a temp file in cwd; clean it up best-effort
        if cleanup_tmp_src:
            try:
                src_path.unlink(missing_ok=True)
            except Exception:
                # nothing to do here; it's a temp file anyway
                pass

    # ok
    print(f"✓ created {dst_path.resolve()}")
    sys.exit(0)


if __name__ == "__main__":
    main()
