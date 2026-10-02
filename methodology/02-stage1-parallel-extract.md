# 阶段 1 — 5 个 sub-agent 并行提取

## 目标

不用单一视角读一遍,而是**同时从 5 个不同角度扫描全书**,最大化候选单元覆盖率。

## 为什么要并行

- **覆盖**: 单一视角会漏。框架提取器找不到的"反例",反例提取器会找到。
- **速度**: Claude Code 的 Agent 工具支持并行,不用白不用。
- **独立性**: 每个 extractor 独立判断，减少相互带偏；多个 extractor 提到同一原文不等于多份独立证据

## 5 个 sub-agent

每个 sub-agent 接收:
- `BOOK_OVERVIEW.md` (阶段 0 产出, 提供全局上下文)
- 书本文本 (或文本路径)
- 对应的 extractor prompt (`extractors/<type>-extractor.md`)

并在一次调用中通过 Agent 工具 **同时 spawn 5 个**,不是串行。

**降级方案**: 当前环境不支持并行 sub-agent 时,用同样 5 个 extractor prompt 串行执行 (每次以"干净视角"执行一个 extractor 的职责,不带上一个 extractor 的判断),产出格式不变。

## 按 extractor 类型分化的上下文策略（v2.2）

阶段 1 的目标是**有依据的覆盖**（宁可多收候选，不在此筛选）。但 5 类 extractor 查找对象的分布特性不同,
不能一刀切全量扫描,也不能一刀切检索式（后者会直接损害覆盖率,方案缺口 B）:

| extractor | 查找对象的分布特性 | 上下文策略 |
|---|---|---|
| framework | 框架可能跨章节；流程/管理机制也可能只在一处讲透 | **保持全量扫描** |
| principle | 原则、公式、清单、指标口径散落在正文/表格/脚注 | **保持全量扫描** |
| case | 案例是局部命中型,有明确文本锚点 | 检索式取块 |
| counter-example | 反例是局部命中型,有明确警告性措辞 | 检索式取块 |
| glossary | 术语是局部命中型,可先用确定性方法预筛 | 检索式取块 + 脚本预筛 |

**检索式取块的前置条件**: 先用确定性脚本建好内容地图 —
`python3 scripts/build_chunks.py <源文件> --sidecar books/<slug>/.cangjie` 生成结构感知块,
`python3 scripts/build_index.py books/<slug>/.cangjie/chunks/chunks.jsonl` 建 SQLite FTS5 索引。
检索式 extractor 的流程: 关键词召回相关块 → 取邻接块防断章取义 → 证据不足时扩大窗口 →
候选需回原文核验。五个 extractor 仍使用独立任务上下文,独立判断不变。

**覆盖率硬门**: 同时对照全量扫描候选池与阶段 0 原书关键任务清单；不能只用旧版三重验证的通过项作分母。
对重要任务逐项标记“有候选/有依据降为参考/待核查/确有遗漏”。未解释遗漏先扩大窗口，仍漏则退回全量扫描；待核查不计作已覆盖的可执行能力。每次改动检索策略都重跑覆盖对比。

## 长文本分块策略 (超出单个 sub-agent 上下文时)

一本大部头 (如全五卷选集) 或几小时视频的转写稿,可能超出单个 sub-agent 能一次读完的上下文。此时:

1. **切块**: 优先复用 `build_chunks.py` 的结构感知块（按章节/卷/分 P 等自然边界,单块 ≤5 万字）
2. **全局锚点**: 每一块都必须附带 `BOOK_OVERVIEW.md` — 它是 extractor 判断"这段内容在全书中扮演什么角色"的锚点,不能省
3. **逐块扫描**: 全量扫描型 extractor 逐块提取候选,标注每条候选来自哪一块 (source_chapter 字段天然承载,有 chunk_id 时一并记录)
4. **块间汇总**: 全部块扫完后合并同一方法，保留所有出处和相邻条件；一次完整说明也保留，重复转述不冒充独立证据
5. 汇总后的结果才写入 `candidates/<type>.md`

| # | extractor | 查找对象 | 产出文件 |
|---|---|---|---|
| 1 | framework-extractor | 思维模型 / 决策框架 / 操作流程 / 排障机制 | `candidates/frameworks.md` |
| 2 | principle-extractor | 原则 / 清单 / 规则 / 公式 / 指标口径 | `candidates/principles.md` |
| 3 | case-extractor | 书中亲历/转述案例、例题，区分性质 | `candidates/cases.md` |
| 4 | counter-example-extractor | 作者警告的失败 / 反例 / 陷阱 | `candidates/counter-examples.md` |
| 5 | glossary-extractor | 关键概念词典 | `candidates/glossary.md` |

## 每个候选单元的最小字段

无论是哪个 extractor,产出的每条候选单元必须包含:

```yaml
id: f01                           # 类型缩写 + 序号
title: 逆向思维                    # 简短标题
type: framework                   # framework / principle / procedure / calculation / troubleshooting / case / counter-example / term
source_chapter: 第三讲             # 书中位置
source_quote: |                   # 原文引用 ≤150 字 (英文 ≤100 词)
  "反过来想,总是反过来想..."
summary: |                        # 用自己的话,5-10 行
  ...
tags: [decision, mental-model]    # 便于后续链接
task_ids: [task-01]               # 对应 overview 的任务；无对应时解释原因
```

## 输出前的自检

每个 extractor 在提交候选之前自问:
1. 这个单元**在书中**有明确根据吗? (不是我脑补)
2. 它属于我这个 extractor 的职责范围吗? (不要越界)
3. 它是不是已经在别处被别的 extractor 提取过了? (重复不是问题,阶段 1.5 会合并)

## 不在本阶段做的事

- **不做筛选** — 宁可多收有依据的候选，不漏单处重要机制，留给阶段 1.5 判断
- **不写 skill** — 只出候选,不出 SKILL.md
- **不做跨单元链接** — 留给阶段 3
