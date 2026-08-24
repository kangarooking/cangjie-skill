# 阶段 5 — 交付 (DIGEST + SCORECARD + 安装)

## 目标

把流水线的产出真正送到两类使用者手里,并留下可复盘的质量记录:

1. **Agent** — skill 必须被安装到宿主环境的 skills 目录,否则永远不会被调用
2. **人类读者** — 用一篇 `DIGEST.md` 精华长文承接"不想读全书,但想看精华"的需求
3. **维护者** — 用一份 `SCORECARD.md` 记录本次流水线质量,便于以后比较和改进

这三件事都不做,前面五个阶段的产出就只是一堆躺在仓库里的文件。

## 第 1 步 — 生成 DIGEST.md (面向读者的精华长文)

### 为什么放在最后而不是阶段 0

阶段 0 的 `BOOK_OVERVIEW.md` 是**流水线的全局上下文**,会被喂给每个 sub-agent — 它必须精炼,不能为了可读性加长。而 DIGEST 面向人类读者,放在流程终点写,手里的材料最全:

- `BOOK_OVERVIEW.md` — 骨架 / 术语 / 批判
- `verified.md` — 通过三重验证的方法论 (已经筛掉了水分)
- 各 skill 的 `SKILL.md` — 每个方法论的解释 / 案例 / 边界
- `candidates/cases.md` / `counter-examples.md` — 案例池和反例池
- `GLOSSARY.md` — 术语词典
- `SCORECARD.md` — 质量指标 (生成后可反向链接)

**DIGEST 是"蒸馏后的再呈现",不是"重新摘要"** — 它只写通过了验证的内容,所以浓度天然高于普通书摘。

### 篇幅与结构要求

- **篇幅**: 5000–10000 字 (视内容体量伸缩; 一篇 20 分钟视频不必硬凑 5000 字)
- **组织**: 按书的骨架 (BOOK_OVERVIEW 的一级论点) 组织章节,不按 skill 列表组织 — 读者要的是"这本书讲了什么",不是产物清单
- 每个核心方法论写一小节: 它解决什么问题 → 核心逻辑 → 书中最有代表性的案例 → 什么时候会失效
- 必须包含**反例/陷阱**一节 (来自 counter-examples) 和**作者的局限**一节 (来自阶段 0 批判) — 只报喜不报忧的精华是软文,不是蒸馏
- 每个方法论小节末尾链接对应的 skill 目录,读者想深入时有路径
- 允许适量引用原文金句 (每段引用遵守 ≤150 字 / 英文 ≤100 词)

模板: `templates/DIGEST.md.template`,输出到 `books/<slug>/DIGEST.md`。

### 质量自检

- [ ] 一个没读过原书的人,读完 DIGEST 能复述这本书的主旨、3 个以上核心方法论、2 个以上陷阱
- [ ] 没有出现"未通过三重验证"的内容被当作核心方法论呈现
- [ ] 有批判/局限部分,不是全程吹捧
- [ ] 每个方法论小节都有 skill 链接

## 第 2 步 — 生成 SCORECARD.md (流水线质量记分卡)

`SCORECARD.md` 是给维护者看的质量记录。它不评价一本书"好不好",而是记录这次蒸馏流程是否健康。

模板: `templates/SCORECARD.md.template`,输出到 `books/<slug>/SCORECARD.md`。

### 必须汇总的指标

- 内容信息: 标题、作者、内容体量分级、处理日期
- 候选统计: 原始候选数、去重后候选数、通过数、淘汰数
- 验证统计: 验证通过率、双评审一致率、仲裁数、A/B/C 证据等级分布
- 链接统计: skill 总数、关系总数、三类关系分布、术语注入数量
- 测试统计: 测试用例总数、四类测试分布、首轮通过率、最终通过率、回炉次数
- 风险记录: fallback 自测、低一致率、诱饵失败、执行质量失败、版权注意点
- 下一步建议: 是否适合交付、是否需要重跑某阶段、是否建议进入 darwin-skill 进化

### 为什么要做

没有记分卡时,每次蒸馏质量只能凭感觉判断。`SCORECARD.md` 把流程健康度变成可比较的数据。以后如果改了 SOP,可以比较新旧版本是否真的提高了通过率、一致率和执行质量。

## 第 3 步 — 安装 skill 到宿主环境

产出目录 `books/<slug>/<skill-slug>/` 只是构建产物,宿主 (Claude Code / Cursor 等) 不会从这里加载 skill。必须安装:

1. **问用户装哪里** (一次性问清,不要逐个 skill 问):
   - 用户级: `~/.claude/skills/<skill-slug>/` (所有项目可用)
   - 项目级: `<project>/.claude/skills/<skill-slug>/` 或 `.cursor/skills/<skill-slug>/`
   - 用户也可能只想要仓库形式 (发布到 GitHub),那就跳过安装
2. **只安装通过阶段 4 测试的 skill** — 未通过的留在构建目录里回炉
3. 复制 (或 symlink) 整个 skill 目录,含 `SKILL.md` 和 `test-prompts.json`
4. 安装后抽 1–2 个 skill 用一句 should_trigger 的 prompt 验证宿主能加载并触发

## 第 4 步 — 收尾汇报

告诉用户:

> 已完成。产出: N 个 skill (已安装到 <位置>)、INDEX.md、GLOSSARY.md、DIGEST.md (精华长文,约 X 字)、SCORECARD.md (质量记分卡)。
> 如需持续进化,可以喂给 darwin-skill: `darwin evolve books/<slug>/`
> 它会用这里的 test-prompts.json 做 ratcheting 自动进化。

最后把 `PIPELINE_STATE.md` 标记为全部完成。