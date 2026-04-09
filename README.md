# RedPen

**Make AI edit your Word documents like a human reviewer** — not rewriting entire paragraphs, but marking exactly what to delete, what to insert, and why, using native Word Track Changes.

> [**中文文档 (Chinese README)**](./README_CN.md)

## What is this?

When you use ChatGPT / Claude to polish a document, the AI gives you a completely rewritten version. You have no idea what actually changed.

RedPen is different. It writes AI edits as native **Word Track Changes**:

- ~~old text~~ → **new text** (strikethrough + colored insertion)
- A comment beside each change explaining the reason
- You Accept / Reject each change individually in Word — **you stay in control**

## Who is it for?

RedPen is a **CLI tool for AI agents** — Claude Code, Codex, OpenCode, or any agent harness that can run shell commands. The agent IS the LLM, so no extra API calls needed — it reads the document, decides what to change, and writes revisions through RedPen.

**You don't run commands manually.** Just tell your AI agent "polish this document" and it calls RedPen automatically.

---

## Installation (2 minutes)

### Prerequisites

- **Python 3.10+** ([download](https://www.python.org/downloads/))
- **macOS / Linux / Windows**

### Option A: One-liner

```bash
git clone https://github.com/yourname/redpen.git
cd redpen
bash install.sh
```

### Option B: Manual

```bash
git clone https://github.com/yourname/redpen.git
cd redpen
pip install -e .
```

### Verify

```bash
redpen --help
```

---

## Try it in 30 seconds

No configuration needed:

```bash
# 1. See what's in the sample document
redpen read examples/sample.docx

# 2. Apply pre-made edits as tracked changes
redpen apply examples/sample.docx @examples/edits.json -o output.docx

# 3. Inspect the tracked changes in terminal
redpen show output.docx

# 4. Open output.docx in Word → Review tab → "All Markup"
```

---

## Agent Integration

### How it works

```
redpen read  →  Agent decides  →  redpen apply
  Extract         what to           Write Word
  paragraphs      change            Track Changes
  (JSON)          (agent's own      (docx)
                   intelligence)
```

### Claude Code

```
User: Polish report.docx — fix grammar, improve tone

Claude Code runs:
  1. redpen read report.docx
  2. (analyzes content, decides edits)
  3. redpen apply report.docx @edits.json -o report_revised.docx
  4. "Done — open report_revised.docx and review the changes"
```

### Codex / OpenCode / Any Agent

Same flow — any agent harness with shell access can call RedPen.

---

## Command Reference

### `redpen read` — Extract document text

```bash
redpen read report.docx          # JSON output (default)
redpen read report.docx --plain  # Plain text
```

Output:
```json
[
  {"index": 0, "text": "First paragraph..."},
  {"index": 1, "text": "Second paragraph..."}
]
```

### `redpen apply` — Write tracked changes from JSON

```bash
redpen apply report.docx @edits.json -o revised.docx
redpen apply report.docx @edits.json --no-comment    # skip comments
```

JSON format:
```json
[
  {
    "paragraph_index": 0,
    "changes": [
      {
        "original": "exact text to find",
        "revised": "replacement text",
        "reason": "explanation (written as Word comment)"
      }
    ]
  }
]
```

Three input methods:
```bash
redpen apply doc.docx @edits.json          # from file
echo '[...]' | redpen apply doc.docx       # from stdin
redpen apply doc.docx '[...]'              # inline JSON
```

### `redpen replace` — Find & replace with tracking

```bash
redpen replace contract.docx "Acme Corp" "NewCo Inc" --author "Legal"
```

### `redpen diff` — Compare two versions

```bash
redpen diff v1.docx v2.docx -o changes.docx
```

### `redpen show` — View tracked changes

```bash
redpen show revised.docx          # table format
redpen show revised.docx --json   # JSON format
```

### `redpen accept` / `redpen reject`

```bash
redpen accept revised.docx -o clean.docx      # accept all changes
redpen reject revised.docx -o original.docx    # reject all changes
```

---

## Quick Reference

| Command | What it does | Example |
|---|---|---|
| `read` | Extract paragraphs → JSON | `redpen read doc.docx` |
| `apply` | JSON edits → Word Track Changes | `redpen apply doc.docx @edits.json` |
| `replace` | Find & replace with tracking | `redpen replace doc.docx "old" "new"` |
| `diff` | Compare two versions → revisions | `redpen diff v1.docx v2.docx` |
| `show` | View tracked changes | `redpen show revised.docx` |
| `accept` | Accept all changes | `redpen accept revised.docx` |
| `reject` | Reject all changes | `redpen reject revised.docx` |

---

## Configuration (optional)

Create `~/.redpen.toml`:

```toml
[default]
author = "Claude"
add_comments = true
```

---

## FAQ

**Q: Do I need an OpenAI API key?**
No. RedPen doesn't call any AI API. The AI agent (e.g., Claude Code) decides what to change; RedPen just writes those changes as Word Track Changes.

**Q: Which Word versions are supported?**
Any software that supports .docx: Microsoft Word, WPS, LibreOffice, Google Docs (import).

**Q: I can't see tracked changes in Word?**
Go to Review tab → "Display for Review" dropdown → select "All Markup".

**Q: Can I accept only some changes?**
Yes. Right-click any individual change in Word → Accept or Reject. That's the whole point of RedPen.

---

## Tech Stack

- [docx-revisions](https://github.com/balalofernandez/docx-revisions) — Word revision read/write
- [python-docx](https://python-docx.readthedocs.io/) — Word document manipulation
- [Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/) — CLI framework
