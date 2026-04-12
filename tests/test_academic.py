"""Tests for academic recipe and section detection."""

from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import copy_example, runner

from redpen.cli import app


def test_recipe_academic_outputs_scaffold_json(tmp_path: Path) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)

    result = runner.invoke(app, ["recipe", "academic", str(doc), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["recipe"] == "academic"
    assert "citation" in payload["prompt"].lower()
    assert payload["comment_language"] == "zh"  # default from config
    assert "中文" in payload["prompt"]  # zh appends Chinese instruction
    assert payload["starter_edits"]
    assert payload["starter_edits"][0]["changes"][0]["reason"]


def test_recipe_academic_comment_lang_en(tmp_path: Path) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)

    result = runner.invoke(app, ["recipe", "academic", str(doc), "--comment-lang", "en", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["comment_language"] == "en"
    assert "English" in payload["prompt"]


def test_recipe_academic_includes_detected_sections(tmp_path: Path) -> None:
    """Academic recipe JSON payload should include detected sections."""
    doc = copy_example("academic_paper.docx", tmp_path)

    result = runner.invoke(app, ["recipe", "academic", str(doc), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert "sections" in payload
    assert isinstance(payload["sections"], list)
    assert len(payload["sections"]) > 0
    # Should detect references section
    assert "references" in payload["sections"]


def test_academic_section_classification() -> None:
    """Unit test for classify_section on common headings."""
    from redpen.academic import classify_section, SectionKind

    assert classify_section("1. Introduction") == SectionKind.INTRODUCTION
    assert classify_section("References") == SectionKind.REFERENCES
    assert classify_section("III. Methodology") == SectionKind.METHOD
    assert classify_section("Abstract") == SectionKind.ABSTRACT
    assert classify_section("A. Appendix A") == SectionKind.APPENDIX


def test_find_protected_spans_coverage() -> None:
    """Unit test for protected span detection."""
    from redpen.academic import find_protected_spans

    text = "As shown in Fig. 1 and Table 2, the model [1,2] achieves $\\alpha=0.05$."
    spans = find_protected_spans(text)
    kinds = {s.kind for s in spans}
    assert "figure_ref" in kinds
    assert "table_ref" in kinds
    assert "citation" in kinds
    assert "formula" in kinds


def test_is_protected_paragraph() -> None:
    """Unit test for paragraph-level protection."""
    from redpen.academic import is_protected_paragraph

    assert is_protected_paragraph("[1] Smith et al. 2024. Some paper.")
    assert is_protected_paragraph("$$E = mc^2$$")
    assert not is_protected_paragraph("This is a normal sentence.")
