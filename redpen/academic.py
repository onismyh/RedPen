"""Academic paper helpers — section detection, high-risk region protection, and structure analysis."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


# ---------------------------------------------------------------------------
# Section classification
# ---------------------------------------------------------------------------

class SectionKind(str, Enum):
    TITLE = "title"
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    RELATED_WORK = "related_work"
    METHOD = "method"
    EXPERIMENT = "experiment"
    RESULT = "result"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    APPENDIX = "appendix"
    ACKNOWLEDGEMENT = "acknowledgement"
    OTHER = "other"


# Ordered patterns: first match wins
_SECTION_PATTERNS: list[tuple[re.Pattern, SectionKind]] = [
    (re.compile(r"\breference", re.I), SectionKind.REFERENCES),
    (re.compile(r"\bbibliograph", re.I), SectionKind.REFERENCES),
    (re.compile(r"\babstract\b", re.I), SectionKind.ABSTRACT),
    (re.compile(r"\bintroduction\b", re.I), SectionKind.INTRODUCTION),
    (re.compile(r"\brelated\s+work", re.I), SectionKind.RELATED_WORK),
    (re.compile(r"\bliterature\s+review", re.I), SectionKind.RELATED_WORK),
    (re.compile(r"\bmethod(ology|s)?\b", re.I), SectionKind.METHOD),
    (re.compile(r"\bapproach\b", re.I), SectionKind.METHOD),
    (re.compile(r"\bexperiment", re.I), SectionKind.EXPERIMENT),
    (re.compile(r"\bevaluation\b", re.I), SectionKind.EXPERIMENT),
    (re.compile(r"\bresult", re.I), SectionKind.RESULT),
    (re.compile(r"\bfinding", re.I), SectionKind.RESULT),
    (re.compile(r"\bdiscussion\b", re.I), SectionKind.DISCUSSION),
    (re.compile(r"\banalysis\b", re.I), SectionKind.DISCUSSION),
    (re.compile(r"\bconclusion", re.I), SectionKind.CONCLUSION),
    (re.compile(r"\bsummary\b", re.I), SectionKind.CONCLUSION),
    (re.compile(r"\bappendix", re.I), SectionKind.APPENDIX),
    (re.compile(r"\backnowledg", re.I), SectionKind.ACKNOWLEDGEMENT),
]


def classify_section(heading_text: str) -> SectionKind:
    """Classify a heading into a known academic section kind."""
    text = heading_text.strip()
    # Strip leading numbering like "1.", "1.1", "II.", "A."
    text = re.sub(r"^[\dIVXivx]+[\.\)]\s*", "", text)
    text = re.sub(r"^[A-Z][\.\)]\s*", "", text)
    for pattern, kind in _SECTION_PATTERNS:
        if pattern.search(text):
            return kind
    return SectionKind.OTHER


# ---------------------------------------------------------------------------
# High-risk region detection
# ---------------------------------------------------------------------------

@dataclass
class ProtectedSpan:
    """A region within paragraph text that should not be edited."""
    start: int
    end: int
    kind: str  # "citation", "formula", "figure_ref", "table_ref", "equation_ref", "url"
    text: str


# Regex patterns for high-risk regions in academic text
_CITATION_BRACKET = re.compile(r"\[[\d,;\s\-–]+\]")                  # [1], [1,2], [1-3]
_CITATION_PARENS = re.compile(                                         # (Author, 2024) / (Author et al., 2024)
    r"\([A-Z][a-z]+(?:\s+(?:et\s+al\.|and|&)\s+[A-Z][a-z]+)*"
    r",?\s*\d{4}[a-z]?\)"
)
_FIGURE_REF = re.compile(r"\bFig(?:ure|\.)\s*[\d\.]+", re.I)
_TABLE_REF = re.compile(r"\bTable\s*[\d\.]+", re.I)
_EQUATION_REF = re.compile(r"\b(?:Eq(?:uation|\.)|Eqn\.)\s*[\(\d][\d\.\)]*", re.I)
_SECTION_REF = re.compile(r"\b(?:Section|Sec\.)\s*[\d\.]+", re.I)
_INLINE_MATH = re.compile(r"\$[^$]+\$")                               # $...$
_DISPLAY_MATH = re.compile(r"\$\$[^$]+\$\$")                          # $$...$$
_URL = re.compile(r"https?://\S+")
_DOI = re.compile(r"\b(?:doi:|DOI:?\s*)\S+", re.I)

_PROTECTED_PATTERNS: list[tuple[re.Pattern, str]] = [
    (_DISPLAY_MATH, "formula"),
    (_INLINE_MATH, "formula"),
    (_CITATION_BRACKET, "citation"),
    (_CITATION_PARENS, "citation"),
    (_FIGURE_REF, "figure_ref"),
    (_TABLE_REF, "table_ref"),
    (_EQUATION_REF, "equation_ref"),
    (_SECTION_REF, "section_ref"),
    (_URL, "url"),
    (_DOI, "doi"),
]


def find_protected_spans(text: str) -> list[ProtectedSpan]:
    """Return all high-risk spans in *text* that should be preserved during editing.

    Spans are sorted by start position and non-overlapping (earlier/longer wins).
    """
    raw: list[ProtectedSpan] = []
    for pattern, kind in _PROTECTED_PATTERNS:
        for m in pattern.finditer(text):
            raw.append(ProtectedSpan(m.start(), m.end(), kind, m.group()))

    # Sort by start, then by length descending (prefer longer matches)
    raw.sort(key=lambda s: (s.start, -(s.end - s.start)))

    # Remove overlaps: greedy left-to-right
    merged: list[ProtectedSpan] = []
    last_end = -1
    for span in raw:
        if span.start >= last_end:
            merged.append(span)
            last_end = span.end
    return merged


def is_protected_paragraph(text: str) -> bool:
    """Return True if the entire paragraph looks like it should not be edited.

    Examples: pure reference entries, raw LaTeX blocks, URLs-only.
    """
    stripped = text.strip()
    if not stripped:
        return True
    # Reference list entry: starts with [N] or a numbered marker
    if re.match(r"^\[\d+\]", stripped):
        return True
    # All-formula paragraph
    if stripped.startswith("$$") and stripped.endswith("$$"):
        return True
    # All-URL
    if _URL.fullmatch(stripped):
        return True
    return False


# ---------------------------------------------------------------------------
# Paragraph-level structure info
# ---------------------------------------------------------------------------

@dataclass
class AcademicParagraph:
    """Enriched paragraph metadata for academic review."""
    index: int
    text: str
    section: SectionKind = SectionKind.OTHER
    is_heading: bool = False
    is_protected: bool = False
    protected_spans: list[ProtectedSpan] = field(default_factory=list)


def build_academic_structure(
    paragraphs: Sequence[dict],
) -> list[AcademicParagraph]:
    """Build section-aware structure from paragraph dicts (as returned by ``redpen read --meta``).

    Each dict must have at least ``index`` and ``text`` keys.
    Optional: ``is_heading``, ``style``.
    """
    result: list[AcademicParagraph] = []
    current_section = SectionKind.OTHER

    for p in paragraphs:
        idx = p["index"]
        text = p.get("text", "")
        heading = p.get("is_heading", False)

        if heading:
            current_section = classify_section(text)

        ap = AcademicParagraph(
            index=idx,
            text=text,
            section=current_section,
            is_heading=heading,
            is_protected=is_protected_paragraph(text),
            protected_spans=find_protected_spans(text),
        )
        result.append(ap)

    return result


# ---------------------------------------------------------------------------
# Safe-edit mask helper
# ---------------------------------------------------------------------------

def editable_ranges(text: str, protected: list[ProtectedSpan] | None = None) -> list[tuple[int, int]]:
    """Return list of ``(start, end)`` character ranges in *text* that are safe to edit.

    Protected spans are excluded. Useful for telling an AI agent which parts of a
    sentence it may modify.
    """
    if protected is None:
        protected = find_protected_spans(text)
    if not protected:
        return [(0, len(text))]

    ranges: list[tuple[int, int]] = []
    cursor = 0
    for span in protected:
        if span.start > cursor:
            ranges.append((cursor, span.start))
        cursor = max(cursor, span.end)
    if cursor < len(text):
        ranges.append((cursor, len(text)))
    return ranges
