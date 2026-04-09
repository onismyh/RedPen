"""Add Word comments (<w:comment>) via direct XML manipulation.

python-docx and docx-revisions do not support comments natively,
so we manipulate the underlying OOXML directly.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from lxml import etree
from docx.opc.part import Part
from docx.opc.packuri import PackURI

if TYPE_CHECKING:
    from docx.document import Document

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WNS = f"{{{WORD_NS}}}"
COMMENTS_URI = PackURI("/word/comments.xml")
COMMENTS_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
COMMENTS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"


# We store the live XML element on the module level, keyed by document id,
# so that repeated calls within the same document session reuse it.
_comments_cache: dict[int, tuple[etree._Element, Part]] = {}


class _CommentsPart(Part):
    """A Part subclass that holds a live XML element and re-serialises on save."""

    def __init__(self, comments_xml: etree._Element, package):
        super().__init__(
            partname=COMMENTS_URI,
            content_type=COMMENTS_CT,
            blob=etree.tostring(comments_xml, xml_declaration=True, encoding="UTF-8", standalone=True),
            package=package,
        )
        self._comments_xml = comments_xml

    @property
    def blob(self):
        return etree.tostring(
            self._comments_xml, xml_declaration=True, encoding="UTF-8", standalone=True
        )

    @blob.setter
    def blob(self, value):
        pass  # ignore writes from base class


def _get_or_create_comments_part(doc: Document) -> etree._Element:
    """Return the <w:comments> XML element, creating the part if needed."""
    doc_id = id(doc)

    # Check cache first
    if doc_id in _comments_cache:
        return _comments_cache[doc_id][0]

    # Check if comments part already exists via relationships
    for rel in doc.part.rels.values():
        if rel.reltype == COMMENTS_REL:
            target = rel.target_part
            # Parse existing blob into XML
            comments_xml = etree.fromstring(target.blob)
            _comments_cache[doc_id] = (comments_xml, target)

            # Replace with our custom part that re-serialises
            new_part = _CommentsPart(comments_xml, doc.part.package)
            rel._target = new_part
            _comments_cache[doc_id] = (comments_xml, new_part)
            return comments_xml

    # Create fresh
    comments_xml = etree.Element(f"{WNS}comments", nsmap={"w": WORD_NS})
    comments_part = _CommentsPart(comments_xml, doc.part.package)
    doc.part.relate_to(comments_part, COMMENTS_REL)
    _comments_cache[doc_id] = (comments_xml, comments_part)
    return comments_xml


def _next_comment_id(comments_el: etree._Element) -> int:
    """Find the next available comment ID."""
    ids = [
        int(c.get(f"{WNS}id", "0"))
        for c in comments_el.findall(f"{WNS}comment")
    ]
    return max(ids, default=-1) + 1


def add_comment_to_paragraph(
    doc: Document,
    paragraph,
    text: str,
    author: str = "AI Reviewer",
    initials: str = "AI",
    date: datetime | None = None,
) -> int:
    """Add a comment anchored to an entire paragraph.

    Returns the comment ID.
    """
    if date is None:
        date = datetime.now(timezone.utc)

    comments_el = _get_or_create_comments_part(doc)
    comment_id = _next_comment_id(comments_el)
    date_str = date.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build <w:comment>
    comment = etree.SubElement(comments_el, f"{WNS}comment")
    comment.set(f"{WNS}id", str(comment_id))
    comment.set(f"{WNS}author", author)
    comment.set(f"{WNS}initials", initials)
    comment.set(f"{WNS}date", date_str)

    # <w:p><w:r><w:t>text</w:t></w:r></w:p>
    p = etree.SubElement(comment, f"{WNS}p")
    r = etree.SubElement(p, f"{WNS}r")
    t = etree.SubElement(r, f"{WNS}t")
    t.text = text

    # Anchor the comment to the paragraph
    para_el = paragraph._element if hasattr(paragraph, "_element") else paragraph.element

    # commentRangeStart at the beginning
    range_start = etree.Element(f"{WNS}commentRangeStart")
    range_start.set(f"{WNS}id", str(comment_id))
    para_el.insert(0, range_start)

    # commentRangeEnd + commentReference run at the end
    range_end = etree.SubElement(para_el, f"{WNS}commentRangeEnd")
    range_end.set(f"{WNS}id", str(comment_id))

    ref_run = etree.SubElement(para_el, f"{WNS}r")
    rpr = etree.SubElement(ref_run, f"{WNS}rPr")
    rst = etree.SubElement(rpr, f"{WNS}rStyle")
    rst.set(f"{WNS}val", "CommentReference")
    ref = etree.SubElement(ref_run, f"{WNS}commentReference")
    ref.set(f"{WNS}id", str(comment_id))

    return comment_id


def add_comments_to_edits(
    doc: Document,
    paragraphs: list,
    edits,
    author: str = "AI Reviewer",
) -> int:
    """Add comments for all edits that have a reason.

    Returns number of comments added.
    """
    count = 0
    for edit in edits:
        idx = edit.paragraph_index
        if idx < 0 or idx >= len(paragraphs):
            continue

        reasons = [c.reason for c in edit.changes if c.reason]
        if not reasons:
            continue

        comment_text = "; ".join(reasons)
        add_comment_to_paragraph(doc, paragraphs[idx], comment_text, author=author)
        count += 1

    return count
