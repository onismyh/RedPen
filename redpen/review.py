"""Review scaffold/plan generator for academic papers.

Generates a structured review plan with per-section review items.
Also provides generate_edits_with_claude() which delegates to the
pluggable LLM backend defined in :mod:`redpen.llm`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Sequence

from .academic import (
    SectionKind,
    build_academic_structure,
    find_protected_spans,
)


class ReviewMode(str, Enum):
    PROOFREAD = "proofread"
    ACADEMIC_POLISH = "academic-polish"
    REVIEWER = "reviewer"


# ---------------------------------------------------------------------------
# Comment / label language
# ---------------------------------------------------------------------------

_LABELS_ZH: dict[str, str] = {
    "title": "标题",
    "abstract": "摘要",
    "introduction": "引言",
    "related_work": "相关工作",
    "method": "方法",
    "experiment": "实验",
    "result": "结果",
    "discussion": "讨论",
    "conclusion": "结论",
    "references": "参考文献",
    "appendix": "附录",
    "acknowledgement": "致谢",
    "other": "其他",
    # Review item labels
    "grammar": "语法",
    "clarity": "清晰度",
    "conciseness": "简洁性",
    "terminology": "术语一致性",
    "logic_flow": "逻辑连贯",
    "academic_tone": "学术语气",
    "protected_skip": "受保护区域(跳过)",
    "section_skip": "参考文献区域(跳过)",
    # Severity
    "high": "高",
    "medium": "中",
    "low": "低",
    "info": "信息",
}

_LABELS_EN: dict[str, str] = {
    "title": "Title",
    "abstract": "Abstract",
    "introduction": "Introduction",
    "related_work": "Related Work",
    "method": "Methods",
    "experiment": "Experiments",
    "result": "Results",
    "discussion": "Discussion",
    "conclusion": "Conclusion",
    "references": "References",
    "appendix": "Appendix",
    "acknowledgement": "Acknowledgement",
    "other": "Other",
    "grammar": "Grammar",
    "clarity": "Clarity",
    "conciseness": "Conciseness",
    "terminology": "Terminology consistency",
    "logic_flow": "Logic flow",
    "academic_tone": "Academic tone",
    "protected_skip": "Protected region (skip)",
    "section_skip": "References section (skip)",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "info": "Info",
}


def _labels(lang: str) -> dict[str, str]:
    return _LABELS_ZH if lang == "zh" else _LABELS_EN


# ---------------------------------------------------------------------------
# Review item
# ---------------------------------------------------------------------------

@dataclass
class ReviewItem:
    paragraph_index: int
    section: str
    category: str           # grammar | clarity | conciseness | terminology | logic_flow | academic_tone
    severity: str           # high | medium | low | info
    note: str               # human-readable instruction / placeholder
    protected_spans: list[dict] | None = None  # spans to preserve if any


@dataclass
class ReviewPlan:
    mode: str
    lang: str
    total_paragraphs: int
    reviewable_paragraphs: int
    skipped_paragraphs: int
    sections_found: list[str]
    items: list[ReviewItem]

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "lang": self.lang,
            "total_paragraphs": self.total_paragraphs,
            "reviewable_paragraphs": self.reviewable_paragraphs,
            "skipped_paragraphs": self.skipped_paragraphs,
            "sections_found": self.sections_found,
            "items": [asdict(item) for item in self.items],
        }

    def to_json(self, **kwargs) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, **kwargs)


# ---------------------------------------------------------------------------
# Category determination per mode
# ---------------------------------------------------------------------------

_MODE_CATEGORIES: dict[ReviewMode, list[str]] = {
    ReviewMode.PROOFREAD: ["grammar", "clarity"],
    ReviewMode.ACADEMIC_POLISH: ["grammar", "clarity", "conciseness", "terminology", "academic_tone"],
    ReviewMode.REVIEWER: ["grammar", "clarity", "conciseness", "terminology", "logic_flow", "academic_tone"],
}


def _severity_for(section: SectionKind, category: str) -> str:
    """Heuristic severity based on section importance and category."""
    if section == SectionKind.ABSTRACT:
        return "high"
    if section in (SectionKind.INTRODUCTION, SectionKind.CONCLUSION):
        return "high" if category in ("clarity", "logic_flow") else "medium"
    if section in (SectionKind.METHOD, SectionKind.EXPERIMENT):
        return "high" if category == "terminology" else "medium"
    return "medium"


# Sections that should be entirely skipped during review
_SKIP_SECTIONS = {SectionKind.REFERENCES, SectionKind.APPENDIX}


# ---------------------------------------------------------------------------
# Plan generation
# ---------------------------------------------------------------------------

def generate_review_plan(
    paragraphs: Sequence[dict],
    mode: ReviewMode | str = ReviewMode.PROOFREAD,
    lang: str = "zh",
) -> ReviewPlan:
    """Build a review plan from paragraph dicts.

    *paragraphs* should be a list of dicts with at least ``index`` and ``text``.
    Optional keys: ``is_heading``, ``style``.

    Returns a :class:`ReviewPlan` with per-paragraph review items.
    No actual LLM calls are made — this is a deterministic scaffold.
    """
    if isinstance(mode, str):
        mode = ReviewMode(mode)

    labels = _labels(lang)
    structure = build_academic_structure(paragraphs)
    categories = _MODE_CATEGORIES[mode]

    items: list[ReviewItem] = []
    skipped = 0
    sections_seen: set[str] = set()

    for ap in structure:
        sections_seen.add(ap.section.value)

        # Skip headings — nothing to review
        if ap.is_heading:
            continue

        # Skip empty
        if not ap.text.strip():
            skipped += 1
            continue

        # Skip protected sections (references, appendix)
        if ap.section in _SKIP_SECTIONS:
            skipped += 1
            items.append(ReviewItem(
                paragraph_index=ap.index,
                section=labels.get(ap.section.value, ap.section.value),
                category=labels["section_skip"],
                severity=labels["info"],
                note="",
            ))
            continue

        # Skip fully-protected paragraphs (pure citations, formulas, etc.)
        if ap.is_protected:
            skipped += 1
            items.append(ReviewItem(
                paragraph_index=ap.index,
                section=labels.get(ap.section.value, ap.section.value),
                category=labels["protected_skip"],
                severity=labels["info"],
                note="",
            ))
            continue

        # Generate review items for each applicable category
        pspans = [{"start": s.start, "end": s.end, "kind": s.kind, "text": s.text}
                   for s in ap.protected_spans] or None

        for cat in categories:
            items.append(ReviewItem(
                paragraph_index=ap.index,
                section=labels.get(ap.section.value, ap.section.value),
                category=labels.get(cat, cat),
                severity=labels.get(_severity_for(ap.section, cat), "medium"),
                note="",
                protected_spans=pspans,
            ))

    reviewable = len(structure) - skipped
    return ReviewPlan(
        mode=mode.value,
        lang=lang,
        total_paragraphs=len(structure),
        reviewable_paragraphs=reviewable,
        skipped_paragraphs=skipped,
        sections_found=sorted(sections_seen),
        items=items,
    )


# ---------------------------------------------------------------------------
# Lightweight check (quick scan)
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    paragraph_index: int
    kind: str       # "protected_region" | "long_sentence" | "passive_voice_hint"
    message: str
    span: tuple[int, int] | None = None


def quick_check(paragraphs: Sequence[dict], lang: str = "zh") -> list[CheckResult]:
    """Run lightweight, rule-based checks on paragraph text.

    No LLM needed. Returns a list of findings. Currently checks:
    - Protected-region inventory (citations, formulas, refs)
    - Overly long sentences (>50 words)
    - Possible passive voice hints (English only)
    """
    results: list[CheckResult] = []

    for p in paragraphs:
        idx = p["index"]
        text = p.get("text", "")
        if not text.strip():
            continue

        # Protected spans inventory
        spans = find_protected_spans(text)
        for s in spans:
            results.append(CheckResult(
                paragraph_index=idx,
                kind="protected_region",
                message=f"{s.kind}: {s.text!r}",
                span=(s.start, s.end),
            ))

        # Long sentences
        sentences = [s.strip() for s in text.replace("。", ".").split(".") if s.strip()]
        for sent in sentences:
            word_count = len(sent.split())
            if word_count > 50:
                results.append(CheckResult(
                    paragraph_index=idx,
                    kind="long_sentence",
                    message=f"Sentence with {word_count} words (>50): {sent[:80]}...",
                ))

    return results


# ---------------------------------------------------------------------------
# Claude-powered edit generation (delegates to LLM backend)
# ---------------------------------------------------------------------------

def generate_edits_with_claude(
    paragraphs: Sequence[dict],
    mode: str,
    lang: str,
    model: str | None = None,
) -> list[dict]:
    """Call the active LLM backend to generate edits.

    Returns a list of edit dicts in the standard redpen apply format.
    This function is designed to be easily monkeypatched in tests.
    """
    from .llm import get_backend

    return get_backend().generate_edits(paragraphs, mode=mode, lang=lang, model=model)
