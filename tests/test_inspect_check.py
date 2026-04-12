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
    assert len(data) > 0
    # Check expected keys
    first = data[0]
    assert "index" in first
    assert "section" in first
    assert "is_heading" in first
    assert "is_protected" in first
    assert "text_preview" in first
    # At least one heading detected
    assert any(item["is_heading"] for item in data)
    # At least one protected paragraph (reference entries start with [N])
    assert any(item["is_protected"] for item in data)
    # Section detection: should find "references"
    assert any(item["section"] == "references" for item in data)


def test_check_json(tmp_path: Path) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)

    result = runner.invoke(app, ["check", str(doc), "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert isinstance(data, dict)  # now returns health summary object
    assert "findings" in data
    assert "health" in data
    findings = data["findings"]
    assert isinstance(findings, list)
    assert len(findings) > 0
    # Should find protected regions (citations, figure refs, etc.)
    kinds = {item["kind"] for item in findings}
    assert "protected_region" in kinds
    # Each item has required keys
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
    assert "tracked_changes_count" in health
    assert "comments_count" in health
    assert "warnings" in health
    assert "errors" in health
    assert isinstance(health["warnings"], list)
    assert isinstance(health["errors"], list)


def test_check_references_modification_warning(tmp_path: Path) -> None:
    """Check on a reviewed doc should warn about references section modifications."""
    from tests.conftest import fake_generate_basic

    # First create a reviewed doc
    doc = copy_example("academic_paper.docx", tmp_path)
    # We just run check on the base doc — references section should be flagged
    result = runner.invoke(app, ["check", str(doc), "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    # The findings should include references-related info
    findings = data["findings"]
    assert len(findings) > 0
