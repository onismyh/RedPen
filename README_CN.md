# RedPen

**别再整篇重写，直接进入红线审阅。**

RedPen 把 AI 的论文润色与审稿建议，写回成 **Word 原生 Track Changes + comments**。
它不是再给你一份“重写稿”，而是给你一份**可以在 Word 里逐条 Accept / Reject 的审阅交付物**。

> [**English README**](./README.md)

---

## 一句话定义

**RedPen 是 AI 和 Word 之间的修订交付层。**

对英文论文来说，它能把 Claude 或其他模型的建议，稳定写回成：
- Word 原生修订痕迹
- comments / 批注理由
- reviewed / clean / report 三件套
- 可审、可控、可回退的审阅流

---

## 30 秒跑通的黄金路径

```bash
redpen review examples/academic_paper.docx --mode academic-polish --lang zh --run
```

你会得到三份标准交付物：
- `academic_paper.reviewed.docx`：带 Track Changes + comments 的审阅版
- `academic_paper.reviewed.clean.docx`：接受全部修改后的干净版
- `academic_paper.reviewed.report.json`：摘要、保护信息、输出路径等结构化报告

然后在 Word 里打开 `.reviewed.docx`：

**审阅 → 所有标记 → 逐条 Accept / Reject**

---

## RedPen 为什么存在

大多数 AI 写作工具会直接给你一份“新稿”。

这对审阅流程是有问题的，因为：
- 你看不清到底改了什么
- 你没法只接受部分修改
- 你失去了 Word 里最自然的审批/审阅流
- 高风险内容（引用、公式、编号）很容易被误伤

RedPen 解决的正是这个问题。

它服务的是：

**审阅，而不是盲目重写。**

---

## 面向英文论文的 academic 工作流

RedPen 现在的主战场是：

**英文论文 → 润色 / 审稿 → 写回 Word 原生修订流**

### 默认保护的高风险内容
- 引用：`[1]`、`(Author, 2024)`
- 公式 / 类公式片段
- Fig. / Table / Eq. 等交叉引用
- URL / DOI
- References / Bibliography 区域

### 三种模式
| 模式 | 适用场景 |
|---|---|
| `proofread` | 轻量语法和清晰度修正 |
| `academic-polish` | 投稿前润色：语法、简洁性、术语、学术语气 |
| `reviewer` | 更像审稿人的评论与建议 |

### trust layer
- `redpen inspect`：看结构、section、保护区域
- `redpen check`：做轻量 preflight 和安全摘要
- `review --run`：走 protection-aware apply

---

## 推荐工作流

### 1）先 inspect
```bash
redpen inspect examples/academic_paper.docx
```

### 2）可选：先看 preflight，不调模型
```bash
redpen review examples/academic_paper.docx --mode academic-polish
```

### 3）真正跑完整 review
```bash
redpen review examples/academic_paper.docx --mode academic-polish --lang zh --run
```

### 4）可选：做轻量安全检查
```bash
redpen check examples/academic_paper.docx --json
```

---

## 三件套交付物

| 文件 | 用途 |
|---|---|
| `*.reviewed.docx` | 给作者 / 导师 / 合作者在 Word 里审 |
| `*.reviewed.clean.docx` | 接受全部修订后的干净版 |
| `*.reviewed.report.json` | 给 agent / pipeline / QA 用的结构化报告 |

`report.json` 里除了兼容字段（如 `mode`、`lang`、`change_count`）外，还会包含更产品化的结构，例如：
- `artifacts`
- `summary`
- `safety`

---

## Showcase

旗舰 demo 叙事见：

- [`examples/showcase/README.md`](./examples/showcase/README.md)

它基于仓库自带的学术论文样例，说明如何演示“不是全文重写，而是 Word 原生审阅交付”。

---

## 安装

```bash
git clone https://github.com/onismyh/RedPen.git
cd RedPen
pip install -e .
```

需要 Python 3.10+。

---

## 配置

comment 语言默认来自 `~/.redpen.toml`：

```toml
[default]
comment_language = "zh"
```

也可以单次覆盖：

```bash
redpen review paper.docx --lang en --run
```

---

## 命令

| 命令 | 做什么 | 示例 |
|---|---|---|
| `review` | 学术论文 review workflow（preflight 或完整运行） | `redpen review paper.docx --mode academic-polish --run` |
| `inspect` | 看结构和受保护区域 | `redpen inspect paper.docx` |
| `check` | 轻量安全检查 | `redpen check paper.docx --json` |
| `read` | 提取段落为 JSON | `redpen read doc.docx` |
| `apply` | 从 JSON 写入修订标记 | `redpen apply doc.docx @edits.json -o out.docx` |
| `replace` | 查找替换 + 修订追踪 | `redpen replace doc.docx "旧" "新"` |
| `diff` | 两版对比 -> 修订文档 | `redpen diff v1.docx v2.docx -o diff.docx` |
| `show` | 查看修订内容 | `redpen show revised.docx` |
| `accept` | 接受全部修订 | `redpen accept revised.docx -o clean.docx` |
| `reject` | 拒绝全部修订 | `redpen reject revised.docx -o original.docx` |
| `recipe` | 生成任务型编辑脚手架 | `redpen recipe proofread doc.docx --json` |

---

## 常见问题

**需要 API Key 吗？**
RedPen 本身不需要；如果你用 `review --run`，需要有可用的模型后端（比如 Claude Code）。

**能只接受部分修改吗？**
可以，这正是 RedPen 的核心价值。打开 reviewed 版，在 Word 里逐条 Accept / Reject 即可。

**为什么不直接全文重写？**
因为审阅不是生成。重写稿隐藏判断过程；红线稿暴露判断过程。

**这只适合 AI Agent 吗？**
不是。人也可以直接用。但它特别适合作为 Claude Code、Codex、OpenCode 等 agent 的文档修订层。
