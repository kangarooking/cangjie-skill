# 阶段 1 — 5 个 sub-agent 并行提取

## 目标

不用单一视角读一遍,而是**同时从 5 个不同角度扫描全书**,最大化候选单元覆盖率。

## 为什么要分批并行

- **覆盖**: 单一视角会漏。框架提取器找不到的"反例",反例提取器会找到。
- **速度**: 支持子 Agent 的宿主可并行处理独立任务,在不超过并发上限的前提下缩短提取时间。
- **独立性**: 每个 extractor 独立判断,避免互相污染 — 三重验证才能真正起作用 (V1 跨域要求"独立出现")

## 5 个 sub-agent

每个 sub-agent 接收:
- `BOOK_OVERVIEW.md` (阶段 0 产出, 提供全局上下文)
- 书本文本 (或文本路径)
- 对应的 extractor prompt (`extractors/<type>-extractor.md`)

使用宿主提供的子 Agent 能力启动任务。Codex 环境可使用当前会话提供的 `spawn_agent` / `wait_agent` 等工具,但必须先检查 Agent 状态与实际可用容量,并遵守 `agents.max_concurrent_threads_per_session` 或当前会话声明的上限。

1. 从 framework / principle / case / counter-example / glossary 中选择本批可容纳的独立任务。
2. 启动本批任务并等待全部完成,主流程逐一校验输出文件。
3. 对剩余提取器重复上述步骤,全部完成后再进入阶段 1.5。

每个子 Agent 只写自己的唯一产出文件。若处于嵌套调用、已有其他 Agent 或无法确认容量,应保守缩小批次、逐个运行或串行;不得假设固定并发槽位数。

**降级方案**: 当前环境不支持 sub-agent 或槽位不足时,用同样 5 个 extractor prompt 串行执行 (每次以"干净视角"执行一个 extractor 的职责,不带上一个 extractor 的判断),产出格式不变。

## 长文本分块策略 (超出单个 sub-agent 上下文时)

一本大部头 (如全五卷选集) 或几小时视频的转写稿,可能超出单个 sub-agent 能一次读完的上下文。此时:

1. **切块**: 按章节/卷/分 P 等自然边界切块,每块控制在 sub-agent 能连同 `BOOK_OVERVIEW.md` 一起舒适读完的规模 (经验值: 单块 ≤5 万字)
2. **全局锚点**: 每一块都必须附带 `BOOK_OVERVIEW.md` — 它是 extractor 判断"这段内容在全书中扮演什么角色"的锚点,不能省
3. **逐块扫描**: extractor 逐块提取候选,标注每条候选来自哪一块 (source_chapter 字段天然承载)
4. **块间汇总**: 全部块扫完后,extractor 自己先做一轮合并 — 同一方法论在多块中出现的,合并成一条并保留所有出处 (这些多出处恰好是阶段 1.5 V1 跨域验证的证据)
5. 汇总后的结果才写入 `candidates/<type>.md`

| # | extractor | 查找对象 | 产出文件 |
|---|---|---|---|
| 1 | framework-extractor | 思维模型 / 决策框架 / 推理方法 | `candidates/frameworks.md` |
| 2 | principle-extractor | 原则 / 清单 / 规则 / 断言 | `candidates/principles.md` |
| 3 | case-extractor | 作者在书中亲自使用的实例 | `candidates/cases.md` |
| 4 | counter-example-extractor | 作者警告的失败 / 反例 / 陷阱 | `candidates/counter-examples.md` |
| 5 | glossary-extractor | 关键概念词典 | `candidates/glossary.md` |

## 每个候选单元的最小字段

无论是哪个 extractor,产出的每条候选单元必须包含:

```yaml
id: f01                           # 类型缩写 + 序号
title: 逆向思维                    # 简短标题
type: framework                   # framework / principle / case / counter-example / term
source_chapter: 第三讲             # 书中位置
source_quote: |                   # 原文引用 ≤150 字 (英文 ≤100 词)
  "反过来想,总是反过来想..."
summary: |                        # 用自己的话,5-10 行
  ...
tags: [decision, mental-model]    # 便于后续链接
```

## 输出前的自检

每个 extractor 在提交候选之前自问:
1. 这个单元**在书中**有明确根据吗? (不是我脑补)
2. 它属于我这个 extractor 的职责范围吗? (不要越界)
3. 它是不是已经在别处被别的 extractor 提取过了? (重复不是问题,阶段 1.5 会合并)

## 不在本阶段做的事

- **不做筛选** — 宁错杀,留给阶段 1.5 三重验证
- **不写 skill** — 只出候选,不出 SKILL.md
- **不做跨单元链接** — 留给阶段 3
