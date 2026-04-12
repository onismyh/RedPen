"""Tests for inspect and check commands."""
from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import copy_example, runner

from redpen.cli import app


def test_inspect_json(tmp_path: Path) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)

    result = runner.invoke(app, ["inspect", str(doc), "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert isinstance(data, dict)
    assert "paragraphs" in data
    assert "summary" in data

    paragraphs = data["paragraphs"]
    assert len(paragraphs) > 0

    first = paragraphs[0]
    assert "index" in first
    assert "section" in first
    assert "is_heading" in first
    assert "is_protected" in first
    assert "text_preview" in first
    assert any(item["is_heading"] for item in paragraphs)
    assert any(item["is_protected"] for item in paragraphs)
    assert any(item["section"] == "references" for item in paragraphs)

    summary = data["summary"]
    assert "sections" in summary
    assert "section_counts" in summary
    assert "protection" in summary
    assert "protected_paragraphs" in summary["protection"]


def test_check_json(tmp_path: Path) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)

    result = runner.invoke(app, ["check", str(doc), "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert isinstance(data, dict)
    assert "findings" in data
    assert "health" in data
    findings = data["findings"]
    assert isinstance(findings, list)
    assert len(findings) > 0

    kinds = {item["kind"] for item in findings}
    assert "protected_region" in kinds
    for item in findings:
        assert "paragraph_index" in item
        assert "kind" in item
        assert "message" in item


def test_check_health_summary(tmp_path: Path) -> None:
    """Check command should return a health summary with warnings/errors."""
    doc = copy_example("academic_paper.docx", tmp_path)

    result = runner.invoke(app, ["check", str(doc), "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    health = data["health"]
    assert "status" in health
    assert "tracked_changes_count" in health
    assert "comments_count" in health
    assert "warning_count" in health
    assert "finding_count" in health
    assert "warnings" in health
    assert "errors" in health
    assert isinstance(health["warnings"], list)
    assert isinstance(health["errors"], list)


def test_check_includes_protection_summary(tmp_path: Path) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)

    result = runner.invoke(app, ["check", str(doc), "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    protection = data["protection"]
    assert "protected_paragraphs" in protection
    assert "protected_span_counts" in protection
    assert "skipped_sections" in protection


def test_check_references_modification_warning(tmp_path: Path) -> None:
    """Check on a reviewed doc should warn about references section modifications."""
    doc = copy_example("academic_paper.docx", tmp_path)
    result = runner.invoke(app, ["check", str(doc), "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    findings = data["findings"]
    assert len(findings) > 0
    assert data["health"]["warning_count"] >= 1
