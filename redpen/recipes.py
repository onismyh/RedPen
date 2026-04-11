"""Task-oriented recipe scaffolds for common RedPen workflows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import typer
from docx import Document
from rich.console import Console

console = Console()
app = typer.Typer(help="Common revision workflows that generate starter scaffolds.")


@dataclass(frozen=True)
class RecipeSpec:
    name: str
    intent: str
    prompt: str
    change_reason: str
    description: str


RECIPES: dict[str, RecipeSpec] = {
    "proofread": RecipeSpec(
        name="proofread",
        intent="Fix grammar, punctuation, and wording while preserving meaning.",
        prompt=(
            "Proofread this Word document paragraph by paragraph. Keep the author's meaning, "
            "make minimal edits, and explain each change briefly in the reason field."
        ),
        change_reason="Fix grammar or improve clarity while preserving meaning.",
        description="Best for grammar cleanup, typo fixes, and light polishing.",
    ),
    "tighten": RecipeSpec(
        name="tighten",
        intent="Make writing more concise and executive without changing claims.",
        prompt=(
            "Tighten this document. Remove redundancy, shorten weak phrases, and keep the tone professional. "
            "Explain each reduction in the reason field."
        ),
        change_reason="Make the sentence more concise and direct.",
        description="Best for reducing fluff in reports, updates, and memos.",
    ),
    "reviewer": RecipeSpec(
        name="reviewer",
        intent="Act like a human reviewer using Track Changes and comments.",
        prompt=(
            "Review this document like a human reviewer. Use conservative revisions, preserve the author's voice, "
            "and write comments that explain concerns or recommendations."
        ),
        change_reason="Reviewer note explaining the suggested change.",
        description="Best for collaborative review where the author will Accept / Reject each edit.",
    ),
}


def _starter_edits(doc_path: Path, reason: str) -> list[dict]:
    doc = Document(str(doc_path))
    edits: list[dict] = []
    for idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if len(text) < 12:
            continue
        edits.append(
            {
                "paragraph_index": idx,
                "changes": [
                    {
                        "original": text,
                        "revised": text,
                        "reason": reason,
                    }
                ],
            }
        )
        if len(edits) == 2:
            break
    return edits


def _build_payload(recipe: RecipeSpec, input_file: Path) -> dict:
    return {
        "recipe": recipe.name,
        "input_file": str(input_file),
        "description": recipe.description,
        "prompt": recipe.prompt,
        "suggested_command": f"redpen apply {input_file} @{recipe.name}.edits.json -o revised.docx",
        "starter_edits": _starter_edits(input_file, recipe.change_reason),
    }


@app.command()
def proofread(
    input_file: str = typer.Argument(..., help="Input .docx file"),
    json_output: bool = typer.Option(False, "--json", help="Output recipe scaffold as JSON"),
) -> None:
    """Generate a starter scaffold for proofreading."""
    payload = _build_payload(RECIPES["proofread"], Path(input_file).resolve())
    if json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    console.print("[bold]RedPen recipe: proofread[/bold]")
    console.print("Use Track Changes to fix grammar and clarity without rewriting the whole document.")
    console.print(f"Input: {payload['input_file']}")
    console.print(f"Prompt: {payload['prompt']}")
    console.print(f"Next: {payload['suggested_command']}")


@app.command()
def tighten(
    input_file: str = typer.Argument(..., help="Input .docx file"),
    json_output: bool = typer.Option(False, "--json", help="Output recipe scaffold as JSON"),
) -> None:
    """Generate a starter scaffold for concise revision."""
    payload = _build_payload(RECIPES["tighten"], Path(input_file).resolve())
    if json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    console.print("[bold]RedPen recipe: tighten[/bold]")
    console.print("Use Track Changes to compress wording without changing claims.")
    console.print(f"Input: {payload['input_file']}")
    console.print(f"Prompt: {payload['prompt']}")
    console.print(f"Next: {payload['suggested_command']}")


@app.command()
def reviewer(
    input_file: str = typer.Argument(..., help="Input .docx file"),
    json_output: bool = typer.Option(False, "--json", help="Output recipe scaffold as JSON"),
) -> None:
    """Generate a starter scaffold for reviewer-style feedback."""
    payload = _build_payload(RECIPES["reviewer"], Path(input_file).resolve())
    if json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    console.print("[bold]RedPen recipe: reviewer[/bold]")
    console.print("Review with native Word Track Changes so the author can Accept / Reject each edit.")
    console.print("This mode is best for editorial or collaborative reviewer workflows.")
    console.print(f"Input: {payload['input_file']}")
    console.print(f"Prompt: {payload['prompt']}")
    console.print(f"Next: {payload['suggested_command']}")
