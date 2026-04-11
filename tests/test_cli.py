from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

from redpen.cli import app

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
runner = CliRunner()


def _copy_example(name: str, tmp_path: Path) -> Path:
    src = EXAMPLES / name
    dst = tmp_path / name
    shutil.copy(src, dst)
    return dst


def test_read_outputs_json_for_sample_doc(tmp_path: Path) -> None:
    doc = _copy_example("sample.docx", tmp_path)

    result = runner.invoke(app, ["read", str(doc)])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data[0]["text"] == "Q1 季度工作总结"
    assert any("销售额方面" in para["text"] for para in data)


def test_apply_writes_tracked_changes_docx(tmp_path: Path) -> None:
    doc = _copy_example("sample.docx", tmp_path)
    edits = EXAMPLES / "edits.json"
    out = tmp_path / "revised.docx"

    result = runner.invoke(app, ["apply", str(doc), f"@{edits}", "-o", str(out)])

    assert result.exit_code == 0
    assert out.exists()
    assert "Applied" in result.stdout

    show_result = runner.invoke(app, ["show", str(out), "--json"])
    assert show_result.exit_code == 0
    changes = json.loads(show_result.stdout)
    assert changes
    assert any(item["type"] == "insert" for item in changes)


def test_recipe_proofread_outputs_scaffold_json(tmp_path: Path) -> None:
    doc = _copy_example("sample.docx", tmp_path)

    result = runner.invoke(app, ["recipe", "proofread", str(doc), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["recipe"] == "proofread"
    assert payload["input_file"].endswith("sample.docx")
    assert payload["suggested_command"] == f"redpen apply {doc} @proofread.edits.json -o revised.docx"
    assert payload["starter_edits"]
    assert payload["starter_edits"][0]["changes"][0]["reason"]


def test_recipe_reviewer_mentions_reviewer_mode(tmp_path: Path) -> None:
    doc = _copy_example("sample.docx", tmp_path)

    result = runner.invoke(app, ["recipe", "reviewer", str(doc)])

    assert result.exit_code == 0
    assert "reviewer" in result.stdout.lower()
    assert "Track Changes" in result.stdout
    assert "Accept / Reject" in result.stdout
