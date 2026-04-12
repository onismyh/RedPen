"""Shared test fixtures and helpers for RedPen test suite."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from redpen.cli import app

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
runner = CliRunner()


def copy_example(name: str, tmp_path: Path) -> Path:
    src = EXAMPLES / name
    dst = tmp_path / name
    shutil.copy(src, dst)
    return dst


def fake_generate_basic(paragraphs, mode, lang, model=None):
    """Standard fake Claude response for review --run tests."""
    return [
        {
            "paragraph_index": 2,
            "changes": [
                {
                    "original": "Recent large language models (LLMs) have improved many NLP tasks.",
                    "revised": "Recent large language models (LLMs) have substantially improved many NLP tasks.",
                    "reason": "增强学术语气并提高表达准确性。",
                }
            ],
        }
    ]
