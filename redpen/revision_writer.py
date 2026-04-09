"""Wrapper around docx-revisions for applying tracked changes to Word documents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from lxml import etree
from docx_revisions import RevisionDocument

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WNS = f"{{{WORD_NS}}}"


def _enable_markup_view(rdoc: RevisionDocument) -> None:
    """Ensure Word opens the document with tracked changes visible.

    Sets <w:revisionView> with markup=true in settings.xml so that
    Word defaults to 'All Markup' view instead of hiding revisions.
    """
    doc = rdoc.document
    settings_el = doc.settings.element

    # Remove existing revisionView if any
    for rv in settings_el.findall(f"{WNS}revisionView"):
        settings_el.remove(rv)

    # Add <w:revisionView w:markup="1" w:comments="1"
    #       w:insDel="1" w:formatting="1" />
    rv = etree.SubElement(settings_el, f"{WNS}revisionView")
    rv.set(f"{WNS}markup", "1")
    rv.set(f"{WNS}comments", "1")
    rv.set(f"{WNS}insDel", "1")
    rv.set(f"{WNS}formatting", "1")


@dataclass
class TextChange:
    """A single text change within a paragraph."""

    original: str
    revised: str
    reason: str = ""


@dataclass
class ParagraphEdit:
    """All changes for one paragraph, identified by index."""

    paragraph_index: int
    changes: list[TextChange]


def apply_tracked_changes(
    doc_path: str,
    edits: list[ParagraphEdit],
    author: str = "AI Reviewer",
) -> RevisionDocument:
    """Open a document and apply a list of edits as tracked changes.

    Each edit locates text in a specific paragraph and replaces it
    using the revision tracking API (produces <w:del> + <w:ins>).
    """
    rdoc = RevisionDocument(doc_path)

    for edit in edits:
        idx = edit.paragraph_index
        if idx < 0 or idx >= len(rdoc.paragraphs):
            continue

        para = rdoc.paragraphs[idx]
        for change in edit.changes:
            if change.original == change.revised:
                continue
            para.replace_tracked(
                search_text=change.original,
                replace_text=change.revised,
                author=author,
            )

    _enable_markup_view(rdoc)
    return rdoc


def find_and_replace_tracked(
    doc_path: str,
    search_text: str,
    replace_text: str,
    author: str = "AI Reviewer",
) -> tuple[RevisionDocument, int]:
    """Document-wide find-and-replace with revision tracking.

    Returns (document, count_of_replacements).
    """
    rdoc = RevisionDocument(doc_path)
    count = rdoc.find_and_replace_tracked(
        search_text=search_text,
        replace_text=replace_text,
        author=author,
    )
    _enable_markup_view(rdoc)
    return rdoc, count


def accept_all(doc_path: str) -> RevisionDocument:
    """Accept all tracked changes in a document."""
    rdoc = RevisionDocument(doc_path)
    rdoc.accept_all()
    return rdoc


def reject_all(doc_path: str) -> RevisionDocument:
    """Reject all tracked changes in a document."""
    rdoc = RevisionDocument(doc_path)
    rdoc.reject_all()
    return rdoc
