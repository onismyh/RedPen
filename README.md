# RedPen

**Stop rewriting. Start redlining.**

RedPen lets AI edit Word documents the way humans review them: with native Word Track Changes, comments, and line-by-line Accept / Reject control.

> [**中文文档 (Chinese README)**](./README_CN.md)

## Why RedPen exists

Most AI writing tools give you a fully rewritten document.

That is bad for review workflows because:
- you cannot see exactly what changed
- you cannot accept only some edits
- you lose the natural approval flow people already use in Word

RedPen fixes that.

Instead of producing a second draft, it writes edits back as real Word revisions:
- deletions
- insertions
- comments with reasons
- native Accept / Reject in Microsoft Word

## What you get

RedPen is for people who want AI help without giving up editorial control.

Best for:
- academic paper proofreading
- contract and policy review
- bilingual revision workflows
- executive memo polishing
- AI agent document review pipelines

## 10-second mental model

```text
redpen read   -> agent decides edits -> redpen apply
  JSON             your AI / reviewer      Track Changes + comments in Word
```

Open the output document in Word:
Review -> All Markup -> Accept / Reject each change.

## Why not just let AI rewrite the whole document?

Because review is not generation.

A rewritten document hides decisions.
A redlined document exposes decisions.

RedPen is built for the second case.

## Quick start

### Install

```bash
git clone https://github.com/onismyh/RedPen.git
cd RedPen
pip install -e .
```

Requires Python 3.10+.

### 3-minute workflow

1. Read the document as structured text:

```bash
redpen read report.docx
```

2. Let your AI agent decide the edits, or start from a recipe scaffold:

```bash
redpen recipe proofread report.docx --json > proofread.json
```

3. Write revisions back into Word:

```bash
redpen apply report.docx @proofread.json -o revised.docx
```

4. Inspect the changes:

```bash
redpen show revised.docx
```

## Example workflows

### 1. Proofread a report

```bash
redpen recipe proofread report.docx --json > edits.json
redpen apply report.docx @edits.json -o report-reviewed.docx
```

Use when you want grammar and clarity fixes while preserving meaning.

### 2. Tighten an executive memo

```bash
redpen recipe tighten memo.docx --json > edits.json
redpen apply memo.docx @edits.json -o memo-tightened.docx
```

Use when you want less fluff and more concise writing.

### 3. Reviewer mode for collaborative editing

```bash
redpen recipe reviewer draft.docx
```

Use when the author should review each suggestion with Track Changes and comments.

### 4. Academic paper review (English papers)

RedPen has a dedicated workflow for reviewing English academic papers.
It automatically detects sections (Abstract, Methods, Results, …),
protects citations (`[1]`, `(Author, 2024)`), inline math (`$...$`),
figure/table/equation references, URLs and DOIs from modification,
and skips the References section entirely.

**Three review modes:**

| Mode | Focus |
|---|---|
| `proofread` | Grammar and clarity only |
| `academic-polish` | Grammar + conciseness + terminology + academic tone |
| `reviewer` | Full review: all of the above + logic flow |

**Quickstart** (using the included example):

```bash
# 1. Inspect document structure and protected regions
redpen inspect examples/academic_paper.docx

# 2. Generate a review plan (no AI, deterministic scaffold)
redpen review examples/academic_paper.docx --mode academic-polish --json

# 3. Run the full review (calls Claude, produces 3 artifacts)
redpen review examples/academic_paper.docx --mode academic-polish --run
```

With `--run`, three files are produced:

| File | Contents |
|---|---|
| `<stem>.reviewed.docx` | Track Changes + comments — open in Word to Accept/Reject |
| `<stem>.reviewed.clean.docx` | All changes accepted — the "final" version |
| `<stem>.reviewed.report.json` | Machine-readable summary (counts, paths, mode) |

**Comment language** defaults to Chinese (`zh`) from `~/.redpen.toml`.
Override per-call with `--lang en` or `--lang zh`.

```toml
# ~/.redpen.toml
[default]
comment_language = "en"   # or "zh"
```

**Lightweight pre-check** (no AI needed):

```bash
redpen check examples/academic_paper.docx --json
```

Finds protected regions, overly long sentences, and other heuristics.

## Commands

| Command | What it does | Example |
|---|---|---|
| `read` | Extract paragraphs as JSON | `redpen read doc.docx` |
| `apply` | Write tracked changes from JSON | `redpen apply doc.docx @edits.json -o out.docx` |
| `replace` | Find & replace with tracking | `redpen replace doc.docx "old" "new"` |
| `diff` | Compare two versions -> revisions | `redpen diff v1.docx v2.docx -o diff.docx` |
| `show` | View tracked changes | `redpen show revised.docx` |
| `accept` | Accept all changes | `redpen accept revised.docx -o clean.docx` |
| `reject` | Reject all changes | `redpen reject revised.docx -o original.docx` |
| `recipe` | Generate task-oriented editing scaffolds | `redpen recipe proofread doc.docx --json` |
| `review` | Academic paper review (scaffold or full run) | `redpen review paper.docx --mode academic-polish --run` |
| `inspect` | Show document structure and protected regions | `redpen inspect paper.docx` |
| `check` | Lightweight rule-based scan (no AI) | `redpen check paper.docx --json` |

## `apply` JSON format

```json
[
  {
    "paragraph_index": 0,
    "changes": [
      {
        "original": "text to find",
        "revised": "replacement",
        "reason": "written as Word comment"
      }
    ]
  }
]
```

Accepts:
- `@file.json`
- stdin pipe
- inline JSON string

## FAQ

**Do I need an API key?**
No. Your AI agent decides what to change. RedPen only writes the edits back as Word Track Changes.

**Can I accept only some changes?**
Yes. Right-click any change in Word -> Accept or Reject.

**Can't see tracked changes in Word?**
Review tab -> Display for Review -> All Markup.

**Is this only for AI agents?**
No. Humans can use it too. But it is especially useful as a revision layer for Claude Code, Codex, OpenCode, and similar agents.
