---
name: cangjie-skill
description: Distill a book, long-video transcript, podcast, course, or interview into a coherent set of executable skills. Use when the user asks to "拆书" / "蒸馏一本书" / "把 XX 书做成 skill" / "把这个视频/播客/课程蒸馏成 skill" / "turn a book or video into skills" — i.e. wants the frameworks, principles, and methodologies in long-form content extracted into atomic, reusable Claude skills that an agent can invoke in real-world situations. NOT for simple summarization, book reviews, or role-playing as the author (that is nuwa-skill's job).
---

# cangjie-skill — 把一本书蒸馏成一组可执行 skills 的元 skill

## 使命

把一本书里沉淀的方法论,拆解成一组**原子化、可被 agent 在真实场景下调用**的 skills,让读者真正用起来。

> **术语约定**: 本文档及 `methodology/`、`extractors/` 中所有的"书",泛指一切被蒸馏的长内容 — 书籍、长视频转写、播客文字稿、课程、访谈、长文、资料集。

**边界**:
- ✅ 做: 方法论 / 决策框架 / 清单 / 原则 / 概念体系的蒸馏
- ❌ 不做: 书摘 / 读后感 / 作者人设角色扮演 (后者请用 nuwa-skill)

## 核心方法论: RIA-TV++

一个五阶段 + 并行提取 + 三重验证 + darwin 兼容测试的流水线。详见 `methodology/00-overview.md`。

```
阶段 0: Adler 整书理解     → BOOK_OVERVIEW.md
阶段 1: 5 个 agent 并行提取 → 候选方法论单元池
阶段 1.5: 三重验证筛选       → 双评审 + V1 自适应 + 通过单元 (用户轻确认)
阶段 2: RIA++ 构造 skill     → 每个 skill 的 SKILL.md
阶段 3: Zettelkasten 链接    → INDEX.md + GLOSSARY.md
阶段 4: 压力测试 (darwin 兼容) → test-prompts.json + execution_check + 对抗题 + 回炉淘汰
阶段 5: 交付                 → DIGEST.md + SCORECARD.md + 安装到 skills 目录
```

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
3. **内容体量分级**: 长书 / 中篇 / 短内容。短内容指少于 2 万字或少于 40 分钟的转写稿,用于阶段 1.5 的 V1 自适应验证。
4. **是否首次试点**: 如果用户是第一次用 cangjie-skill,建议先蒸馏 1 份内容验证流程再批量。

**非书籍内容的字段映射**: `source_chapter` 等"章节"字段对视频填时间戳或分 P,对播客填集数,对课程填讲次 — 保证可追溯即可。

## 输出结构

```
books/<book-slug>/
├── PIPELINE_STATE.md          # 流水线状态: 当前阶段 + 各 skill 进度 (断点续跑用)
├── BOOK_OVERVIEW.md           # 阶段 0 产出: 主旨/骨架/术语/批判
├── verified.md                # 阶段 1.5 产出: 通过三重验证的单元 + 判定理由
├── INDEX.md                   # 阶段 3 产出: skill 总览 + 引用图
├── GLOSSARY.md                # 阶段 3 产出: 全书共享术语词典
├── DIGEST.md                  # 阶段 5 产出: 面向读者的精华长文
├── SCORECARD.md               # 阶段 5 产出: 流水线质量记分卡
├── candidates/                # 阶段 1 产出: 原始候选池 (审计用)
├── rejected/                  # 阶段 1.5 淘汰的单元 + 原因 (审计用)
├── <skill-slug-1>/
│   ├── SKILL.md
│   ├── test-prompts.json      # darwin-skill 兼容格式
│   └── test-results.md        # 阶段 4 测试通过率 + 失败分析
├── <skill-slug-2>/
│   └── ...
```

## 执行流程 (严格按顺序)

**断点续跑**: 开始前先检查 `books/<slug>/PIPELINE_STATE.md` 是否存在。存在则读取并从记录的阶段续跑,不要从头重来。每完成一个阶段,更新该文件 (当前阶段 / 已完成产物 / 各 skill 状态 / 下一步),格式用简单的 checklist markdown 即可。

### 阶段 0 — 整书理解

1. 读取用户提供的书本文本。大文件分块阅读。
2. 执行 `methodology/01-stage0-adler.md` 中的 Adler 四步 (结构 / 解释 / 批判 / 应用)。
3. 按 `templates/BOOK_OVERVIEW.md.template` 填充,写入 `books/<slug>/BOOK_OVERVIEW.md`。
4. 把产出展示给用户确认:"骨架我理解对了吗?有没有你希望重点突出的方向?" 得到确认再进入阶段 1。

### 阶段 1 — 5 个 sub-agent 并行提取

**并行** spawn 5 个 Task sub-agents(使用 Agent 工具,一次调用中发起 5 个):

| sub-agent | 读取的 prompt | 产出 |
|---|---|---|
| 框架提取器 | `extractors/framework-extractor.md` | 决策框架 / 思维模型 |
| 原则提取器 | `extractors/principle-extractor.md` | 原则 / 清单 / 规则 |
| 案例提取器 | `extractors/case-extractor.md` | 作者在书中亲自使用过的实例 |
| 反例提取器 | `extractors/counter-example-extractor.md` | 书中警告的失败模式 |
| 术语提取器 | `extractors/glossary-extractor.md` | 关键概念词典 |

每个 sub-agent 独立读书、独立提取、独立输出到 `books/<slug>/candidates/<type>.md`。

- **长文本**: 超出单个 sub-agent 上下文的内容,按 `methodology/02-stage1-parallel-extract.md` 的分块策略处理。
- **降级方案**: 当前环境不支持并行 sub-agent 时,用同样 5 个 extractor prompt **串行**执行,产出格式不变。

### 阶段 1.5 — 三重验证筛选

读取 `methodology/03-stage1.5-triple-verify.md`,对每个候选单元执行:

- **V1 跨域**: 长书/中篇要求书中至少 2 个独立段落有佐证;短内容允许 1 处内容内佐证 + 1 处外部可佐证,并标记证据等级
- **V2 预测力**: 能用它回答一个书里没明说的新问题吗?
- **V3 独特性**: 不是任何聪明人都会说的常识吗?

每条候选由两个独立评审 agent 分别判断 V1 / V2 / V3。两者结论一致时直接录用或淘汰;结论不一致时进入第三个仲裁 agent,或升级为用户确认项。通过的写入 `books/<slug>/verified.md`,并记录评审一致性。不通过的写入 `books/<slug>/rejected/` 并附原因 — 保留审计轨迹,也允许用户事后捞回。

**用户轻确认** ★: 筛选完成后,把"通过的 N 个候选标题 + 淘汰的 M 个"列表展示给用户:"这 N 个会做成 skill,有想捞回或砍掉的吗?" 得到确认再进入阶段 2 — 阶段 2–4 是最耗时的部分,这一步确认能避免大量返工。

### 阶段 2 — RIA++ 构造 skill

对每个通过的单元,按 `templates/SKILL.md.template` 填充:

- **R (Reading)**: 原文引用 ≤150 字/段 (英文原文 ≤100 词/段)
- **I (Interpretation)**: 用自己的话重写方法论骨架 (避免照搬译本)
- **A1 (Past Application)**: 书中作者用过的案例
- **A2 (Future Trigger)** ★: 用户在什么情境下会需要这个 → skill 的 `description` 字段
- **E (Execution)**: 1-2-3 可执行步骤
- **B (Boundary)**: 什么时候不适用 / 来自阶段 0 批判阶段的作者盲点

细则见 `methodology/04-stage2-ria-plus.md`。注意: A2 中"与相邻 skill 的区分"此时只写**初稿** (基于 verified.md 的单元列表),阶段 3 建立链接后回填定稿。

### 阶段 3 — Zettelkasten 链接

按 `methodology/05-stage3-zettelkasten.md`:
1. 找出 skill 之间的引用关系 (A 依赖 B / A 对比 B / A 组合 B)
2. 在每个 SKILL.md 末尾补"相关 skills"段,并回填 A2 的"与相邻 skill 的区分"
3. 按 `templates/INDEX.md.template` 生成 `INDEX.md` (含引用图 mermaid)
4. 把 `candidates/glossary.md` 整理成 `books/<slug>/GLOSSARY.md` — 它是所有 skill 的共享词典,不该埋在审计目录里
5. 执行术语反向注入: 扫描每个 skill 正文,凡使用 GLOSSARY 中的作者特定术语,在该 skill 末尾追加 2–5 条"本 skill 术语表",保证独立调用时不失义

### 阶段 4 — 压力测试 (darwin 兼容)

对每个 skill 按 `methodology/06-stage4-pressure-test.md`:
1. 设计 5–10 条测试 prompt,按 `templates/test-prompts.json.template` 写入 `test-prompts.json`
2. 至少包括 4 类: **应调用** / **不应调用 (诱饵)** / **边界模糊** / **执行质量检查**。诱饵中至少 1 条必须是"应触发同书另一个 skill"的场景 (跨 skill 混淆测试)
3. 增加对抗性出题: 另起一个 agent 只读取 skill 的 name + description,生成 3 条最容易误触发或漏触发的用户话术,并入测试集
4. 优先用独立 sub-agent 盲测每条 prompt,由主流程对照预期统计结果,**未过的回炉重做阶段 2** — 不做"表面修补"
5. 每个 skill 的测试结果写入 `<skill-dir>/test-results.md`

### 阶段 5 — 交付

按 `methodology/07-stage5-deliver.md`:
1. 生成 `books/<slug>/DIGEST.md` — 面向读者的精华长文 (按 `templates/DIGEST.md.template`),满足"不读全书、只看精华"的需求
2. 生成 `books/<slug>/SCORECARD.md` — 汇总候选数、验证通过率、评审一致率、测试通过率、回炉次数和总耗时
3. 询问用户安装位置 (用户级 `~/.claude/skills/` 或项目级 `.claude/skills/` / `.cursor/skills/`),把通过测试的 skill 复制或 symlink 过去 — **没有这一步,产出的 skill 无法被真正调用**
4. 告知用户: "已完成,可一键喂给 darwin-skill 自动进化"

## 质量红线 (违反则阻止输出)

1. 每个 skill 必须通过**全部**三重验证
2. 每个 skill 必须有完整的 R / I / A1 / A2 / E / B 六段
3. 原文引用 ≤150 字/段 (英文 ≤100 词/段)
4. 每个 skill 必须有 `test-prompts.json`,且包含诱饵测试 (不应调用的场景),其中至少 1 条是同书兄弟 skill 的场景
5. 每个 skill 必须至少有 1 条 `execution_check`,验证 E 段执行结果是否忠于作者方法论
6. `description` 字段必须明确 trigger 条件,不能只是"一个关于 X 的 skill"

## 与 nuwa-skill / darwin-skill 的生态定位

- **nuwa-skill**: 蒸馏人 (思维方式 / 表达 DNA)
- **cangjie-skill** (本 skill): 蒸馏书 (方法论 / 框架 / 原则)
- **darwin-skill**: 进化任意 skill

三者咬合: 本 skill 输出的 `test-prompts.json` 严格遵循 darwin-skill 格式,以便产出的 skill 可直接接入 darwin 做自动进化。

## 调用惯例

- **永远先试点 1 本** — 除非用户明确说"批量"
- **阶段之间主动汇报进度** — 不要静默跑完再 dump 结果
- **不凭记忆拆书** — 没文本就停下来问
- **保留审计轨迹** — candidates/ 和 rejected/ 都要留
- **随时可续跑** — 每完成一个阶段就更新 PIPELINE_STATE.md,中断后从状态文件恢复
