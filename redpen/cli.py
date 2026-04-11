"""RedPen CLI — Word track changes toolkit for AI agents."""

from __future__ import annotations

import json as json_mod
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

import logging

app = typer.Typer(
    name="redpen",
    help="Word track changes toolkit for AI agents (Claude Code / Codex / OpenCode).",
    no_args_is_help=True,
)
console = Console()
logger = logging.getLogger("redpen")


def _resolve_output(input_path: str, output: str | None) -> str:
    """If -o is given use it, otherwise overwrite the input file (in-place)."""
    if output:
        from pathlib import Path
        out = Path(output).resolve()
        inp = Path(input_path).resolve()
        if out == inp:
            logger.warning("Output path is the same as input path. File will be overwritten.")
    return output if output else input_path


# ---------------------------------------------------------------------------
# redpen read
# ---------------------------------------------------------------------------
@app.command()
def read(
    input_file: str = typer.Argument(..., help=".docx file to read"),
    plain: bool = typer.Option(False, "--plain", help="Plain text instead of JSON"),
) -> None:
    """Extract document paragraphs as JSON (default) or plain text.

    If the document already has tracked changes (from a previous round),
    the text shown is the "accepted" version — i.e. what the document
    looks like after accepting all prior revisions.  This lets agents
    make further edits on the latest state.
    """
    from docx_revisions import RevisionDocument

    rdoc = RevisionDocument(input_file)
    paragraphs = []
    for i, para in enumerate(rdoc.paragraphs):
        text = para.accepted_text
        if text.strip():
            paragraphs.append({"index": i, "text": text})

    has_changes = len(rdoc.track_changes) > 0

    if plain:
        for p in paragraphs:
            console.print(f"[{p['index']}] {p['text']}")
    else:
        print(json_mod.dumps(paragraphs, ensure_ascii=False, indent=2))

    if has_changes:
        Console(stderr=True).print(
            "[dim](document has existing tracked changes — "
            "text shown is the accepted/latest version)[/dim]"
        )


# ---------------------------------------------------------------------------
# redpen apply
# ---------------------------------------------------------------------------
@app.command()
def apply(
    input_file: str = typer.Argument(..., help="Input .docx file"),
    edits_json: str = typer.Argument(
        None, help="JSON string, @file path, or omit to read from stdin"
    ),
    output: str = typer.Option(None, "-o", "--output", help="Output file path"),
    author: str = typer.Option("Claude", "--author", help="Revision author name"),
    comment: bool = typer.Option(True, "--comment/--no-comment", help="Add comments from reason fields"),
) -> None:
    """Apply edits as Word tracked changes from JSON.

    Accepts JSON as:
      - Inline argument:  redpen apply doc.docx '[...]'
      - File reference:   redpen apply doc.docx @edits.json
      - Stdin pipe:       echo '[...]' | redpen apply doc.docx

    JSON format:

        [{"paragraph_index": 0, "changes": [
            {"original": "old", "revised": "new", "reason": "why"}
        ]}]
    """
    from .revision_writer import apply_tracked_changes, ParagraphEdit, TextChange
    from .comment_writer import add_comments_to_edits

    # Load JSON from argument, @file, or stdin
    if edits_json is None:
        if sys.stdin.isatty():
            console.print("[red]Error:[/red] No edits provided. Pass JSON, @file, or pipe via stdin.")
            raise typer.Exit(1)
        raw = sys.stdin.read()
    elif edits_json.startswith("@"):
        with open(edits_json[1:], "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = edits_json

    data = json_mod.loads(raw)
    edits = []
    for item in data:
        changes = [
            TextChange(
                original=c["original"],
                revised=c["revised"],
                reason=c.get("reason", ""),
            )
            for c in item.get("changes", [])
            if c.get("original") != c.get("revised")
        ]
        if changes:
            edits.append(ParagraphEdit(
                paragraph_index=item["paragraph_index"],
                changes=changes,
            ))

    if not edits:
        console.print("[yellow]No effective changes in the provided JSON.[/yellow]")
        raise typer.Exit(0)

    out_path = _resolve_output(input_file, output)
    rdoc = apply_tracked_changes(input_file, edits, author=author)

    if comment:
        doc = rdoc.document
        paragraphs = list(doc.paragraphs)
        add_comments_to_edits(doc, paragraphs, edits, author=author)

    rdoc.save(out_path)

    total = sum(len(e.changes) for e in edits)
    console.print(f"Applied {total} tracked changes across {len(edits)} paragraphs -> {out_path}")


# ---------------------------------------------------------------------------
# redpen replace
# ---------------------------------------------------------------------------
@app.command()
def replace(
    input_file: str = typer.Argument(..., help="Input .docx file"),
    search: str = typer.Argument(..., help="Text to find"),
    replacement: str = typer.Argument(..., help="Replacement text"),
    output: str = typer.Option(None, "-o", "--output", help="Output file path"),
    author: str = typer.Option("Claude", "--author", help="Revision author name"),
) -> None:
    """Find and replace with revision tracking."""
    from .revision_writer import find_and_replace_tracked

    out_path = _resolve_output(input_file, output)
    rdoc, count = find_and_replace_tracked(input_file, search, replacement, author=author)

    if count == 0:
        console.print(f"[yellow]Text not found:[/yellow] \"{search}\"")
        raise typer.Exit(1)

    rdoc.save(out_path)
    console.print(f"Replaced {count} occurrence(s) -> {out_path}")


# ---------------------------------------------------------------------------
# redpen diff
# ---------------------------------------------------------------------------
@app.command()
def diff(
    old_file: str = typer.Argument(..., help="Original .docx file"),
    new_file: str = typer.Argument(..., help="Modified .docx file"),
    output: str = typer.Option(None, "-o", "--output", help="Output file path"),
    author: str = typer.Option("Claude", "--author", help="Revision author name"),
) -> None:
    """Compare two documents, output a revision-tracked docx."""
    from .differ import diff_documents

    out_path = _resolve_output(old_file, output)
    rdoc = diff_documents(old_file, new_file, author=author)
    rdoc.save(out_path)
    console.print(f"Diff complete -> {out_path}")


# ---------------------------------------------------------------------------
# redpen show
# ---------------------------------------------------------------------------
@app.command()
def show(
    input_file: str = typer.Argument(..., help=".docx file with tracked changes"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Display tracked changes (table or JSON)."""
    from docx_revisions import RevisionDocument, TrackedInsertion, TrackedDeletion

    rdoc = RevisionDocument(input_file)
    changes = rdoc.track_changes

    if not changes:
        if json_output:
            print("[]")
        else:
            console.print("[yellow]No tracked changes found.[/yellow]")
        return

    if json_output:
        items = []
        for change in changes:
            items.append({
                "type": "insert" if isinstance(change, TrackedInsertion) else "delete",
                "author": change.author or "",
                "text": change.text,
            })
        print(json_mod.dumps(items, ensure_ascii=False, indent=2))
    else:
        table = Table(title=f"Tracked Changes - {Path(input_file).name}", show_lines=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Type", width=8)
        table.add_column("Author", width=14)
        table.add_column("Text", min_width=40)

        for i, change in enumerate(changes, 1):
            if isinstance(change, TrackedInsertion):
                change_type = Text("INSERT", style="green bold")
            elif isinstance(change, TrackedDeletion):
                change_type = Text("DELETE", style="red bold")
            else:
                change_type = Text("OTHER", style="yellow")

            text = change.text if change.text else ""
            display = text[:120] + ("..." if len(text) > 120 else "")
            table.add_row(str(i), change_type, change.author or "-", display)

        console.print(table)
        console.print(f"\nTotal: {len(changes)} tracked changes")


# ---------------------------------------------------------------------------
# redpen accept
# ---------------------------------------------------------------------------
@app.command()
def accept(
    input_file: str = typer.Argument(..., help=".docx file with tracked changes"),
    output: str = typer.Option(None, "-o", "--output", help="Output file path"),
) -> None:
    """Accept all tracked changes, produce a clean document."""
    from .revision_writer import accept_all

    out_path = _resolve_output(input_file, output)
    rdoc = accept_all(input_file)
    rdoc.save(out_path)
    console.print(f"All changes accepted -> {out_path}")


# ---------------------------------------------------------------------------
# redpen reject
# ---------------------------------------------------------------------------
@app.command()
def reject(
    input_file: str = typer.Argument(..., help=".docx file with tracked changes"),
    output: str = typer.Option(None, "-o", "--output", help="Output file path"),
) -> None:
    """Reject all tracked changes, restore original text."""
    from .revision_writer import reject_all

    out_path = _resolve_output(input_file, output)
    rdoc = reject_all(input_file)
    rdoc.save(out_path)
    console.print(f"All changes rejected -> {out_path}")


if __name__ == "__main__":
    app()
