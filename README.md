# RedPen

**Stop rewriting. Start redlining.**

RedPen turns AI review into **native Word revisions** for academic papers.
Instead of giving you a rewritten draft, it writes edits back as **Track Changes + comments** so you can review every suggestion in Microsoft Word.

> [**中文文档 (Chinese README)**](./README_CN.md)

---

## The one-line product definition

**RedPen is the revision delivery layer between AI and Word.**

For English academic papers, it lets Claude or another model produce suggestions that come back as:
- native Word Track Changes
- comments with reasons
- clean Accept / Reject workflow
- a reviewed file, a clean file, and a machine-readable report

---

## The 30-second demo

```bash
redpen review examples/academic_paper.docx --mode academic-polish --lang zh --run
```

You get three standard deliverables:
- `academic_paper.reviewed.docx` — Track Changes + comments, ready for Word review
- `academic_paper.reviewed.clean.docx` — all changes accepted
- `academic_paper.reviewed.report.json` — summary, safety, and artifact metadata

Then open the reviewed file in Word:

**Review → All Markup → Accept / Reject each change**

---

## Why RedPen exists

Most AI writing tools give you a second draft.

That is bad for review workflows because:
- you cannot see exactly what changed
- you cannot accept only some edits
- you lose the approval flow people already use in Word
- high-risk content like citations and formulas is easy to damage

RedPen fixes that.

It is designed for **review**, not blind rewrite.

---

## What makes the academic workflow different

RedPen's academic-first workflow is optimized for **English papers** and tries hard to avoid the most dangerous failure modes.

### Protected by default
- citations like `[1]` and `(Author, 2024)`
- inline math / formula-like spans
- figure / table / equation references
- URLs and DOIs
- References / Bibliography section

### Three review modes
| Mode | Best for |
|---|---|
| `proofread` | grammar and clarity only |
| `academic-polish` | pre-submission polishing: grammar, conciseness, terminology, academic tone |
| `reviewer` | stronger reviewer-style critique and comments |

### Trust tools
- `redpen inspect` — document structure + protected content overview
- `redpen check` — lightweight preflight and safety summary
- protection-aware apply path during `review --run`

---

## Golden path

### 1) Inspect the paper
```bash
redpen inspect examples/academic_paper.docx
```

### 2) Optional preflight without calling a model
```bash
redpen review examples/academic_paper.docx --mode academic-polish
```

### 3) Run the full review
```bash
redpen review examples/academic_paper.docx --mode academic-polish --lang zh --run
```

### 4) Optional lightweight safety scan
```bash
redpen check examples/academic_paper.docx --json
```

---

## Artifact model

RedPen produces a standard delivery bundle:

| Artifact | Purpose |
|---|---|
| `*.reviewed.docx` | author / collaborator review in Word |
| `*.reviewed.clean.docx` | clean version with all changes accepted |
| `*.reviewed.report.json` | structured metadata for agents, pipelines, or QA |

The report includes compatibility keys like `mode`, `lang`, `change_count`, and `paragraphs_changed`, plus richer nested sections such as:
- `artifacts`
- `summary`
- `safety`

---

## Showcase

See the flagship demo narrative here:

- [`examples/showcase/README.md`](./examples/showcase/README.md)

It explains the recommended before/after demo flow using the bundled academic sample document.

---

## Install

```bash
git clone https://github.com/onismyh/RedPen.git
cd RedPen
pip install -e .
```

Requires Python 3.10+.

---

## Configuration

Comment language defaults to Chinese (`zh`) via `~/.redpen.toml`.

```toml
[default]
comment_language = "zh"
```

Override per run:

```bash
redpen review paper.docx --lang en --run
```

---

## Commands

| Command | What it does | Example |
|---|---|---|
| `review` | academic review workflow (preflight or full run) | `redpen review paper.docx --mode academic-polish --run` |
| `inspect` | show structure + protected regions | `redpen inspect paper.docx` |
| `check` | lightweight safety scan | `redpen check paper.docx --json` |
| `read` | extract paragraphs as JSON | `redpen read doc.docx` |
| `apply` | write tracked changes from JSON | `redpen apply doc.docx @edits.json -o out.docx` |
| `replace` | find & replace with tracking | `redpen replace doc.docx "old" "new"` |
| `diff` | compare two versions → revisions | `redpen diff v1.docx v2.docx -o diff.docx` |
| `show` | view tracked changes | `redpen show revised.docx` |
| `accept` | accept all changes | `redpen accept revised.docx -o clean.docx` |
| `reject` | reject all changes | `redpen reject revised.docx -o original.docx` |
| `recipe` | generate task-oriented editing scaffolds | `redpen recipe proofread doc.docx --json` |

---

## FAQ

**Do I need an API key?**
Not for RedPen itself. If you use `review --run`, you need a configured model backend such as Claude Code.

**Can I accept only some changes?**
Yes. That is the whole point. Open the reviewed file in Word and Accept / Reject each change.

**Why not just rewrite the whole paper?**
Because review is not generation. A rewritten document hides decisions; a redlined document exposes them.

**Is this only for AI agents?**
No. Humans can use it too. But it is especially useful as a revision layer for Claude Code, Codex, OpenCode, and similar agents.
