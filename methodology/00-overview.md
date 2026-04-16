# RIA-TV++ 方法论总览

本文是 book2skill 所用 SOP 的设计说明,解释"为什么这么做"。执行时的具体步骤请读 `SKILL.md` 和 `methodology/01-*` 至 `06-*`。

## 命名

**RIA-TV++** =
- **RIA** — 赵周 (《这样读书就够了》) 的便签拆书法: Reading / Interpretation / Appropriation
- **TV** — Triple Verification,借自 nuwa-skill 的三重验证
- **++** — 面向 agent 执行的扩展: E (Execution 可执行步骤) + B (Boundary 边界)

## 思想来源

| 来源 | 借鉴内容 |
|---|---|
| Mortimer Adler 《如何阅读一本书》 | 阶段 0: 分析阅读三阶段 (结构/解释/批判) |
| 赵周 RIA 拆书法 | 阶段 2: R-I-A1-A2 基本骨架, 尤其 A2 → trigger |
| Niklas Luhmann Zettelkasten | 原子化 + 链接 + 用自己的话重写 |
| Tiago Forte Progressive Summarization | 阶段 4 的"可验证压缩链条"思想 |
| nuwa-skill | 阶段 1 并行 extractor + 阶段 1.5 三重验证 |
| darwin-skill | 阶段 4 test-prompts.json 格式 + 可进化性 |

## 根本洞察

**现有读书方法论都是为人类读者蒸馏,不是为 agent 执行者蒸馏。**

| 维度 | 给人看 | 给 agent 用 (book2skill 目标) |
|---|---|---|
| 关键字段 | 故事 / 金句 / 情感钩子 | trigger / 可执行步骤 / 判停标准 |
| 失败模式 | 读完就忘 | trigger 不准 → 永不调用或乱调用 |
| 成功标准 | 读者"有收获" | 真实问题被解决 |

所以 RIA-TV++ 的所有"扩展"(TV / E / B / test-prompts) 都是为了解决这个目标迁移带来的新问题。

## 流水线

```
          ┌───────────────────┐
          │ 阶段 0: 整书理解   │  Adler 四步
          └─────────┬─────────┘
                    │ BOOK_OVERVIEW.md
                    ▼
          ┌───────────────────┐
          │ 阶段 1: 并行提取   │  5 个 sub-agent 同时跑
          └─────────┬─────────┘
                    │ candidates/
                    ▼
          ┌───────────────────┐
          │ 阶段 1.5: 三重验证 │  V1 跨域 / V2 预测力 / V3 独特性
          └─────────┬─────────┘
                    │ 通过单元 + rejected/
                    ▼
          ┌───────────────────┐
          │ 阶段 2: RIA++ 构造 │  R / I / A1 / A2 / E / B
          └─────────┬─────────┘
                    │ 每个 skill 的 SKILL.md
                    ▼
          ┌───────────────────┐
          │ 阶段 3: 链接       │  Zettelkasten + INDEX.md
          └─────────┬─────────┘
                    │
                    ▼
          ┌───────────────────┐
          │ 阶段 4: 压力测试   │  test-prompts.json + 本地跑 + 回炉
          └───────────────────┘
                    │
                    ▼
          可喂给 darwin-skill 自动进化
```

## 不变量 (任何迭代都不能违反)

1. **原子性**: 一个 skill 只做一个方法论单元,不能"大而全"
2. **可追溯**: 每个 skill 必须有原文引用,指向源书章节
3. **可验证**: 每个 skill 必须通过三重验证 + 压力测试
4. **可进化**: 每个 skill 必须附带 darwin 兼容的 test-prompts.json
5. **用户参与**: 阶段 0 之后必须让用户确认骨架再继续
