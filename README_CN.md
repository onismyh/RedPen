# RedPen

**让 AI 像人类审稿人一样改你的 Word 文档** —— 不是整段重写，而是在原文上标记删掉哪里、改成什么、为什么改，你在 Word 里逐条接受或拒绝。

> [**English README**](./README.md)

## 这是什么？

用 ChatGPT / Claude 润色文档，AI 会直接给你一个全新版本，你看不出改了哪里。

RedPen 把 AI 的修改写成 Word 原生的 **Track Changes** —— ~~旧文字~~ → **新文字**，旁边批注说明原因。你在 Word 里逐条 Accept / Reject。

支持 **Claude Code、Codex、OpenCode** 等任何能执行命令的 AI Agent。不需要 API Key。

---

## 安装

### 方式一：让 AI Agent 帮你装

把下面这段话发给 Claude Code / Codex / 任何 Agent：

```
帮我安装 RedPen —— 一个 Word 修订标记 CLI 工具。
执行：git clone https://github.com/yourname/redpen.git ~/redpen && pip install -e ~/redpen
装好后运行 redpen --help 验证。
```

### 方式二：自己装

```bash
git clone https://github.com/yourname/redpen.git
cd redpen
pip install -e .
```

需要 Python 3.10+。

---

## 工作流程

```
redpen read  →  Agent 决定改什么  →  redpen apply
  (JSON)         (Agent 自身智能)      (Word 修订标记)
```

在 Claude Code 中的例子：

```
你: 帮我润色 report.docx，修正语法，优化表达

Claude Code 执行:
  1. redpen read report.docx
  2. （决定修改内容）
  3. redpen apply report.docx @edits.json -o revised.docx
```

打开 `revised.docx` → 审阅 → 所有标记 → 逐条 Accept / Reject。

---

## 命令

| 命令 | 做什么 | 示例 |
|---|---|---|
| `read` | 提取段落为 JSON | `redpen read doc.docx` |
| `apply` | 从 JSON 写入修订标记 | `redpen apply doc.docx @edits.json -o out.docx` |
| `replace` | 查找替换 + 修订追踪 | `redpen replace doc.docx "旧" "新"` |
| `diff` | 两版对比 → 修订文档 | `redpen diff v1.docx v2.docx -o diff.docx` |
| `show` | 查看修订内容 | `redpen show revised.docx` |
| `accept` | 接受全部修订 | `redpen accept revised.docx -o clean.docx` |
| `reject` | 拒绝全部修订 | `redpen reject revised.docx -o original.docx` |

### `apply` 的 JSON 格式

```json
[
  {
    "paragraph_index": 0,
    "changes": [
      { "original": "要找的原文", "revised": "替换内容", "reason": "原因（写入 Word 批注）" }
    ]
  }
]
```

支持 `@文件.json`、stdin 管道、内联 JSON 三种输入方式。

---

## 常见问题

**需要 API Key 吗？** 不需要。AI Agent 决定改什么，RedPen 只负责写成 Word 修订格式。

**看不到修订标记？** Word 中：审阅 → 显示以供审阅 → 选「所有标记」。

**能只接受部分修改吗？** 可以。在 Word 里右键单条修订 → Accept 或 Reject。
