"""Tests for review plan generation and Claude integration (review --run)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tests.conftest import copy_example, fake_generate_basic, runner

from redpen.cli import app


def test_review_academic_polish_json(tmp_path: Path) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)

    result = runner.invoke(app, ["review", str(doc), "--mode", "academic-polish", "--lang", "zh", "--json"])

    assert result.exit_code == 0, result.output
    plan = json.loads(result.stdout)
    assert plan["mode"] == "academic-polish"
    assert plan["lang"] == "zh"
    assert plan["total_paragraphs"] > 0
    assert plan["reviewable_paragraphs"] > 0
    assert plan["skipped_paragraphs"] > 0  # references are skipped
    assert len(plan["items"]) > 0
    # References section paragraphs should be marked as skipped
    ref_items = [it for it in plan["items"] if "参考文献" in it["section"]]
    assert len(ref_items) > 0  # zh label for references


def test_review_run_json_outputs_generated_edits(tmp_path: Path, monkeypatch) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)
    monkeypatch.setattr("redpen.review.generate_edits_with_claude", fake_generate_basic)

    result = runner.invoke(
        app,
        ["review", str(doc), "--mode", "academic-polish", "--lang", "zh", "--run", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload[0]["paragraph_index"] == 2
    assert payload[0]["changes"][0]["reason"]


def test_review_run_applies_tracked_changes_docx(tmp_path: Path, monkeypatch) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)
    out = tmp_path / "academic-reviewed.docx"
    monkeypatch.setattr("redpen.review.generate_edits_with_claude", fake_generate_basic)

    result = runner.invoke(
        app,
        ["review", str(doc), "--mode", "academic-polish", "--lang", "zh", "--run", "-o", str(out)],
    )

    assert result.exit_code == 0, result.output
    assert out.exists()
    assert "Applied" in result.output or "Review complete" in result.output

    show_result = runner.invoke(app, ["show", str(out), "--json"])
    assert show_result.exit_code == 0
    changes = json.loads(show_result.stdout)
    assert any(item["type"] == "insert" for item in changes)


def test_review_run_writes_clean_and_report_artifacts(tmp_path: Path, monkeypatch) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)
    out = tmp_path / "academic-reviewed.docx"
    clean = tmp_path / "academic-reviewed.clean.docx"
    report = tmp_path / "academic-reviewed.report.json"
    monkeypatch.setattr("redpen.review.generate_edits_with_claude", fake_generate_basic)

    result = runner.invoke(
        app,
        ["review", str(doc), "--mode", "academic-polish", "--lang", "zh", "--run", "-o", str(out)],
    )

    assert result.exit_code == 0, result.output
    assert out.exists()
    assert clean.exists()
    assert report.exists()

    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["mode"] == "academic-polish"
    assert payload["lang"] == "zh"
    assert payload["reviewed_file"].endswith("academic-reviewed.docx")
    assert payload["clean_file"].endswith("academic-reviewed.clean.docx")
    assert payload["change_count"] == 1


def test_review_run_default_output_writes_reviewed_clean_and_report(tmp_path: Path, monkeypatch) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)
    reviewed = tmp_path / "academic_paper.reviewed.docx"
    clean = tmp_path / "academic_paper.reviewed.clean.docx"
    report = tmp_path / "academic_paper.reviewed.report.json"

    def fake_generate(paragraphs, mode, lang, model=None):
        return [
            {
                "paragraph_index": 4,
                "changes": [
                    {
                        "original": "the computational requirements of these models presents a significant barrier",
                        "revised": "the computational requirements of these models present a significant barrier",
                        "reason": "修正主谓一致错误。",
                    }
                ],
            }
        ]

    monkeypatch.setattr("redpen.review.generate_edits_with_claude", fake_generate)

    result = runner.invoke(
        app,
        ["review", str(doc), "--mode", "academic-polish", "--lang", "zh", "--run"],
    )

    assert result.exit_code == 0, result.output
    assert reviewed.exists()
    assert clean.exists()
    assert report.exists()


def test_review_run_handles_claude_timeout(tmp_path: Path, monkeypatch) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)

    def fake_generate(paragraphs, mode, lang, model=None):
        raise subprocess.TimeoutExpired(cmd="claude", timeout=180)

    monkeypatch.setattr("redpen.review.generate_edits_with_claude", fake_generate)

    result = runner.invoke(
        app,
        ["review", str(doc), "--mode", "academic-polish", "--lang", "zh", "--run"],
    )

    assert result.exit_code == 1
    assert "Claude" in result.output
    assert "timeout" in result.output.lower() or "timed out" in result.output.lower()


def test_review_run_handles_claude_failure(tmp_path: Path, monkeypatch) -> None:
    doc = copy_example("academic_paper.docx", tmp_path)

    def fake_generate(paragraphs, mode, lang, model=None):
        raise subprocess.CalledProcessError(1, ["claude"], stderr="boom")

    monkeypatch.setattr("redpen.review.generate_edits_with_claude", fake_generate)

    result = runner.invoke(
        app,
        ["review", str(doc), "--mode", "academic-polish", "--lang", "zh", "--run"],
    )

    assert result.exit_code == 1
    assert "Claude" in result.output
    assert "boom" in result.output


def test_review_run_uses_protection_aware_apply(tmp_path: Path, monkeypatch) -> None:
    """Verify that review --run uses the protection-aware apply path."""
    doc = copy_example("academic_paper.docx", tmp_path)
    out = tmp_path / "reviewed.docx"

    # Fake edits that try to modify a citation — should be filtered
    def fake_generate(paragraphs, mode, lang, model=None):
        return [
            {
                "paragraph_index": 2,
                "changes": [
                    {
                        "original": "Recent large language models (LLMs) have improved many NLP tasks.",
                        "revised": "Recent large language models (LLMs) have substantially improved many NLP tasks.",
                        "reason": "improve clarity",
                    }
                ],
            }
        ]

    monkeypatch.setattr("redpen.review.generate_edits_with_claude", fake_generate)

    result = runner.invoke(
        app,
        ["review", str(doc), "--mode", "academic-polish", "--lang", "zh", "--run", "-o", str(out)],
    )

    assert result.exit_code == 0, result.output
    assert out.exists()
