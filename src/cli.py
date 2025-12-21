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
import logging
import sys
from pathlib import Path
from typing import Final

import pypandoc

# bundled stuff lives relative to repo root (keeps docker + tests happier)
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE: Final[Path] = BASE_DIR / "templates" / "vintage.tex"
LUA_FILTER: Final[Path] = BASE_DIR / "filters" / "landscape-6col.lua"


def convert(src: Path, dst: Path, markdown_format: str, template_path: Path) -> None:  # noqa: D401 – keep signature untouched
    """Convert src md -> dst pdf.

    NOTE: tests + API import this directly, so don't get clever w/ args.
    """

    # sanity: fail early w/ msgs tests grep for
    if not src.is_file():
        raise FileNotFoundError(f"source file does not exist: {src}")

    # tpl must exist. if not, better to crash than silently make junk output.
    if not template_path.is_file():
        raise FileNotFoundError(f"template does not exist: {template_path}")

    # lua filter is "required" right now. if this goes missing, packaging is broken.
    if not LUA_FILTER.is_file():
        raise FileNotFoundError(f"lua filter does not exist: {LUA_FILTER}")

    # make sure out dir exists (pandoc won't do it for you)
    dst.parent.mkdir(parents=True, exist_ok=True)

    # pandoc knobs. keep these boring + explicit so diffs are easy to read later.
    extra_args = [
        f"--template={template_path}",
        "--pdf-engine=xelatex",
        "--lua-filter",
        str(LUA_FILTER),
        "-f",
        f"{markdown_format}-yaml_metadata_block",
    ]

    logging.debug("pandoc extra_args=%s", extra_args)

    # do the work; pypandoc throws RuntimeError on pandoc failures
    try:
        pypandoc.convert_file(
            str(src),
            to="pdf",
            outputfile=str(dst),
            extra_args=extra_args,
        )
    except RuntimeError as exc:
        # don't leak a mile of pandoc spew to callers; log it + raise a clean error
        logging.error("pandoc failed: %s", exc)
        raise RuntimeError("pandoc conversion failed") from exc


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
        choices=["gfm", "commonmark_x"],
        default="gfm",
        help="Markdown flavour to expect in the input.",
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

        # use a stable-ish temp name; ok for local usage + CI. (not great for concurrency.)
        tmp_src = Path("stdin.md").resolve()
        tmp_src.write_text(stdin_markdown, encoding="utf-8")
        src_path = tmp_src
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
