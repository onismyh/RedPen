"""High-level orchestration for review --run artifact generation."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .academic import build_academic_structure
from .comment_writer import add_comments_to_edits
from .revision_writer import ApplyStats, ParagraphEdit, accept_all, apply_tracked_changes_protected

REPORT_SCHEMA_VERSION = "1.0.0"


@dataclass
class ReviewRunResult:
    reviewed_path: str
    clean_path: str
    report_path: str
    change_count: int
    paragraphs_changed: int
    protection_warnings: list[dict[str, Any]]
    apply_stats: ApplyStats
    report: dict[str, Any]


def resolve_reviewed_output_path(input_file: str, output: str | None) -> str:
    if output:
        return output
    input_path = Path(input_file)
    return str(input_path.with_suffix("").with_name(input_path.stem + ".reviewed.docx"))


def run_review(
    *,
    input_file: str,
    paragraphs: list[dict],
    edits: list[ParagraphEdit],
    mode: str,
    lang: str,
    output: str | None = None,
    model: str | None = None,
    author: str = "Claude",
) -> ReviewRunResult:
    """Apply review edits and build the standard artifact bundle."""
    out_path = resolve_reviewed_output_path(input_file, output)
    rdoc, protection_warnings, apply_stats, applied_edits = apply_tracked_changes_protected(input_file, edits, author=author)
    doc = rdoc.document
    add_comments_to_edits(doc, list(doc.paragraphs), applied_edits, author=author)
    rdoc.save(out_path)

    out_p = Path(out_path)
    base = out_p.with_suffix("")
    clean_path = base.parent / (base.name + ".clean.docx")
    report_path = base.parent / (base.name + ".report.json")

    clean_rdoc = accept_all(str(out_p))
    clean_rdoc.save(str(clean_path))

    structure = build_academic_structure(paragraphs)
    sections = sorted({ap.section.value for ap in structure})
    protected_count = sum(1 for ap in structure if ap.is_protected)
    span_kinds: dict[str, int] = {}
    for ap in structure:
        for span in ap.protected_spans:
            span_kinds[span.kind] = span_kinds.get(span.kind, 0) + 1

    change_count = apply_stats.applied_changes
    paragraphs_changed = len(apply_stats.applied_paragraph_indexes or set())
    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "mode": mode,
        "lang": lang,
        "source_file": str(Path(input_file).resolve()),
        "reviewed_file": str(out_p.resolve()),
        "clean_file": str(clean_path.resolve()),
        "report_file": str(report_path.resolve()),
        "change_count": change_count,
        "paragraph_count": len(paragraphs),
        "paragraphs_changed": paragraphs_changed,
        "model": model or "",
        "protection_warnings": protection_warnings,
        "artifacts": {
            "reviewed": str(out_p.resolve()),
            "clean": str(clean_path.resolve()),
            "report": str(report_path.resolve()),
        },
        "summary": {
            "sections_found": sections,
            "paragraphs_reviewed": paragraphs_changed,
            "paragraphs_skipped": len(paragraphs) - paragraphs_changed,
            "edits_proposed": apply_stats.proposed_changes,
            "edits_applied": apply_stats.applied_changes,
            "edits_skipped": apply_stats.skipped_changes,
            "edits_not_found": apply_stats.not_found_changes,
        },
        "safety": {
            "protected_paragraphs": protected_count,
            "protected_span_counts": span_kinds,
            "skipped_sections": [s for s in sections if s in ("references", "appendix")],
            "protection_warnings": protection_warnings,
        },
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return ReviewRunResult(
        reviewed_path=str(out_p),
        clean_path=str(clean_path),
        report_path=str(report_path),
        change_count=change_count,
        paragraphs_changed=paragraphs_changed,
        protection_warnings=protection_warnings,
        apply_stats=apply_stats,
        report=report,
    )
