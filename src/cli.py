#!/usr/bin/env python
"""
md2pdf – Convert Markdown to PDF via Pandoc + XeLaTeX, with GFM/CommonMark support and package safeguards.
"""
from __future__ import annotations
import argparse
import pathlib
import sys
import pypandoc

TEMPLATE = pathlib.Path(__file__).parent.parent / "templates" / "vintage.tex"
LUA = pathlib.Path(__file__).parent.parent / "filters" / "landscape-6col.lua"

def convert(src: pathlib.Path, dst: pathlib.Path, markdown_format: str) -> None:
    if not TEMPLATE.exists():
        sys.exit(f"Template not found: {TEMPLATE}")

    extra_args = [
        f"--template={TEMPLATE}",
        "--pdf-engine=xelatex",
        "--lua-filter",  str(LUA),
        # "--lua-filter", str(pathlib.Path(__file__).parent.parent / "filters" / "shrink-6col-adjust.lua"),
        "-f", f"{markdown_format}-yaml_metadata_block",
    ]

    try:
        pypandoc.convert_file(
            str(src),
            "pdf",
            outputfile=str(dst),
            extra_args=extra_args,
        )
    except RuntimeError as e:
        print(f"Pandoc conversion failed: {e}")
        print("Ensure you have XeLaTeX installed and the necessary LaTeX packages.")
        sys.exit(1)

def main() -> None:
    ap = argparse.ArgumentParser(
        prog="md2pdf",
        description="Render Markdown → PDF (offline, no server) with GFM/CommonMark options.",
    )
    ap.add_argument("source", type=pathlib.Path, help="Markdown file")
    ap.add_argument("-o", "--output", type=pathlib.Path,
                    help="Output PDF (default: <source>.pdf)")
    ap.add_argument(
        "--markdown-format",
        type=str,
        default="gfm",
        choices=["gfm", "commonmark_x"],
        help="Markdown format to use (gfm or commonmark_x, default: gfm)",
    )
    args = ap.parse_args()

    src = args.source
    if not src.exists():
        sys.exit("Source file does not exist.")
    dst = args.output or src.with_suffix(".pdf")
    markdown_format = args.markdown_format

    convert(src, dst, markdown_format)
    print("✓ created", dst.resolve())

if __name__ == "__main__":
    main()

