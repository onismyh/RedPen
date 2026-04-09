# RedPen

**Make AI edit your Word documents like a human reviewer** — not rewriting entire paragraphs, but marking exactly what to delete, what to insert, and why, using native Word Track Changes.

> [**中文文档 (Chinese README)**](./README_CN.md)

## What is this?

When you use ChatGPT / Claude to polish a document, the AI gives you a completely rewritten version. You have no idea what actually changed.

RedPen writes AI edits as native **Word Track Changes** — ~~old text~~ → **new text**, with comments explaining each change. You Accept / Reject individually in Word.

Works with **Claude Code, Codex, OpenCode**, or any AI agent that can run shell commands. No API key needed.

---

## Installation

### Option A: Tell your AI agent to install it

Paste this to Claude Code / Codex / any agent:

```
Install RedPen — a Word track changes CLI tool.
Run: git clone https://github.com/yourname/redpen.git ~/redpen && pip install -e ~/redpen
Then use `redpen --help` to verify.
```

### Option B: Install yourself

```bash
git clone https://github.com/yourname/redpen.git
cd redpen
pip install -e .
```

Requires Python 3.10+.

---

## How it works

```
redpen read  →  Agent decides what to change  →  redpen apply
  (JSON)         (agent's own intelligence)       (Word Track Changes)
```

Example in Claude Code:

```
User: Polish report.docx — fix grammar, improve tone

Claude Code runs:
  1. redpen read report.docx
  2. (decides edits)
  3. redpen apply report.docx @edits.json -o revised.docx
```

Open `revised.docx` in Word → Review → All Markup → Accept / Reject each change.

---

## Commands

| Command | What it does | Example |
|---|---|---|
| `read` | Extract paragraphs as JSON | `redpen read doc.docx` |
| `apply` | Write tracked changes from JSON | `redpen apply doc.docx @edits.json -o out.docx` |
| `replace` | Find & replace with tracking | `redpen replace doc.docx "old" "new"` |
| `diff` | Compare two versions → revisions | `redpen diff v1.docx v2.docx -o diff.docx` |
| `show` | View tracked changes | `redpen show revised.docx` |
| `accept` | Accept all changes | `redpen accept revised.docx -o clean.docx` |
| `reject` | Reject all changes | `redpen reject revised.docx -o original.docx` |

### `apply` JSON format

```json
[
  {
    "paragraph_index": 0,
    "changes": [
      { "original": "text to find", "revised": "replacement", "reason": "written as Word comment" }
    ]
  }
]
```

Accepts `@file.json`, stdin pipe, or inline JSON string.

---

## FAQ

**Do I need an API key?** No. The AI agent decides what to change; RedPen just writes it as Word Track Changes.

**Can't see tracked changes in Word?** Review tab → Display for Review → "All Markup".

**Can I accept only some changes?** Yes — right-click any change in Word → Accept or Reject.
