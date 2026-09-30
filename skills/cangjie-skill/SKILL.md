---
name: cangjie-skill
description: Distill a book, long-video transcript, podcast, course, or interview into a coherent set of executable skills. Use when the user asks to "拆书" / "蒸馏一本书" / "把 XX 书做成 skill" / "把这个视频/播客/课程蒸馏成 skill" / "turn a book or video into skills" — i.e. wants the frameworks, principles, and methodologies in long-form content extracted into atomic, reusable Claude skills that an agent can invoke in real-world situations. NOT for simple summarization, book reviews, or role-playing as the author (that is nuwa-skill's job).
metadata:
  cangjie.version: "2.5.0"
---

# cangjie-skill — 把一本书蒸馏成一组可执行 skills 的元 skill

## 使命

把一本书里沉淀的方法论,拆解成**原子化、可被 agent 在真实场景下调用**的能力,并按用户目的编译成合适数量的 skill,让读者真正用起来。

> **术语约定**: 本文档及 `methodology/`、`extractors/` 中所有的"书",泛指一切被蒸馏的长内容 — 书籍、长视频转写、播客文字稿、课程、访谈、长文、资料集。

**边界**:
- ✅ 做: 方法论 / 决策框架 / 清单 / 原则 / 概念体系的蒸馏
- ❌ 不做: 书摘 / 读后感 / 作者人设角色扮演 (后者请用 nuwa-skill)

## 核心方法论: RIA-TV++（v2.5 Bundle 版）

一个五阶段 + 并行提取 + 三重验证 + 晋级门 + darwin 兼容测试的流水线。详见 `methodology/00-overview.md`。

```
阶段 0:   Adler 整书理解        → BOOK_OVERVIEW.md
阶段 1:   5 个 agent 并行提取    → 候选方法论单元池
阶段 1.5: 三重验证筛选（知识验证） → 通过的单元 (用户轻确认)
阶段 1.6: 独立 Skill 晋级门（产品化验证）→ promoted / router 去向
阶段 2:   RIA++ 构造能力卡       → .cangjie/capabilities/cards/<slug>.md
阶段 3:   Zettelkasten 链接      → verified.yaml 的 also_read + GLOSSARY
阶段 4:   压力测试 (darwin 兼容)  → 评测用例 + 回炉淘汰
阶段 5:   编译与交付             → cangjie.py compile（single/pack）+ DIGEST.md + 安装
```

**v2.5 关键变化（ADR-002）**: 阶段 2–4 不再直接把每个单元写成独立的最终 Skill 目录，而是产出一份 **Capability Bundle**（`books/<slug>/.cangjie/capabilities/verified.yaml` + `cards/*.md`）。single 与 pack 都从这同一份 Bundle 由 `scripts/cangjie.py compile` 确定性编译，两者引用同一组稳定 `capability_id`。旧的 one-to-one 输出仍受支持（legacy-pack，见 `docs/migrations/2026-08-25-v2.0-to-v2.1.md`）。

## 何时调用此 skill

用户说类似:
- "帮我拆《穷查理宝典》"
- "把毛选蒸馏成 skill"
- "把这个 B 站视频/播客/课程蒸馏成 skill"
- "distill this book into skills: <path>"
- "我想把这本书的方法论做成可用的 skill"

## 输入要求

在开始前**必须**从用户处确认:
1. **内容文本来源**: PDF / EPUB / TXT / 字幕文件 / 转写稿路径, 或可访问的纯文本。**不要**在没有文本的情况下"凭记忆"蒸馏 — 宁可停下来问用户要。(视频/播客建议先用 video-downloader 类工具拿到转写文本)
2. **内容元信息**: 书籍是"书名 + 作者 + 出版年"; 视频/播客/课程是"标题 + 作者(UP 主/主播/讲者) + 发布时间"。用于目录命名和审计。
3. **使用目的**（决定输出模式推荐）: 学习/查阅这本书 → 倾向 single；接入日常工作流、跨书组合 → 倾向 pack。不确定时按 single-first 原则先推荐 single。
4. **是否首次试点**: 如果用户是第一次用 cangjie-skill,建议先蒸馏 1 份内容验证流程再批量。

**非书籍内容的字段映射**: 章节类字段对视频填时间戳或分 P,对播客填集数,对课程填讲次 — 保证可追溯即可。

## 输出结构

```
books/<book-slug>/
├── PIPELINE_STATE.md          # 流水线状态: 当前阶段 + 进度 (断点续跑用)
├── BOOK_OVERVIEW.md           # 阶段 0 产出: 主旨/骨架/术语/批判
├── verified.md                # 阶段 1.5 产出: 通过三重验证的单元 + 判定理由
├── GLOSSARY.md                # 阶段 3 产出: 全书共享术语词典
├── DIGEST.md                  # 阶段 5 产出: 面向读者的精华长文
├── candidates/                # 阶段 1 产出: 原始候选池 (审计用)
├── rejected/                  # 阶段 1.5 淘汰的单元 + 原因 (审计用)
└── .cangjie/                  # v2.5 侧车层（编译事实源 + 运行记录）
    ├── capabilities/
    │   ├── verified.yaml      # Capability Bundle（唯一编译事实源, capability-bundle.schema.json）
    │   ├── cards/<slug>.md    # RIA 能力卡（R/I/A1/A2/E/B, 阶段 2 产出）
    │   ├── destinations.json  # 晋级/路由去向映射（阶段 1.6 产出）
    │   └── book/{overview.md,glossary.md}
    ├── runs/<run-id>/         # 每次编译/更新的决策报告与校验日志
    └── snapshots/             # 发布前快照（rollback 用）
```

最终交付物由 `scripts/cangjie.py compile` 从 Bundle 编译（--output single 得到 1 个入口 + 能力卡；--output pack 得到 1 个来源路由入口 + 少量晋级 Skill）。

## 执行流程 (严格按顺序)

**断点续跑**: 开始前先检查 `books/<slug>/PIPELINE_STATE.md` 是否存在。存在则读取并从记录的阶段续跑,不要从头重来。每完成一个阶段,更新该文件。

### 阶段 0 — 整书理解

1. 读取用户提供的书本文本。大文件分块阅读。
2. 执行 `methodology/01-stage0-adler.md` 中的 Adler 四步 (结构 / 解释 / 批判 / 应用)。
3. 按 `templates/BOOK_OVERVIEW.md.template` 填充,写入 `books/<slug>/BOOK_OVERVIEW.md`。
4. 把产出展示给用户确认:"骨架我理解对了吗?有没有你希望重点突出的方向?" 得到确认再进入阶段 1。

### 阶段 1 — 5 个 sub-agent 并行提取

**并行** spawn 5 个 Task sub-agents(使用 Agent 工具,一次调用中发起 5 个):

| sub-agent | 读取的 prompt | 上下文策略 | 产出 |
|---|---|---|---|
| 框架提取器 | `extractors/framework-extractor.md` | **全量扫描**（跨章节隐性分布） | 决策框架 / 思维模型 |
| 原则提取器 | `extractors/principle-extractor.md` | **全量扫描**（需判断反复出现） | 原则 / 清单 / 规则 |
| 案例提取器 | `extractors/case-extractor.md` | 检索式取块（局部命中型） | 作者在书中亲自使用过的实例 |
| 反例提取器 | `extractors/counter-example-extractor.md` | 检索式取块（局部命中型） | 书中警告的失败模式 |
| 术语提取器 | `extractors/glossary-extractor.md` | 检索式取块 + 脚本预筛 | 关键概念词典 |

每个 sub-agent 独立判断、独立输出到 `books/<slug>/candidates/<type>.md`。

- **长文本**: 超出单个 sub-agent 上下文的内容,按 `methodology/02-stage1-parallel-extract.md` 的分块策略处理；已建立内容索引（`.cangjie/index/`）时,检索式 extractor 按索引取相关块。
- **覆盖率硬门**: 检索式改造后,最终通过三重验证的候选相对全量扫描基线**漏检数必须为 0**,否则该 extractor 退回全量扫描。
- **降级方案**: 当前环境不支持并行 sub-agent 时,用同样 5 个 extractor prompt **串行**执行,产出格式不变。

### 阶段 1.5 — 三重验证筛选（知识验证）

读取 `methodology/03-stage1.5-triple-verify.md`,对每个候选单元执行:

- **V1 跨域**: 书中至少 2 个独立段落有佐证?
- **V2 预测力**: 能用它回答一个书里没明说的新问题吗?
- **V3 独特性**: 不是任何聪明人都会说的常识吗?

通过的写入 `books/<slug>/verified.md`。不通过的写入 `books/<slug>/rejected/` 并附原因。

**用户轻确认** ★: 筛选完成后,把"通过的 N 个候选标题 + 淘汰的 M 个"列表展示给用户确认,再进入阶段 1.6。

### 阶段 1.6 — 独立 Skill 晋级门（产品化验证）

读取 `methodology/03b-stage1.6-promotion-gate.md`。知识验证通过 ≠ 值得成为独立 Skill。对每个单元评审五条判据（独立意图/独立契约/独立运行/独立复用/独立评测,前 3 条必须通过,后 2 条至少 1 条),把去向写入 Bundle 的 `promotion.destination`（promoted / router）。未晋级单元**不淘汰**,保留为来源路由入口内的能力卡。可发现入口软预算默认 8（含 1 个来源路由入口）。

### 阶段 2 — RIA++ 构造能力卡

对每个通过的单元,按 `methodology/04-stage2-ria-plus.md` 构造 R / I / A1 / A2 / E / B 六段能力卡:

- 卡片正文写入 `books/<slug>/.cangjie/capabilities/cards/<slug>.md`（**不带 frontmatter**,frontmatter 数据记入 Bundle）;
- 同时在 `verified.yaml` 登记该能力: 稳定 `capability_id`、intents、keywords、one_liner、importance（附依据）、`frontmatter.description`（A2 浓缩版）。

### 阶段 3 — Zettelkasten 链接

按 `methodology/05-stage3-zettelkasten.md`:
1. 找出能力之间的引用关系,写入 Bundle 中各能力的 `also_read`,并回填 A2 的"与相邻能力的区分"
2. 把 `candidates/glossary.md` 整理成 `books/<slug>/GLOSSARY.md`,并复制到 `.cangjie/capabilities/book/glossary.md`
3. INDEX/路由表由编译器从 Bundle 生成,不再手写

### 阶段 4 — 压力测试 (darwin 兼容)

对每个**晋级能力**按 `methodology/06-stage4-pressure-test.md` 设计触发评测（含兄弟诱饵与来源路由入口的互斥负例）;对 router 能力设计"经路由入口可达"的路由用例。未过的回炉重做阶段 2。

### 阶段 5 — 编译与交付

按 `methodology/07-stage5-deliver.md`:
1. 生成 `books/<slug>/DIGEST.md` — 面向读者的精华长文
2. 运行 `python3 scripts/cangjie.py compile --bundle books/<slug>/.cangjie/capabilities --out <目标目录> --output auto`,把决策报告展示给用户轻确认（按推荐 / 改 single / 改 pack）
3. 询问用户安装位置,把编译产物复制或 symlink 过去
4. 告知用户: "已完成,可一键喂给 darwin-skill 自动进化"

## 质量红线 (违反则阻止输出)

1. 每个能力必须通过**全部**三重验证
2. 每张能力卡必须有完整的 R / I / A1 / A2 / E / B 六段
3. 原文引用 ≤150 字/段 (英文 ≤100 词/段)
4. 每个 active 能力在 `destinations.json` 中恰好一个去向（promoted_to 或 served_by）;未晋级能力必须可经来源路由入口到达
5. 晋级 Skill 的 `description` 必须明确 trigger 条件,并与来源路由入口互有近邻负例
6. 编译产物必须通过 `scripts/validate_skill_pack.py`（格式/相对引用/frontmatter 100%）
7. 生成目录只读:检测到本地手改时不得静默覆盖（编译器强制三选一）

## 与 nuwa-skill / darwin-skill 的生态定位

- **nuwa-skill**: 蒸馏人 (思维方式 / 表达 DNA)
- **cangjie-skill** (本 skill): 蒸馏书 (方法论 / 框架 / 原则)
- **darwin-skill**: 进化任意 skill

三者咬合: 本 skill 输出的评测用例遵循 darwin-skill 格式,以便产出的 skill 可直接接入 darwin 做自动进化。

## 调用惯例

- **永远先试点 1 本** — 除非用户明确说"批量"
- **阶段之间主动汇报进度** — 不要静默跑完再 dump 结果
- **不凭记忆拆书** — 没文本就停下来问
- **保留审计轨迹** — candidates/ 和 rejected/ 都要留
- **随时可续跑** — 每完成一个阶段就更新 PIPELINE_STATE.md,中断后从状态文件恢复
- **输出策略持久化** — update/repair 默认沿用原输出模式,不因新增材料静默改变产物形态
