# RedPen 第二阶段：极致产品 Taste 计划

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 把 RedPen 从“已经跑通的 academic review CLI”升级成一个**极致克制、极度可信、默认正确、能被一眼看懂价值**的产品。

**Product Definition:** RedPen 不是帮用户重写论文，而是把 AI 的学术润色与审稿建议，**安全写回 Word 原生 Track Changes + comments** 的审阅交付层。

**Architecture:** 第二阶段不做横向功能膨胀，不急着做大而全平台。核心策略是三件事：
1. 把主场景压缩到极致：**英文论文审阅/润色写回 Word**
2. 把信任系统做厚：**高风险内容默认保护 + 结果可解释 + 输出可验证**
3. 把产品入口与包装做对：**用户看到的是任务与结果，不是命令和实现细节**

**Lenses:**
- **Steve Jobs:** 极致聚焦、默认最优、第一眼就懂、demo 先赢
- **张一鸣:** 信息结构清晰、决策成本低、可传播、可复用、可规模化
- **Elon Musk:** 第一性原理、系统可靠性、验证闭环、技术壁垒

**Non-goals（这一阶段明确不做）:**
- 不做通用 AI 写作平台
- 不做 web 编辑器 / 在线协作产品
- 不扩成太多文档垂类入口
- 不增加一堆 mode 让用户选择困难

---

## 一、当前产品判断

RedPen 第一阶段已经完成了一件很重要的事：

> 它证明了 AI 建议可以不是“另存一份重写稿”，而是**写回到 Word 原生审阅流**。

这是产品最有价值的洞察，也是接下来所有工作的中心。

### 已经成立的部分
- academic review / polish / reviewer 三模式成立
- Claude 真调用成立
- reviewed / clean / report 三件套成立
- references / citations / formulas / Fig/Table/Eq refs 保护方向成立
- inspect / check / protection-aware apply 开始形成 trust layer

### 还不够顶级的部分
- 用户第一眼看到的仍像“工程工具”，不是“产品”
- 主路径还不够无脑，理解成本仍偏高
- 信任资产还不够厚，离“敢交给重要论文”还差一层
- 输出虽然齐，但包装还不够像交付物
- 协议层潜力存在，但对外呈现仍像功能集合

一句话：

**第一阶段证明了“可行”，第二阶段要证明“值得依赖，值得传播，值得接入”。**

---

## 二、极致产品 Taste 的核心原则

### 原则 1：极致聚焦
这一阶段只打一个主场景：

**英文论文 → 学术润色/审稿 → 原生 Word 修订交付**

其他场景（法律、政策、双语、企业报告）不是现在的主叙事。

### 原则 2：默认正确
用户不应该先研究参数，才获得正确结果。

理想状态：

```bash
redpen review paper.docx
```

默认就能：
- 自动使用学术场景最佳策略
- 默认保护高风险内容
- 默认输出 reviewed / clean / report
- 默认给出清晰 summary
- 默认是最推荐的路径

### 原则 3：信任先于聪明
对 RedPen 而言，用户不是在买“会不会润色”，而是在买：
- 会不会误伤引用
- 会不会破坏公式/编号
- 会不会把 comment 挂错位置
- 会不会让我还能逐条 Accept / Reject

所以产品核心不是“更能写”，而是：

**更可控、更可审、更可回退。**

### 原则 4：结果先于过程
用户首先应该看到：
- 一个可直接打开审的 Word 修订稿
- 一个 clean 交付稿
- 一个清楚的变更摘要

而不是先看到内部命令、JSON 结构、模式细节。

### 原则 5：少即是多
第二阶段不追求 mode 数量，不追求配置数量，不追求场景数量。

要追求的是：
- 更少选择
- 更强默认值
- 更稳结果
- 更清晰品牌

---

## 三、三位创始人视角下的产品要求

## 3.1 Steve Jobs 视角：做出“第一眼就想用”的产品

### Jobs 会要求什么
1. 主场景必须一刀切开，不许模糊
2. 第一次体验必须立刻理解价值
3. 功能不是越多越好，而是默认路径越顺越好
4. demo 必须炸裂，最好 30 秒内完成认知转化

### Jobs 对 RedPen 的结论
RedPen 最值钱的，不是“AI 会改论文”，而是：

**它让 AI 以人类熟悉、组织可接受、Word 原生支持的方式参与审阅。**

### 对应产品动作
- 把对外叙事压缩成一个句子
- 把 README/首页/演示全部围绕一个主场景重写
- 把用户入口从命令集合变成“任务选择”
- 让 demo 成为传播资产，而不是附属说明

---

## 3.2 张一鸣视角：做出“低理解成本、高传播效率”的产品

### 张一鸣会要求什么
1. 信息结构必须非常清楚
2. 用户决策成本必须极低
3. 输出必须可以规模复用与嵌入
4. 数据结构要支持反馈与迭代

### 张一鸣对 RedPen 的结论
RedPen 不该只是一套 CLI，而应该逐渐长成：

**AI 审阅输出 → Word 审阅交付的标准层。**

### 对应产品动作
- 把三种 mode 产品化命名与解释清楚
- 把 report 从工程输出变成“可读 summary + 可机器接入”双层结构
- 把 schema 升级成 versioned protocol
- 把“结果文件”做成标准包装与增长载体

---

## 3.3 Elon Musk 视角：做出“系统级可靠”的基础设施

### Musk 会要求什么
1. 核心约束要被明确定义
2. 风险点要有系统级保护，而不是文档级承诺
3. 所有关键路径要可验证
4. 产品壁垒来自 reliability + validation，而不是 prompt 巧思

### Musk 对 RedPen 的结论
真正的难点不在“生成建议”，而在：

**把不稳定的 LLM 输出变成稳定、可审计、可回滚、兼容 Word 生态的 revision actions。**

### 对应产品动作
- 做强 preflight / validation / apply-time checks
- 建 golden docs benchmark
- 做多轮稳定性与 round-trip 回归
- 建 failure taxonomy 与 deterministic report

---

## 四、第二阶段总主题

# RedPen 2.0 = Trusted Academic Revision Infrastructure

翻成产品语言就是：

**让用户在不放弃 Word 审阅习惯的前提下，放心地把英文论文交给 AI 做润色与审稿修订。**

---

## 五、下一阶段的 P0 / P1 / P2 路线图

## P0：一定先做（决定产品是否真正升级）

### P0-1. 重做默认主路径
**目标：** 让第一次使用几乎不需要学习。

#### 产品要求
- 默认命令就是黄金路径
- 不要求用户先理解 inspect/check/report/clean 的差异
- 没配参数也能跑出最佳默认结果

#### 目标体验
```bash
redpen review paper.docx
```

得到：
- `paper.reviewed.docx`
- `paper.reviewed.clean.docx`
- `paper.reviewed.report.json`
- 一段清楚的人类可读摘要

#### 设计动作
- 收敛默认 mode
- 自动学术场景策略
- 默认 zh comments（保留 en 可选）
- 默认启用保护与检查
- 出错时给人能看懂的原因与下一步动作

#### 验收标准
- 新用户 30 秒内能理解如何使用
- README 首个示例只有一条命令
- 不看实现细节也能完成一次端到端体验

---

### P0-2. 把信任系统做成产品一层，而不是技术细节
**目标：** 从“能用”升级为“敢用”。

#### 产品要求
用户在运行前后都知道：
- 哪些内容会被保护
- 哪些内容不会被改
- 哪些修改被阻止了
- 哪些区域风险较高

#### 设计动作
- 强化 `inspect` 与 `check` 的输出语义
- 在 report 中增加：
  - protected_zones_summary
  - risky_edit_attempts
  - skipped_sections
  - warnings
  - health_status
- 在 CLI 输出中增加“本次保护了什么”的可读摘要

#### 验收标准
- 用户能明确感知“References / citations / formulas / refs 受保护”
- report 不再只是技术 JSON，而是兼顾可读与可接入
- README 中“为什么比全文重写更可信”表达清楚

---

### P0-3. 做一个旗舰 demo，而不是更多功能
**目标：** 用最短时间让人理解 RedPen 的价值。

#### Demo 脚本
1. 放入一篇英文论文 `.docx`
2. inspect 显示识别到 Abstract / Methods / Results / Discussion / References
3. 标出保护内容：引用、公式、图表编号、DOI、URL
4. 跑 `redpen review paper.docx`
5. 产出 reviewed / clean / report 三件套
6. 打开 Word 展示 Track Changes + 中文 comments
7. 最后展示 clean 版与摘要报告

#### 需要的交付物
- 一份专门的 showcase 样例论文
- before / after 截图
- 30~60 秒 GIF 或视频
- README 首屏嵌入
- 一句极强的 slogan

#### 推荐 slogan 候选
- **Stop rewriting. Start redlining.**
- AI review, native to Word.
- Turn model suggestions into Word revisions.

#### 验收标准
- 第一次看到 demo 的人 30 秒内能说出 RedPen 的价值
- 产品与普通“全文重写器”的差异一眼可见

---

### P0-4. 把输出三件套做成“产品包装”
**目标：** 输出不是附件，而是交付体系。

#### 三件套职责
- `reviewed.docx`：用于审阅、沟通、逐条 Accept / Reject
- `clean.docx`：用于继续编辑或准备提交
- `report.json`：用于记录、接入 agent/workflow、质量分析

#### 设计动作
- 统一命名规则
- 补全 report 结构
- CLI 输出里对三件套做清晰解释
- README 中把三件套定义成核心产品能力

#### 验收标准
- 用户知道每个文件应该怎么用
- report 同时服务人类摘要与程序接入
- 三件套成为 README/demo/对外介绍中的标准表达

---

### P0-5. 建立可信回归体系
**目标：** 把可靠性变成壁垒。

#### 需要的验证集
- 英文学术论文（标准稿）
- 含大量引用的论文
- 含公式/图表编号的论文
- 多 section 长文档
- 多轮修订样例

#### 核心验证维度
- 文档能正常打开
- Track Changes 正常显示
- comments 正常挂载
- clean 导出正确
- 保护区未被误伤
- 多轮修订稳定

#### 验收标准
- 每次改动都能跑 regression
- 新功能不能轻易打坏可靠性
- 可以对外明确说出质量边界与已覆盖范围

---

## P1：紧接着做（决定产品是否可规模传播/接入）

### P1-1. 将 schema 升级为 versioned protocol
**目标：** 从 CLI 工具长成可接入的 revision layer。

#### 必加字段方向
- `schema_version`
- `document_id`
- `mode`
- `section`
- `anchor`
- `edit_type`
- `confidence`
- `risk_level`
- `rationale`
- `comment_text`
- `source_model`
- `metadata`

#### 验收标准
- Claude/OpenAI/内部模型都可以产出统一 edits 结构
- report 与 protocol 可相互关联
- 后续 API / SDK 化不需要推翻现有设计

---

### P1-2. 做“更像产品”的 mode 解释与命名
**目标：** 降低选择焦虑。

#### 建议表达
- `proofread`：轻量语言修正
- `academic-polish`：面向投稿前学术表达打磨
- `reviewer`：面向严苛审稿式评论与建议

#### 设计动作
- 在 CLI help / README / 示例中统一语义
- 让用户先理解结果差异，而不是实现差异
- 控制 mode 数量，不新增低价值 mode

---

### P1-3. 建立 accept/reject 反馈的结构化入口
**目标：** 为后续质量迭代和个性化做准备。

#### 方向
- 未来记录修改采纳率
- 分 section / 分 edit type 看 acceptance
- 找出最容易被 reject 的建议类型

#### 备注
这一阶段可以先设计 report 字段与接口，不必一次做完整产品闭环。

---

### P1-4. 强化 README / README_CN 的产品叙事
**目标：** 让开源页就像产品着陆页。

#### README 首页结构建议
1. 一句话价值主张
2. before / after 视觉对比
3. 一条命令跑通示例
4. 三件套结果解释
5. 为什么不做全文重写
6. 可信保护范围
7. demo / showcase

#### 验收标准
- README 首屏就能解释产品差异
- 用户无需深读即可产生“想试一下”的冲动

---

## P2：之后再做（不要抢跑）

### P2-1. Python SDK / API 边界
把 RedPen 核心能力拆成：
- parse
- inspect
- generate_edits
- validate_edits
- apply_edits
- export_report

### P2-2. 垂类扩展
等 academic 这个主场景做成标准后，再考虑：
- legal redline
- policy review
- bilingual revision

### P2-3. UI 壳层
只有当 CLI 主路径、demo、三件套、协议、回归都成熟后，再考虑：
- 轻 web shell
- Word 插件
- 团队批处理入口

---

## 六、必须砍掉的东西

这一阶段为了维持顶级 taste，明确砍掉以下冲动：

### 1. 砍“泛用途叙事”
不要同时讲论文、合同、公文、双语、企业报告、博客稿件。

### 2. 砍“更多 mode 就更强”
mode 多会稀释主路径。

### 3. 砍“先做 Web 再说”
现在 UI 容易让产品变钝。

### 4. 砍“强调模型多聪明”
真正该卖的是：可审、可控、可交付。

### 5. 砍“让用户自己拼最佳配置”
极致产品应该默认就选对。

---

## 七、产品语言与品牌建议

### 推荐一句话定义
**RedPen turns AI review into native Word revisions for academic papers.**

### 中文表达
**RedPen 把 AI 的论文润色与审稿建议，写回成 Word 原生修订稿。**

### 推荐品牌心智
不是：
- AI 写作工具
- AI 论文重写器
- 智能文档编辑器

而是：
- **AI 审稿写回层**
- **Academic revision delivery layer**
- **Trusted revision infrastructure for Word**

---

## 八、第二阶段的北极星指标

### 用户层指标
- 首次成功跑通率
- 从 README 到跑通 demo 的时间
- 用户对“是否敢用于重要论文”的主观评分
- reviewed.docx 被继续审阅而不是被丢弃的比例

### 质量层指标
- openability success rate
- protected-zone integrity rate
- comment anchor correctness proxy
- clean export success rate
- multi-round stability rate

### 产品传播指标
- README 转化（访问 → 安装/试用）
- demo 被引用/转发的频率
- repo star / issue / PR 的增长质量
- agent / workflow 集成尝试次数

---

## 九、阶段性里程碑

## Milestone A：产品入口完成
**定义：** 新用户只看 README 首屏与一个命令，就能跑出结果并理解价值。

## Milestone B：信任系统完成
**定义：** inspect/check/report 明确表达保护范围与风险，产品可对外讲“为什么可靠”。

## Milestone C：旗舰 demo 完成
**定义：** 30~60 秒演示可以清晰展示“不是全文重写，而是 Word 原生审阅交付”。

## Milestone D：可信回归完成
**定义：** 有稳定 benchmark + regression，能防止后续迭代把核心可靠性打坏。

## Milestone E：协议层成型
**定义：** edits schema 与 report 结构升级完成，具备 SDK/API 化基础。

---

## 十、如果只能做 5 件事，就做这 5 件

1. **把默认主路径做到无脑可用**
2. **把信任系统变成产品前台**
3. **做一个炸裂的旗舰 demo**
4. **把输出三件套包装成标准交付**
5. **建立可信回归体系**

---

## 十一、最终判断

如果用极致产品 taste 收敛第二阶段方向，结论非常简单：

> **RedPen 接下来不该变得更大，而该变得更尖、更稳、更像标准。**

第一阶段已经证明：
- 这件事可行

第二阶段必须证明：
- 这件事值得依赖
- 值得传播
- 值得接入

这就是 RedPen 2.0 应该去的地方。
