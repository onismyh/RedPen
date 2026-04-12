# RedPen Showcase

This directory defines the flagship demo narrative for RedPen's academic-first product.

## Demo goal

Show, in under a minute, that RedPen is **not** a full-document rewriter.
It is a system that turns AI suggestions into **native Word revisions**.

## Recommended demo flow

Use the bundled paper:

- `../academic_paper.docx`

### Step 1 — Show protection and structure
```bash
redpen inspect ../academic_paper.docx
```

Call out that RedPen identifies:
- major paper sections
- protected citations
- formula-like spans
- figure / table / equation references
- skipped References section

### Step 2 — Show the preflight
```bash
redpen review ../academic_paper.docx --mode academic-polish
```

This frames the task as a review workflow, not an opaque rewrite.

### Step 3 — Run the full academic review
```bash
redpen review ../academic_paper.docx --mode academic-polish --lang zh --run
```

Expected outputs:
- `academic_paper.reviewed.docx`
- `academic_paper.reviewed.clean.docx`
- `academic_paper.reviewed.report.json`

### Step 4 — Open the reviewed file in Word

In Word, show:
- Track Changes markup
- comments attached to the edits
- Accept / Reject flow

This is the key moment: the user sees that AI suggestions came back in a format that is still fully reviewable.

### Step 5 — Show the clean artifact and report

Explain the bundle:
- reviewed file for human review
- clean file for downstream editing or submission
- report JSON for agents, pipelines, or QA

## Talking points

### What to emphasize
- "Stop rewriting. Start redlining."
- The product is academic-first.
- Protected content is a feature, not a footnote.
- Reviewability matters more than raw generation.

### What not to emphasize
- Do not position RedPen as a generic AI editor.
- Do not lead with low-level JSON/apply mechanics.
- Do not turn the demo into a CLI feature tour.

## Suggested before/after framing

**Before:** a paper that still needs polishing, but where the author must retain control.

**After:** a Word-native review package with:
- visible edits
- clear comments
- preserved citations and references
- a clean accepted version
- a structured report
