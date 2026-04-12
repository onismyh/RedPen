"""Preserve run formatting (bold, italic, font, color, etc.) when applying tracked changes.

docx-revisions creates plain w:r elements for del/ins runs, losing all
character formatting.  This module copies the rPr from the source runs
so that replacements inherit the original styling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lxml import etree

from docx.oxml.ns import qn

if TYPE_CHECKING:
    from docx.text.paragraph import Paragraph as DocxParagraph


# OOXML tags we care about
_W_R = qn("w:r")
_W_DEL = qn("w:del")
_W_INS = qn("w:ins")
_W_RPR = qn("w:rPr")


def _find_nearest_format_source(elements: list[etree._Element], index: int) -> etree._Element | None:
    """Find the nearest <w:r> element, skipping over del/ins elements.

    Searches left first (the text before the match), then right.
    Returns the <w:r> element or None.
    """
    # Search left
    for i in range(index - 1, -1, -1):
        el = elements[i]
        if el.tag == _W_R:
            return el
        if el.tag not in (_W_DEL, _W_INS):
            break  # hit an unrelated element, stop searching

    # Search right
    for i in range(index + 1, len(elements)):
        el = elements[i]
        if el.tag == _W_R:
            return el
        if el.tag not in (_W_DEL, _W_INS):
            break

    return None


def _copy_rpr(src_r_elem: etree._Element, dest_r_elem: etree._Element) -> None:
    """Copy w:rPr from one w:r element to another via deep copy."""
    src_rpr = src_r_elem.find(_W_RPR)
    if src_rpr is None:
        return
    copied_rpr = etree.fromstring(etree.tostring(src_rpr))
    dest_r_elem.insert(0, copied_rpr)


def copy_format_to_runs(parent: etree._Element, source_paragraph) -> int:
    """Copy formatting from original runs to all del/ins runs in the paragraph.

    For each del/ins element, finds the nearest non-revision <w:r> element
    (searching left first, then right, skipping over other del/ins elements)
    and copies its rPr. This handles multiple consecutive replacements where
    del/ins elements become adjacent.

    Returns the number of runs that received formatting.
    """
    count = 0
    elements = list(parent)

    for i, el in enumerate(elements):
        if el.tag not in (_W_DEL, _W_INS):
            continue

        # Find the w:r child inside the del/ins element
        run_elem = el.find(_W_R)
        if run_elem is None:
            continue

        source = _find_nearest_format_source(elements, i)
        if source is not None:
            _copy_rpr(source, run_elem)
            count += 1

    return count
