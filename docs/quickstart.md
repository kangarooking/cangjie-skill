# Quickstart：从一本书到一个可安装的 Skill Pack

> 本文是**实操向的分步指引**：手把手走一遍 cangjie-skill 的完整流程（RIA-TV++ v2.5）。
> 概念与设计原理见 [README](../README.zh-CN.md)；Agent 执行契约见 [SKILL.md](../SKILL.md)。

## 0. 准备

**环境依赖**：

- Python 3.10+ 与 PyYAML（`python3 -m pip install pyyaml`；可选 `tiktoken`、`jsonschema`）
- 一个能执行 [SKILL.md](../SKILL.md) 的 Agent 环境（Claude Code / OpenClaw / Hermes 等），或你自己的 Agent runtime

```bash
# 自检：环境不完整时它会告诉你缺什么
python3 scripts/cangjie.py doctor
```

**输入准备**（开始前必须拿到手）：

1. **内容文本**：PDF / EPUB / TXT / 字幕 / 转写稿的文件路径。没有文本就不要开工——凭记忆蒸馏是质量红线
2. **元信息**：书 = 「书名 + 作者 + 出版年」；视频/播客 = 「标题 + 作者 + 发布时间」
3. **使用目的**：自己学习查阅 → 倾向 single；要接入工作流、跨书组合 → 倾向 pack（不确定就先 single）
4. 给书起一个 slug（小写英文+连字符，如 `poor-charlies-almanack`），后面所有产物都在 `books/<slug>/` 下

## 1. 启动蒸馏

在 Agent 环境里调用本 Skill（即 `SKILL.md`），把上面的输入交给它。Agent 会**严格按顺序**执行 7 个阶段，每个阶段产出一组可核对的文件。

> **断点续跑**：流程状态记录在 `books/<slug>/PIPELINE_STATE.md`。中断后重新启动时 Agent 会读取它，从上次阶段继续，不会从头重跑。

## 2. 七个阶段各自做什么、产出什么

| 阶段 | 做什么 | 你能核对到的产物 |
|---|---|---|
| 0 整书理解 | Adler 四步分析（结构/解释/批判/应用） | `books/<slug>/BOOK_OVERVIEW.md` |
| 1 并行提取 | 5 个 sub-agent（框架/原则/案例/反例/术语）同时提取 | `books/<slug>/candidates/<type>.md` |
| 1.5 三重验证 | 来源充分性 / 可执行性 / 任务增益逐条判定 | `verified.md`、`coverage-audit.md`、`rejected/` |
| 1.6 晋级门 | 判断哪些单元值得成为独立 Skill | `.cangjie/capabilities/destinations.json` |
| 2 RIA++ 构造 | 每个单元生成 R/I/A1/A2/E/B 六段能力卡 | `.cangjie/capabilities/cards/<slug>.md` + `verified.yaml` |
| 3 Zettelkasten | 能力间引用 + 全书术语词典 | `GLOSSARY.md`、Bundle 中的 `also_read` |
| 4 压力测试 | 晋级能力测触发、router 能力测可达，且要**实际完成任务** | 评测记录（未过的回炉阶段 2） |
| 5 编译交付 | 生成 DIGEST + 编译 Skill Pack | `DIGEST.md` + 安装目录产物 |

**每个阶段结束都值得停下来看一眼**：

- 阶段 0 后确认骨架理解是否正确、有无想突出的方向
- 阶段 1.5 后有四类清单（可执行/参考/待核查/淘汰），确认没有你想保留却被淘汰的内容
- 阶段 1.6 后检查晋级决定是否符合你的使用预期

## 3. 迷你案例：一份 3 页文本会经历什么

假设输入是一份 3 页的《谈判》课程讲义（`books/negotiation-notes/`）：

1. **阶段 0**：`BOOK_OVERVIEW.md` 识别出全篇围绕「开价—让步—收尾」三段结构，关键任务 4 个（如"设计开价区间"）
2. **阶段 1**：框架提取器拿到 1 个「三段式谈判流程」；原则提取器拿到 2 条（如"让步幅度递减"）；术语提取器拿到「ANCHOR」等 3 个概念；案例/反例提取器因讲义无实例而产出空
3. **阶段 1.5**：5 个候选中 4 个通过（都能定位原文、可执行、有增益）；1 条来源不充分转入 `needs-review.md`
4. **阶段 1.6**：只有「三段式谈判流程」满足独立意图/契约/运行 → 晋级为独立 Skill；其余归入 router
5. **阶段 2-4**：生成 1 张晋级能力卡 + 3 张 router 能力卡；压力测试用"对方向我报价 80 万，我的底价 65 万"这类新输入实际跑任务并核对输出
6. **阶段 5**：编译为 1 个来源路由入口 + 1 个晋级 Skill，`doctor` + staging 校验通过后发布

小输入不会产出很多 Skill，这是正常的——**覆盖审计**会说明原书关键任务是否都有着落，而不是靠凑数量。

## 4. 编译、安装与验证

```bash
# 阶段 5 由 Agent 发起；也可以手动执行（--output auto 会给出 single/pack 推荐）
python3 scripts/cangjie.py compile --bundle books/negotiation-notes/.cangjie/capabilities --out <目标目录> --output auto
```

- `--output single`：1 个入口 + 能力卡，适合学习查阅
- `--output pack`：1 个来源路由入口 + 少量晋级 Skill，适合接入日常工作流
- 编译走 **staging + 原子发布**：校验不过（如 broken-ref 硬闸门）会保留 staging 供排查，**坏产物不会流入发布目录**
- 安装位置由你确认后复制/symlink 过去；发布哈希登记在 `.cangjie/`，手改发布物会被检出

```bash
# 出问题先回滚到最近快照（--list 可查看）
python3 scripts/cangjie.py rollback --pack books/<slug>/.cangjie/capabilities --list
```

## 5. 实战技巧

- **大书先建索引**：超出单 sub-agent 上下文的长文本，流程会按分块策略处理并建立 `.cangjie/index/` 内容索引；有索引时检索式提取器取块更准
- **视频/播客先转写**：先用转写工具拿到文本，章节字段填时间戳/集数，保证可追溯
- **没有并行 sub-agent 环境**：5 个提取器可以**串行**跑，产出格式不变，只是慢
- **Skill 太多撑爆上下文**：优先 single / 让晋级门严格一点；装了大量 pack 后可参考渐进式披露类方案管理索引开销（见 issue #20 的讨论）
- **质量红线是硬的**：凭记忆蒸馏、跳过三重验证、未过压力测试就声明通过——任一发生都应停止交付
- **更新已蒸馏的书**：用 `python3 scripts/cangjie.py update --pack books/<slug>/.cangjie/capabilities --add <新来源>` 登记新来源，它会做 diff → change-set → 影响分析，生成待处理任务而不是直接覆盖

## 6. 常见问题

| 现象 | 处理 |
|---|---|
| `cangjie.py` 一跑就 ImportError | 缺 PyYAML：`python3 -m pip install pyyaml`；`doctor` 在缺依赖时仍可运行 |
| 编译报 `[broken-ref]` + `[hard-gate]` | Bundle 里有指向不存在文件的引用；按错误信息修 `verified.yaml`（staging 已保留） |
| 候选很少 | 先看 `coverage-audit.md`：是书本身方法论密度低，还是提取遗漏；后者补读/全量扫描重跑阶段 1 |
| 阶段中断 | 直接重启，Agent 会从 `PIPELINE_STATE.md` 续跑 |
