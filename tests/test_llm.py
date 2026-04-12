"""Tests for the LLM backend abstraction layer."""
from __future__ import annotations

import json
import subprocess

import pytest

from redpen.llm import (
    ClaudeCLIBackend,
    LLMBackend,
    build_system_prompt,
    build_user_message,
    get_backend,
    set_backend,
)


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------

class FakeBackend:
    """Minimal implementation that satisfies LLMBackend."""

    def __init__(self, edits: list[dict] | None = None):
        self.calls: list[dict] = []
        self._edits = edits or []

    def generate_edits(self, paragraphs, mode, lang, model=None):
        self.calls.append({"paragraphs": paragraphs, "mode": mode, "lang": lang, "model": model})
        return self._edits


def test_fake_backend_satisfies_protocol():
    backend = FakeBackend()
    assert isinstance(backend, LLMBackend)


def test_claude_cli_backend_satisfies_protocol():
    backend = ClaudeCLIBackend()
    assert isinstance(backend, LLMBackend)


# ---------------------------------------------------------------------------
# get_backend / set_backend
# ---------------------------------------------------------------------------

def test_default_backend_is_claude_cli():
    assert isinstance(get_backend(), ClaudeCLIBackend)


def test_set_backend_swaps_and_restores():
    original = get_backend()
    fake = FakeBackend(edits=[{"paragraph_index": 0, "changes": []}])
    set_backend(fake)
    try:
        assert get_backend() is fake
    finally:
        set_backend(original)
    assert get_backend() is original


# ---------------------------------------------------------------------------
# generate_edits delegates through get_backend
# ---------------------------------------------------------------------------

def test_generate_edits_delegates_to_backend():
    original = get_backend()
    expected = [{"paragraph_index": 1, "changes": [{"original": "a", "revised": "b", "reason": "c"}]}]
    fake = FakeBackend(edits=expected)
    set_backend(fake)
    try:
        from redpen.review import generate_edits_with_claude

        paragraphs = [{"index": 1, "text": "hello"}]
        result = generate_edits_with_claude(paragraphs, mode="proofread", lang="en", model="test-model")
        assert result == expected
        assert len(fake.calls) == 1
        assert fake.calls[0]["mode"] == "proofread"
        assert fake.calls[0]["lang"] == "en"
        assert fake.calls[0]["model"] == "test-model"
    finally:
        set_backend(original)


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def test_build_system_prompt_zh():
    prompt = build_system_prompt("proofread", "zh")
    assert "Mode: proofread" in prompt
    assert "中文" in prompt


def test_build_system_prompt_en():
    prompt = build_system_prompt("academic-polish", "en")
    assert "Mode: academic-polish" in prompt
    assert "English" in prompt


def test_build_user_message():
    paragraphs = [
        {"index": 0, "text": "First paragraph."},
        {"index": 3, "text": "Fourth paragraph."},
    ]
    msg = build_user_message(paragraphs)
    assert "[Paragraph 0] First paragraph." in msg
    assert "[Paragraph 3] Fourth paragraph." in msg
    assert "\n\n" in msg


# ---------------------------------------------------------------------------
# ClaudeCLIBackend subprocess (monkeypatched)
# ---------------------------------------------------------------------------

def test_claude_cli_backend_subprocess_call(monkeypatch):
    """ClaudeCLIBackend should shell out to `claude` and parse the result."""
    edits = [{"paragraph_index": 0, "changes": [{"original": "a", "revised": "b", "reason": "c"}]}]
    stdout = json.dumps({"result": json.dumps(edits)})

    def fake_run(cmd, **kwargs):
        assert cmd[0] == "claude"
        assert "--append-system-prompt" in cmd
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=stdout, stderr="")

    monkeypatch.setattr("redpen.llm.subprocess.run", fake_run)

    backend = ClaudeCLIBackend()
    result = backend.generate_edits(
        [{"index": 0, "text": "hello"}], mode="proofread", lang="zh",
    )
    assert result == edits


def test_claude_cli_backend_passes_model_flag(monkeypatch):
    """When model is provided, --model flag should appear in the command."""
    captured_cmd = []

    def fake_run(cmd, **kwargs):
        captured_cmd.extend(cmd)
        return subprocess.CompletedProcess(
            args=cmd, returncode=0,
            stdout=json.dumps({"result": "[]"}), stderr="",
        )

    monkeypatch.setattr("redpen.llm.subprocess.run", fake_run)

    backend = ClaudeCLIBackend()
    backend.generate_edits(
        [{"index": 0, "text": "hi"}], mode="reviewer", lang="en", model="claude-opus-4-20250514",
    )
    assert "--model" in captured_cmd
    assert "claude-opus-4-20250514" in captured_cmd


def test_claude_cli_backend_no_model_flag(monkeypatch):
    """When model is None, --model flag should NOT appear."""
    captured_cmd = []

    def fake_run(cmd, **kwargs):
        captured_cmd.extend(cmd)
        return subprocess.CompletedProcess(
            args=cmd, returncode=0,
            stdout=json.dumps({"result": "[]"}), stderr="",
        )

    monkeypatch.setattr("redpen.llm.subprocess.run", fake_run)

    backend = ClaudeCLIBackend()
    backend.generate_edits(
        [{"index": 0, "text": "hi"}], mode="proofread", lang="zh",
    )
    assert "--model" not in captured_cmd
