"""Rendered output checks for the audit's documented content losses."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.cli import (
    ConversionError,
    DEFAULT_TEMPLATE,
    WEB_MARKDOWN_FORMAT,
    convert_with_diagnostics,
)

fitz = pytest.importorskip("fitz")
FIXTURES = Path(__file__).parent / "fixtures" / "audit"


def render_case(name: str, tmp_path: Path):
    source = FIXTURES / f"{name}.md"
    output = tmp_path / f"{name}.pdf"
    result = convert_with_diagnostics(source, output, WEB_MARKDOWN_FORMAT, DEFAULT_TEMPLATE)
    document = fitz.open(output)
    text = "\n".join(page.get_text() for page in document)
    return document, text, result


def test_small_table_stays_on_one_portrait_page(tmp_path: Path):
    document, text, _ = render_case("02_small_table", tmp_path)
    assert len(document) == 1
    assert document[0].rect.width < document[0].rect.height
    assert "Group A" in text and "END_SMALL_927" in text


def test_wide_table_headers_and_values_do_not_collide(tmp_path: Path):
    document, text, _ = render_case("03_wide_table", tmp_path)
    assert all(f"Marker_{index:02d}" in text for index in range(1, 7))
    page = next(page for page in document if "Marker_01" in page.get_text())
    estimate = page.search_for("Estimate")[0]
    lower = page.search_for("Lower CI")[0]
    upper = page.search_for("Upper CI")[0]
    assert not estimate.intersects(lower)
    assert not lower.intersects(upper)


def test_realistic_report_preserves_numbers_and_label_spacing(tmp_path: Path):
    document, text, _ = render_case("16_realistic_report", tmp_path)
    assert len(document) == 1
    assert "12,480" in text and "58,231.5" in text
    assert "1.43" in text and "1.21–1.68" in text
    assert "Ischaemic/cerebrovascular" in text
    label = document[0].search_for("Ischaemic/cerebrovascular")[0]
    value = document[0].search_for("3744")[0]
    assert not label.intersects(value)


def test_long_code_is_preserved_and_inside_page(tmp_path: Path):
    document, text, _ = render_case("07_long_code", tmp_path)
    assert "END_LONG_LINE_927" in text
    words = [word for page in document for word in page.get_text("words")]
    assert all(word[2] <= document[0].rect.width - 30 for word in words)


def test_math_currency_and_metadata(tmp_path: Path):
    _, brackets, _ = render_case("05_math_brackets", tmp_path)
    assert "\\(" not in brackets and "\\[" not in brackets
    assert "1.43" in brackets
    _, currency, _ = render_case("14_currency", tmp_path)
    assert "$25" in currency and "$40" in currency and "$65" in currency
    _, metadata, _ = render_case("13_metadata", tmp_path)
    assert "Synthetic mortality report" in metadata
    assert "Example Research Team" in metadata
    assert "25 September 2026" in metadata


def test_literal_code_and_escaped_examples_survive(tmp_path: Path):
    source = tmp_path / "literal.md"
    output = tmp_path / "literal.pdf"
    source.write_text(
        "# Literal examples\n\n```tex\n\\input{example.tex}\n```\n\n"
        "The literal price is \\$25 and the formula is \\(x=2\\).",
        encoding="utf-8",
    )
    convert_with_diagnostics(source, output, WEB_MARKDOWN_FORMAT, DEFAULT_TEMPLATE)
    text = "\n".join(page.get_text() for page in fitz.open(output))
    assert "input" in text and "example.tex" in text
    assert "$25" in text and "x = 2" in text


def test_scientific_minus_is_visible_or_reported(tmp_path: Path):
    _, text, result = render_case("06_unicode", tmp_path)
    assert "10−3" in text or "10-3" in text or "⁻ (U+207B)" in " ".join(result.warnings)
    assert any("Unsupported glyphs" in warning for warning in result.warnings)


def test_warnings_and_bad_equation(tmp_path: Path):
    for name, marker in (
        ("10_mermaid", "Mermaid"),
        ("11_missing_image", "missing-forest-plot.png"),
        ("12_citation", "smith2024"),
    ):
        _, _, result = render_case(name, tmp_path)
        assert marker in " ".join(result.warnings)
    with pytest.raises(ConversionError) as error:
        render_case("15_malformed_math", tmp_path)
    assert error.value.input_error


def test_multipage_headers_and_rows(tmp_path: Path):
    document, text, _ = render_case("08_multipage_table", tmp_path)
    assert len(document) > 1
    assert all(f"REC_{index:03d}" in text for index in range(1, 71))
    table_pages = [page.get_text() for page in document if "REC_" in page.get_text()]
    assert len(table_pages) >= 2
    assert all("Estimate" in page for page in table_pages)


def test_repeated_output_has_same_text_and_pixels(tmp_path: Path):
    first, first_text, _ = render_case("01_basic", tmp_path)
    second, second_text, _ = render_case("18_basic_repeat", tmp_path)
    assert first_text == second_text
    assert first[0].get_pixmap().samples == second[0].get_pixmap().samples
