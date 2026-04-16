---
name: book2skill
description: Distill a book into a coherent set of executable skills. Use when the user asks to "拆书" / "蒸馏一本书" / "把 XX 书做成 skill" / "turn a book into skills" — i.e. wants a book's frameworks, principles, and methodologies extracted into atomic, reusable Claude skills that an agent can invoke in real-world situations. NOT for simple summarization, book reviews, or role-playing as the author (that is nuwa-skill's job).
---

# book2skill — 把一本书蒸馏成一组可执行 skills 的元 skill

## 使命

把一本书里沉淀的方法论,拆解成一组**原子化、可被 agent 在真实场景下调用**的 skills,让读者真正用起来。

**边界**:
- ✅ 做: 方法论 / 决策框架 / 清单 / 原则 / 概念体系的蒸馏
- ❌ 不做: 书摘 / 读后感 / 作者人设角色扮演 (后者请用 nuwa-skill)

## 核心方法论: RIA-TV++

一个四阶段 + 并行提取 + 三重验证 + darwin 兼容测试的流水线。详见 `methodology/00-overview.md`。

```
阶段 0: Adler 整书理解     → BOOK_OVERVIEW.md
阶段 1: 5 个 agent 并行提取 → 候选方法论单元池
阶段 1.5: 三重验证筛选       → 通过的单元
阶段 2: RIA++ 构造 skill     → 每个 skill 的 SKILL.md
阶段 3: Zettelkasten 链接    → INDEX.md
阶段 4: 压力测试 (darwin 兼容) → test-prompts.json + 回炉淘汰
```

## 何时调用此 skill

用户说类似:
- "帮我拆《穷查理宝典》"
- "把毛选蒸馏成 skill"
- "distill this book into skills: <path>"
- "我想把这本书的方法论做成可用的 skill"

## 输入要求

在开始前**必须**从用户处确认:
1. **书的文本来源**: PDF / EPUB / TXT 文件路径, 或可访问的纯文本。**不要**在没有文本的情况下"凭记忆"拆书 — 宁可停下来问用户要。
2. **书名 + 作者 + 出版年**: 用于目录命名和审计。
3. **是否首次试点**: 如果用户是第一次用 book2skill,建议先拆 1 本验证流程再批量。

## 输出结构

```
books/<book-slug>/
├── BOOK_OVERVIEW.md           # 阶段 0 产出: 主旨/骨架/术语/批判
├── INDEX.md                   # 阶段 3 产出: skill 总览 + 引用图
├── candidates/                # 阶段 1 产出: 原始候选池 (审计用)
├── rejected/                  # 阶段 1.5 淘汰的单元 + 原因 (审计用)
├── <skill-slug-1>/
│   ├── SKILL.md
│   └── test-prompts.json      # darwin-skill 兼容格式
├── <skill-slug-2>/
│   └── ...
```

## 执行流程 (严格按顺序)

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

### 阶段 1.5 — 三重验证筛选

读取 `methodology/03-stage1.5-triple-verify.md`,对每个候选单元执行:

- **V1 跨域**: 书中至少 2 个独立段落有佐证?
- **V2 预测力**: 能用它回答一个书里没明说的新问题吗?
- **V3 独特性**: 不是任何聪明人都会说的常识吗?

通过的进入阶段 2。不通过的写入 `books/<slug>/rejected/` 并附原因 — 保留审计轨迹,也允许用户事后捞回。

### 阶段 2 — RIA++ 构造 skill

对每个通过的单元,按 `templates/SKILL.md.template` 填充:

- **R (Reading)**: 原文引用 ≤150 字/段
- **I (Interpretation)**: 用自己的话重写方法论骨架 (避免照搬译本)
- **A1 (Past Application)**: 书中作者用过的案例
- **A2 (Future Trigger)** ★: 用户在什么情境下会需要这个 → skill 的 `description` 字段
- **E (Execution)**: 1-2-3 可执行步骤
- **B (Boundary)**: 什么时候不适用 / 来自阶段 0 批判阶段的作者盲点

细则见 `methodology/04-stage2-ria-plus.md`。

### 阶段 3 — Zettelkasten 链接

按 `methodology/05-stage3-zettelkasten.md`:
1. 找出 skill 之间的引用关系 (A 依赖 B / A 对比 B / A 组合 B)
2. 在每个 SKILL.md 末尾补"相关 skills"段
3. 按 `templates/INDEX.md.template` 生成 `INDEX.md` (含引用图 mermaid)

### 阶段 4 — 压力测试 (darwin 兼容)

对每个 skill 按 `methodology/06-stage4-pressure-test.md`:
1. 设计 5–10 条测试 prompt,按 `templates/test-prompts.json.template` 写入 `test-prompts.json`
2. 至少包括 3 类: **应调用** / **不应调用 (诱饵)** / **边界模糊**
3. 本地跑一遍,**未过的回炉重做阶段 2** — 不做"表面修补"
4. 全部通过后通知用户: "已完成,可一键喂给 darwin-skill 自动进化"

## 质量红线 (违反则阻止输出)

1. 每个 skill 必须通过**全部**三重验证
2. 每个 skill 必须有完整的 R / I / A1 / A2 / E / B 六段
3. 原文引用 ≤150 字/段
4. 每个 skill 必须有 `test-prompts.json`,且包含诱饵测试 (不应调用的场景)
5. `description` 字段必须明确 trigger 条件,不能只是"一个关于 X 的 skill"

## 与 nuwa-skill / darwin-skill 的生态定位

- **nuwa-skill**: 蒸馏人 (思维方式 / 表达 DNA)
- **book2skill** (本 skill): 蒸馏书 (方法论 / 框架 / 原则)
- **darwin-skill**: 进化任意 skill

三者咬合: 本 skill 输出的 `test-prompts.json` 严格遵循 darwin-skill 格式,以便产出的 skill 可直接接入 darwin 做自动进化。

## 调用惯例

- **永远先试点 1 本** — 除非用户明确说"批量"
- **阶段之间主动汇报进度** — 不要静默跑完再 dump 结果
- **不凭记忆拆书** — 没文本就停下来问
- **保留审计轨迹** — candidates/ 和 rejected/ 都要留
