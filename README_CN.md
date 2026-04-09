# RedPen

**让 AI 像人类审稿人一样改你的 Word 文档** —— 不是整段重写，而是在原文上标记「删掉哪里、改成什么、为什么改」，你在 Word 里逐条决定接受还是拒绝。

> [**English README**](./README.md)

## 这是什么？

你用 ChatGPT / Claude 润色文档时，AI 会直接给你一个全新版本，你根本看不出改了哪里。

RedPen 不一样。它把 AI 的修改写成 Word 原生的 **Track Changes（修订模式）**：

- ~~旧文字~~ → **新文字**（删除线 + 彩色插入）
- 每处修改旁边有批注，解释为什么改
- 你在 Word 里逐条 Accept / Reject，**你做主**

## 谁在用？

RedPen 是给 **AI Agent**（Claude Code、Codex、OpenCode 等）用的工具。Agent 自己就是大语言模型，不需要再调 API —— 它读文档、决定怎么改、然后通过 RedPen 写入 Word 修订标记。

**你不需要手动运行命令。** 你只要对 AI Agent 说「帮我润色这个文档」，Agent 会自动调用 RedPen。

---

## 安装（2 分钟）

### 前提条件

- **Python 3.10+**（[下载地址](https://www.python.org/downloads/)）
- **macOS / Linux / Windows** 均可

### 方式一：一键安装（推荐）

```bash
git clone https://github.com/yourname/redpen.git
cd redpen
bash install.sh
```

### 方式二：手动安装

```bash
git clone https://github.com/yourname/redpen.git
cd redpen
pip install -e .
```

### 验证安装

```bash
redpen --help
```

看到命令列表就说明成功了。

---

## 30 秒体验

安装后立刻试试，不需要任何配置：

```bash
# 1. 看看示例文档里写了什么
redpen read examples/sample.docx

# 2. 用预置的修改方案生成带修订标记的文档
redpen apply examples/sample.docx @examples/edits.json -o output.docx

# 3. 在终端查看修订内容
redpen show output.docx

# 4. 用 Word 打开 output.docx，在「审阅」标签看修订
```

> **Word 查看修订**：打开文档 → 点击「审阅」标签 → 将「显示以供审阅」下拉框切换为「所有标记 (All Markup)」

---

## 在 AI Agent 中使用

### 工作流程

```
redpen read  →  Agent 决策  →  redpen apply
  读取段落         AI 判断         写入修订标记
  (JSON)         要改什么         (Word Track Changes)
```

### Claude Code

```
你: 帮我润色 report.docx，修正语法错误，优化表达

Claude Code 自动执行:
  1. redpen read report.docx          ← 读取文档内容
  2. （Claude 自己分析并决定修改）
  3. redpen apply report.docx @edits.json -o report_revised.docx
  4. 告诉你：输出在 report_revised.docx，请打开审阅
```

### Codex / OpenCode

同理 —— 任何能执行 shell 命令的 AI Agent 都能用。

---

## 命令参考

### `redpen read` — 读取文档

```bash
redpen read report.docx          # 输出 JSON（默认）
redpen read report.docx --plain  # 纯文本
```

输出：
```json
[
  {"index": 0, "text": "第一段内容..."},
  {"index": 1, "text": "第二段内容..."}
]
```

### `redpen apply` — 写入修订标记

```bash
redpen apply report.docx @edits.json -o revised.docx
redpen apply report.docx @edits.json --no-comment   # 不加批注
```

edits.json 格式：
```json
[
  {
    "paragraph_index": 0,
    "changes": [
      {
        "original": "原文中的一段话",
        "revised": "修改后的内容",
        "reason": "修改原因（会写入 Word 批注）"
      }
    ]
  }
]
```

三种输入方式：
```bash
redpen apply doc.docx @edits.json          # 从文件读取
echo '[...]' | redpen apply doc.docx       # 从管道输入
redpen apply doc.docx '[...]'              # 内联 JSON
```

### `redpen replace` — 查找替换

```bash
redpen replace contract.docx "甲方" "乙方" --author "Legal"
```

### `redpen diff` — 对比两版文档

```bash
redpen diff v1.docx v2.docx -o changes.docx
```

### `redpen show` — 查看修订

```bash
redpen show revised.docx          # 表格形式
redpen show revised.docx --json   # JSON 形式
```

### `redpen accept` / `redpen reject`

```bash
redpen accept revised.docx -o clean.docx      # 接受全部修订
redpen reject revised.docx -o original.docx    # 拒绝全部修订
```

---

## 命令速查表

| 命令 | 做什么 | 示例 |
|---|---|---|
| `read` | 提取文档段落 → JSON | `redpen read doc.docx` |
| `apply` | JSON 修改 → Word 修订标记 | `redpen apply doc.docx @edits.json` |
| `replace` | 查找替换 + 修订追踪 | `redpen replace doc.docx "旧" "新"` |
| `diff` | 两版对比 → 修订文档 | `redpen diff v1.docx v2.docx` |
| `show` | 查看修订内容 | `redpen show revised.docx` |
| `accept` | 接受全部修订 | `redpen accept revised.docx` |
| `reject` | 拒绝全部修订 | `redpen reject revised.docx` |

---

## 可选配置

创建 `~/.redpen.toml`：

```toml
[default]
author = "Claude"       # 修订作者名
add_comments = true     # 是否默认添加批注
```

---

## 常见问题

**Q: 需要 OpenAI API Key 吗？**
不需要。RedPen 本身不调用任何 AI API。AI Agent（如 Claude Code）自己决定怎么改，RedPen 只负责把修改写成 Word 格式。

**Q: 支持哪些 Word 版本？**
所有支持 .docx 格式的软件：Microsoft Word、WPS、LibreOffice、Google Docs（导入 docx）。

**Q: 打开文档看不到修订标记？**
在 Word 中：审阅 → 显示以供审阅 → 选择「所有标记 (All Markup)」。

**Q: 可以只接受部分修改吗？**
可以。在 Word 中右键单条修订 → Accept 或 Reject。这正是 RedPen 的核心优势。

---

## 技术栈

- [docx-revisions](https://github.com/balalofernandez/docx-revisions) — Word 修订读写
- [python-docx](https://python-docx.readthedocs.io/) — Word 文档操作
- [Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/) — CLI 框架
