# RedPen 下一档产品改造方案

> For Hermes: Use subagent-driven-development skill to implement this plan task-by-task.

目标：把 RedPen 从“有 sense 的 CLI 工具”升级为“AI 文档审阅工作流的标准接口层”。

架构思路：不改变 RedPen 的核心哲学——保留 Word Track Changes 作为最终呈现层；升级的重点不是把它做成另一个写作 AI，而是补齐 4 个缺口：可信性、易用性、可传播性、可扩展性。

技术栈：Python 3.10+, Typer, python-docx, docx-revisions, lxml, Rich

---

## 一、先给结论：RedPen 要升一个档次，应该怎么改

RedPen 现在最强的地方是：
1. 核心洞察对
2. CLI 边界清楚
3. 技术选型服务于用户已有习惯（Word Track Changes）

RedPen 现在最弱的地方是：
1. 缺少“第一眼就懂”的产品展示
2. 缺少“普通人也能用”的任务入口
3. 缺少“可以信任它改不坏文档”的质量体系
4. 缺少“逐步变成基础设施”的协议层设计

所以升级方向不是加很多功能，而是做 4 件事：
- 把 demo 做炸裂
- 把常见任务做成 recipe/workflow
- 把质量保障做厚
- 把 JSON edit schema 做成稳定协议

一句话版本：
“保留 CLI 的锋利感，但把它包装成一个能被 agent、研究者、律师、学生、编辑真正反复使用的文档修订基础设施。”

---

## 二、产品升级目标

### 目标 1：从“能用”升级到“让人敢用”
用户最大的隐性担忧不是不会用，而是：
- 会不会改坏 Word 文档？
- 会不会丢格式？
- 会不会 comment 锚错地方？
- 多轮修改会不会乱？

所以第一优先级是可靠性叙事 + 自动化验证。

### 目标 2：从“工程师工具”升级到“任务工具”
今天 RedPen 是命令驱动：
- read
- apply
- diff

下一步应该变成任务驱动：
- polish grammar
- tighten writing
- reviewer mode
- legal redline
- bilingual revision

不是替代底层命令，而是在上面加一层 workflow/recipe。

### 目标 3：从“单次使用”升级到“工作流组件”
未来真正有价值的不是单个命令，而是：
- AI Agent 可调用的稳定 JSON schema
- 多轮修订可持续迭代
- 企业/团队可嵌入现有文档流程

---

## 三、产品路线图（按优先级）

### Phase 1：把产品讲清楚、演示清楚、安装顺滑
目标：提高第一眼转化率

应做内容：
1. README 首屏重写
2. 增加 before/after 文档截图
3. 增加 15 秒 GIF 演示
4. 增加“3 个真实场景”入口
5. 增加一键安装与 smoke test

用户应该在 20 秒内明白：
“它不是重写工具，而是 AI 审稿写回 Word 的工具。”

### Phase 2：把常见需求变成 recipe
目标：让用户不需要自己拼 JSON

新增：
- `redpen recipe proofread`
- `redpen recipe tighten`
- `redpen recipe academic`
- `redpen recipe reviewer`
- `redpen recipe bilingual`

说明：
这些 recipe 初期可以只是生成 JSON 模板 / prompt scaffold，不需要内置模型。

### Phase 3：补齐质量基础设施
目标：让 RedPen 成为“可信工具”而不是“巧妙脚本”

新增：
- tests/
- fixtures/
- golden docs
- round-trip validation
- 多轮修订回归测试
- 格式保留测试

### Phase 4：把 edit JSON 升级为协议
目标：让 RedPen 成为 agent ecosystem 的标准接口层

当前 schema 太轻：
- paragraph_index
- changes[{original, revised, reason}]

建议升级为 versioned schema：
- schema_version
- document_id
- edit_intent
- anchor strategy
- paragraph selector
- confidence
- reason
- labels
- metadata

这样以后可以接：
- Claude Code
- Codex
- OpenCode
- OfficeCLI
- 内部审稿机器人

---

## 四、建议新增的产品层能力

### 1. “体验层”升级

#### 1.1 增加 examples/showcase
建议新增：
- `examples/showcase/academic-before.docx`
- `examples/showcase/academic-after.docx`
- `examples/showcase/legal-before.docx`
- `examples/showcase/legal-after.docx`
- `examples/showcase/bilingual-before.docx`
- `examples/showcase/bilingual-after.docx`

目标：让用户看到真实价值，而不是只看命令。

#### 1.2 README 信息结构重写
建议 README 首屏改成：
1. 一句话价值主张
2. 10 秒演示图
3. 三种用户场景
4. 最短可运行示例
5. 为什么不是“直接让 AI 重写全文”

建议 tagline 候选：
- RedPen: AI edits, written back as real Word Track Changes.
- RedPen: Let AI revise docs the way humans review them.
- RedPen: Stop rewriting. Start redlining.

其中最锋利的是：
Stop rewriting. Start redlining.

### 2. “产品入口层”升级

#### 2.1 新增 recipe 子命令
建议文件：
- Create: `redpen/recipes.py`
- Modify: `redpen/cli.py`

命令形态：
- `redpen recipe proofread input.docx`
- `redpen recipe reviewer input.docx --audience journal`
- `redpen recipe bilingual input.docx --from zh --to en`

第一阶段不必自动调用模型，可以输出：
- 推荐 prompt
- JSON skeleton
- 推荐 author/comment style

这样能显著降低使用门槛。

#### 2.2 新增 inspect/check 命令
建议文件：
- Create: `redpen/validator.py`
- Modify: `redpen/cli.py`

命令：
- `redpen inspect file.docx`
- `redpen check file.docx`

输出：
- 是否含 tracked changes
- comment 数量
- paragraph 数量
- 是否可能存在 broken anchor
- 是否存在空修订

### 3. “可靠性层”升级

#### 3.1 建立 tests 目录
建议新增：
- Create: `tests/test_read.py`
- Create: `tests/test_apply.py`
- Create: `tests/test_replace.py`
- Create: `tests/test_diff.py`
- Create: `tests/test_comments.py`
- Create: `tests/test_format_preservation.py`
- Create: `tests/test_multi_round_revisions.py`
- Create: `tests/fixtures/`

最先要测的不是“功能有没有”，而是：
- 修改后文档还能不能被 Word 正常打开
- 格式有没有丢
- 多轮修订能否继续 read/apply
- comment 是否落在正确段落

#### 3.2 加 golden files
建议新增：
- `tests/golden/expected_show_output.txt`
- `tests/golden/expected_read_meta.json`
- `tests/golden/expected_diff_summary.json`

#### 3.3 增加 CLI smoke tests
至少覆盖：
- install 后 `redpen --help`
- `read` on sample.docx
- `apply` on sample.docx
- `diff` on two examples
- `show` output readable

### 4. “协议层”升级

#### 4.1 JSON schema versioning
建议新增：
- Create: `redpen/schema.py`
- Create: `docs/schema/redpen-edit-schema-v1.md`

建议 v1 schema：
```json
{
  "schema_version": "1.0",
  "document": {
    "path": "report.docx"
  },
  "edits": [
    {
      "paragraph_index": 3,
      "intent": "tighten",
      "changes": [
        {
          "original": "in order to",
          "revised": "to",
          "reason": "make sentence more concise",
          "confidence": 0.94,
          "labels": ["conciseness"]
        }
      ]
    }
  ]
}
```

#### 4.2 锚点策略升级
当前高度依赖 paragraph_index + original text。
后面应增加：
- paragraph hash
- text window anchor
- style hint
- fallback mode

否则复杂文档、多轮修订、跨段替换会越来越脆弱。

---

## 五、最值得优先做的 5 个“升级动作”

### 动作 A：把 README 改成产品页
价值：最高
成本：低

改动文件：
- Modify: `README.md`
- Modify: `README_CN.md`
- Create: `assets/redpen-demo.gif`
- Create: `assets/redpen-before-after.png`

完成标准：
- 首屏一张图就能说明价值
- 新用户 30 秒能完成 mental model 建立

### 动作 B：新增 recipe 层
价值：很高
成本：中

改动文件：
- Create: `redpen/recipes.py`
- Modify: `redpen/cli.py`
- Create: `examples/recipes/`

完成标准：
- 用户不需要自己从 0 写 edits.json
- 可以直接从 task 名称出发

### 动作 C：补测试体系
价值：极高
成本：中高

改动文件：
- Create: `tests/`
- Modify: `pyproject.toml`

完成标准：
- 关键命令有回归测试
- 多轮修订不崩
- format preservation 有明确保障

### 动作 D：提供“可信输出检查”
价值：高
成本：中

改动文件：
- Create: `redpen/validator.py`
- Modify: `redpen/cli.py`

完成标准：
- 用户在 apply/diff 后可立刻验证文档健康度
- 增强“敢用”心智

### 动作 E：把 schema 文档化
价值：中高
成本：低

改动文件：
- Create: `redpen/schema.py`
- Create: `docs/schema/redpen-edit-schema-v1.md`

完成标准：
- 外部 agent 可稳定集成
- RedPen 从工具向协议演化

---

## 六、具体实施计划

### Task 1: 建立文档规划目录

目标：为产品升级文档、schema、showcase 留出结构

文件：
- Create: `docs/schema/`
- Create: `docs/showcase/`
- Create: `examples/showcase/`
- Create: `examples/recipes/`

步骤：
1. 创建目录结构
2. 在每个目录放 README 占位说明
3. 提交

建议提交信息：
`docs: scaffold product upgrade directories`

### Task 2: 重写 README 首屏信息架构

目标：让 RedPen 的价值主张更锋利、更可传播

文件：
- Modify: `README.md`
- Modify: `README_CN.md`

改动要点：
1. 用一句话主张开场
2. 加入 before/after 说明图位置
3. 增加“Why not just rewrite the whole doc?”小节
4. 增加“Best for”场景
5. 增加“3-minute quickstart”

建议增加的小节：
- Who this is for
- Three real workflows
- Why Track Changes matters

建议提交信息：
`docs: sharpen positioning and onboarding`

### Task 3: 新增 recipe 层骨架

目标：把命令入口从底层能力提升为任务入口

文件：
- Create: `redpen/recipes.py`
- Modify: `redpen/cli.py`

最小实现：
- `redpen recipe proofread`
- `redpen recipe tighten`
- `redpen recipe reviewer`

第一版行为：
- 输出推荐 prompt
- 输出 edits.json skeleton
- 提示后续 apply 命令

建议提交信息：
`feat: add recipe scaffolds for common revision workflows`

### Task 4: 为 recipe 加示例文件

目标：增强可模仿性

文件：
- Create: `examples/recipes/proofread.json`
- Create: `examples/recipes/tighten.json`
- Create: `examples/recipes/reviewer.json`
- Create: `examples/recipes/README.md`

建议提交信息：
`docs: add recipe examples for common editing tasks`

### Task 5: 建立测试基础设施

目标：从“看起来聪明”升级为“可以信任”

文件：
- Modify: `pyproject.toml`
- Create: `tests/conftest.py`
- Create: `tests/test_read.py`
- Create: `tests/test_apply.py`
- Create: `tests/test_diff.py`
- Create: `tests/test_comments.py`

测试框架建议：
- pytest
- fixture docx files in `tests/fixtures/`

建议提交信息：
`test: add baseline regression suite for core commands`

### Task 6: 为格式保留建立专项测试

目标：把 RedPen 最关键的优势产品化

文件：
- Create: `tests/test_format_preservation.py`
- Create: `tests/fixtures/formatted_sample.docx`

验证内容：
- bold/italic/color/font 保留
- comment 不破坏原段落结构
- replace 后风格仍可接受

建议提交信息：
`test: add format preservation regression coverage`

### Task 7: 新增 inspect/check 命令

目标：让用户在写回文档后更安心

文件：
- Create: `redpen/validator.py`
- Modify: `redpen/cli.py`

第一版可输出：
- tracked changes count
- comments count
- paragraph count
- whether document contains existing revisions
- basic consistency warnings

建议提交信息：
`feat: add document inspection and validation command`

### Task 8: 定义 schema v1

目标：把 RedPen 变成 agent-friendly protocol

文件：
- Create: `redpen/schema.py`
- Create: `docs/schema/redpen-edit-schema-v1.md`

第一版要求：
- 支持 schema_version
- 支持 confidence / labels / intent
- 保持向后兼容当前 edits.json

建议提交信息：
`feat: introduce versioned edit schema v1`

### Task 9: 支持向后兼容解析

目标：升级 schema 时不破坏现有用户

文件：
- Modify: `redpen/cli.py`
- Modify: `redpen/revision_writer.py`

要求：
- 旧格式继续可用
- 新格式自动识别
- 错误提示要清楚

建议提交信息：
`feat: support backward-compatible edit schema parsing`

### Task 10: 增加 showcase 样例

目标：让用户立刻看见价值，而不是读说明书

文件：
- Create: `examples/showcase/README.md`
- Create: `examples/showcase/academic-notes.md`
- Create: `examples/showcase/legal-notes.md`
- Create: `examples/showcase/bilingual-notes.md`

注意：
如果暂时不方便放真实 docx，可先用 markdown 说明场景，后续再补实物样例。

建议提交信息：
`docs: add showcase scenarios for real-world revision use`

---

## 七、产品表达升级建议

### 新的一句话定义
建议主定义：
RedPen lets AI edit Word documents the way humans review them.

备用：
RedPen writes AI edits back as real Word Track Changes.

中文主定义建议：
让 AI 像人类审稿人一样改 Word，而不是重写一整篇。

### 官网/README 首屏文案建议
Instead of this:
- “AI rewrote your whole document.”

You get this:
- “Word Track Changes, comments, accept/reject, paragraph by paragraph.”

### 三个高转化场景
1. 学术论文润色
2. 合同与正式文档修订
3. 中英双语文档校改

---

## 八、不建议现在做的事

1. 不要急着做 Web App
原因：会稀释 CLI 的锋利定位，也会让工程复杂度突然上升。

2. 不要急着接内置模型
原因：RedPen 的价值在“写回与审阅层”，不是模型层。

3. 不要做太多文档格式
原因：现在聚焦 .docx 是正确的。PDF、Google Docs、Pages 都会分散精力。

4. 不要做“万能编辑助手”
原因：那会把产品从锋利工具变成普通 AI 套壳。

---

## 九、最终建议

如果只能做 3 件事，我建议顺序是：
1. 重写 README + 演示资产
2. 加 recipe 层
3. 加测试体系

如果做完这 3 件事，RedPen 就会从：
- “聪明的小工具”
变成：
- “一个可信、好讲、好用、值得传播的 AI 文档审阅工具”

如果再做 schema v1 + inspect/check，RedPen 就开始像：
- “AI 文档修订基础设施”

---

## 十、交付判断标准

升级完成后，应该达到这几个结果：

1. 新用户 30 秒理解价值
2. Agent 用户 3 分钟跑通完整流程
3. 普通用户不需要手写 JSON 也能开始
4. 核心命令有回归测试
5. 多轮修订与格式保留有明确保障
6. 外部工具能基于 schema 接入

达到这几点，RedPen 就算真正提升了一个档次。
