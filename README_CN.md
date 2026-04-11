# RedPen

**别再整篇重写，直接进入红线审阅。**

RedPen 让 AI 像人类审稿人一样修改 Word：直接写入原生 Track Changes、批注和逐条 Accept / Reject 审阅流程。

> [**English README**](./README.md)

## RedPen 解决什么问题

大多数 AI 写作工具会直接给你一份“重写后的新文档”。

这对审阅流程并不好，因为：
- 你看不清到底改了什么
- 你不能只接受其中一部分修改
- 你失去了 Word 里最自然的审阅流程

RedPen 做的不是“再生成一版”，而是把修改写回 Word 原文：
- 删除什么
- 插入什么
- 为什么改（批注）
- 最终由你在 Word 中逐条 Accept / Reject

## 适合谁

RedPen 适合希望“保留审阅控制权”的用户。

典型场景：
- 学术论文润色
- 合同、公文、制度文件修订
- 中英双语文档校改
- 汇报材料精修
- AI Agent 文档审阅流水线

## 10 秒理解它

```text
redpen read   -> agent 决定修改 -> redpen apply
  JSON            你的 AI / 审稿人      Word 修订 + 批注
```

打开输出文档后，在 Word 中：
审阅 -> 所有标记 -> 逐条 Accept / Reject。

## 为什么不直接让 AI 重写全文？

因为“生成”和“审阅”不是一回事。

重写后的文档隐藏了判断过程。
带修订的文档暴露了判断过程。

RedPen 是为后者设计的。

## 快速开始

### 安装

```bash
git clone https://github.com/onismyh/RedPen.git
cd RedPen
pip install -e .
```

需要 Python 3.10+。

### 3 分钟跑通流程

1. 先把 Word 文档读成结构化文本：

```bash
redpen read report.docx
```

2. 让 AI 决定修改内容，或者先用 recipe 生成脚手架：

```bash
redpen recipe proofread report.docx --json > proofread.json
```

3. 把修订写回 Word：

```bash
redpen apply report.docx @proofread.json -o revised.docx
```

4. 查看修订内容：

```bash
redpen show revised.docx
```

## 三个典型工作流

### 1. 文档校对 / 润色

```bash
redpen recipe proofread report.docx --json > edits.json
redpen apply report.docx @edits.json -o report-reviewed.docx
```

适合修正语法、措辞和轻量表达问题，同时保持原意。

### 2. 精简汇报材料

```bash
redpen recipe tighten memo.docx --json > edits.json
redpen apply memo.docx @edits.json -o memo-tightened.docx
```

适合去掉冗余、让表达更简洁有力。

### 3. 审稿人模式

```bash
redpen recipe reviewer draft.docx
```

适合协同编辑：作者后续在 Word 中逐条 Accept / Reject。

## 命令

| 命令 | 做什么 | 示例 |
|---|---|---|
| `read` | 提取段落为 JSON | `redpen read doc.docx` |
| `apply` | 从 JSON 写入修订标记 | `redpen apply doc.docx @edits.json -o out.docx` |
| `replace` | 查找替换 + 修订追踪 | `redpen replace doc.docx "旧" "新"` |
| `diff` | 两版对比 -> 修订文档 | `redpen diff v1.docx v2.docx -o diff.docx` |
| `show` | 查看修订内容 | `redpen show revised.docx` |
| `accept` | 接受全部修订 | `redpen accept revised.docx -o clean.docx` |
| `reject` | 拒绝全部修订 | `redpen reject revised.docx -o original.docx` |
| `recipe` | 生成任务型编辑脚手架 | `redpen recipe proofread doc.docx --json` |

## `apply` 的 JSON 格式

```json
[
  {
    "paragraph_index": 0,
    "changes": [
      {
        "original": "要找的原文",
        "revised": "替换内容",
        "reason": "会写入 Word 批注"
      }
    ]
  }
]
```

支持：
- `@file.json`
- stdin 管道
- 内联 JSON 字符串

## 常见问题

**需要 API Key 吗？**
不需要。AI Agent 负责决定改什么，RedPen 只负责把这些修改写回 Word 修订格式。

**能只接受部分修改吗？**
可以。在 Word 里右键任意一条修订 -> Accept 或 Reject。

**看不到修订标记？**
Word 中：审阅 -> 显示以供审阅 -> 所有标记。

**这只适合 AI Agent 吗？**
不是。人也可以直接用。但它特别适合作为 Claude Code、Codex、OpenCode 等 Agent 的文档修订层。
