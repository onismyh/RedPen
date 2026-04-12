"""LLM backend abstraction for edit generation.

Defines a lightweight protocol so RedPen can swap model providers
without touching the review/CLI layers.
"""

from __future__ import annotations

import json
import subprocess
from typing import Protocol, Sequence, runtime_checkable


# ---------------------------------------------------------------------------
# Backend protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class LLMBackend(Protocol):
    """Minimal interface that any LLM backend must satisfy."""

    def generate_edits(
        self,
        paragraphs: Sequence[dict],
        mode: str,
        lang: str,
        model: str | None = None,
    ) -> list[dict]:
        """Return a list of edit dicts in the standard redpen format."""
        ...


# ---------------------------------------------------------------------------
# System prompt shared across backends
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """\
You are an expert academic paper editor. Review the provided paragraphs and \
generate precise text edits in JSON format.

Mode: {mode}
Rules:
- Do NOT modify citations like [1], (Author, 2024), inline math ($...$), \
Figure/Table/Equation references (Fig. 1, Table 2, Eq. 3), URLs, or DOIs.
- Skip paragraphs in the References/Bibliography section entirely.
- Each edit must specify the exact original text and the revised text.
- Keep edits minimal and preserve the author's meaning.
{lang_instruction}

Output a JSON array of objects, each with:
  {{"paragraph_index": <int>, "changes": [{{"original": "...", "revised": "...", "reason": "..."}}]}}
Only include paragraphs that need changes. Output ONLY valid JSON, no markdown fences."""

LANG_ZH = "Write all change reasons and comments in Chinese (中文)."
LANG_EN = "Write all change reasons and comments in English."


def build_user_message(paragraphs: Sequence[dict]) -> str:
    """Format paragraphs into the standard user message."""
    lines = [f"[Paragraph {p['index']}] {p['text']}" for p in paragraphs]
    return "\n\n".join(lines)


def build_system_prompt(mode: str, lang: str) -> str:
    """Build the system prompt for a given mode and language."""
    lang_instruction = LANG_ZH if lang == "zh" else LANG_EN
    return SYSTEM_PROMPT_TEMPLATE.format(mode=mode, lang_instruction=lang_instruction)


# ---------------------------------------------------------------------------
# Claude CLI backend
# ---------------------------------------------------------------------------

class ClaudeCLIBackend:
    """Calls the ``claude`` CLI as a subprocess to generate edits."""

    def generate_edits(
        self,
        paragraphs: Sequence[dict],
        mode: str,
        lang: str,
        model: str | None = None,
    ) -> list[dict]:
        system_prompt = build_system_prompt(mode, lang)
        user_message = build_user_message(paragraphs)

        cmd = [
            "claude", "-p", user_message,
            "--output-format", "json",
            "--allowedTools", "",
            "--append-system-prompt", system_prompt,
        ]
        if model:
            cmd.extend(["--model", model])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)

        # Claude Code JSON output wraps the response in {"result": ...}
        outer = json.loads(result.stdout)
        content = outer.get("result", result.stdout) if isinstance(outer, dict) else result.stdout
        if isinstance(content, str):
            edits = json.loads(content)
        else:
            edits = content
        return edits


# ---------------------------------------------------------------------------
# Module-level default backend
# ---------------------------------------------------------------------------

_backend: LLMBackend = ClaudeCLIBackend()


def get_backend() -> LLMBackend:
    """Return the current LLM backend."""
    return _backend


def set_backend(backend: LLMBackend) -> None:
    """Replace the current LLM backend (useful for testing or alternative providers)."""
    global _backend
    _backend = backend
