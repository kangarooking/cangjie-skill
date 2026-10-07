# 阶段 5 — 编译与交付 (compile + DIGEST + 安装)

## 目标

把流水线的产出真正送到两类使用者手里:

1. **Agent** — Capability Bundle 必须被编译成 single 或 compact pack,并安装到宿主环境的 skills 目录,否则永远不会被调用
2. **人类读者** — 用一篇 `DIGEST.md` 精华长文承接"不想读全书,但想看精华"的需求

这两件事都不做,前面五个阶段的产出就只是一堆躺在仓库里的文件。

## 第 0 步 — 从 Bundle 编译产物（v2.1）

```bash
python3 scripts/cangjie.py compile \
  --bundle books/<slug>/.cangjie/capabilities \
  --out dist/<slug> --output auto
```

1. auto 决策器按 single-first-v1 策略给出推荐（decision report 一屏展示理由与备选）;
2. 把报告给用户轻确认: **按推荐 / 改成 single / 改成 pack** — 默认值只是推荐,不能取消用户显式选择;
3. 确认后加 `--yes`（或显式 `--output`）执行。编译器自动做 staging 校验、发布哈希登记与原子发布;
4. 编译产物必须通过 `validate_skill_pack.py`（编译器已内置为硬门）。
5. `update` / `repair` 默认沿用本次决策,不因新增材料静默改变产物形态;重新选型走 `replan-output --dry-run`。

## 第 1 步 — 生成 DIGEST.md (面向读者的精华长文)

### 为什么放在最后而不是阶段 0

阶段 0 的 `BOOK_OVERVIEW.md` 是**流水线的全局上下文**,会被喂给每个 sub-agent — 它必须精炼,不能为了可读性加长。而 DIGEST 面向人类读者,放在流程终点写,手里的材料最全:

- `BOOK_OVERVIEW.md` — 骨架 / 术语 / 批判
- `verified.md` — 通过三重验证的方法论 (已经筛掉了水分)
- 各 skill 的 SKILL.md — 每个方法论的解释 / 案例 / 边界
- `candidates/cases.md` / `counter-examples.md` — 案例池和反例池
- `GLOSSARY.md` — 术语词典

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

## 第 2 步 — 安装编译产物到宿主环境

编译输出目录（如 `dist/<slug>/`）只是构建产物,宿主 (Claude Code / Cursor 等) 不会从这里加载 skill。必须安装:

1. **问用户装哪里** (一次性问清,不要逐个 skill 问):
   - 用户级: `~/.claude/skills/` (所有项目可用)
   - 项目级: `<project>/.claude/skills/` 或 `.cursor/skills/`
   - 用户也可能只想要仓库形式 (发布到 GitHub),那就跳过安装
2. **single 模式**: 复制整个入口目录（含 `references/`）,1 个可发现入口;
   **pack 模式**: 分别复制来源路由入口目录和各晋级 Skill 目录（`capability-destinations.json` 是审计清单,不必安装）
3. **只安装通过阶段 4 测试的产物** — 未通过的留在构建目录里回炉
4. 安装后抽 1–2 个入口用一句 should_trigger 的 prompt 验证宿主能加载并触发;pack 模式另抽 1 条 router 意图验证路由入口
5. **不要同时安装同一本书的 single 和 pack** — 两套 description 会重复覆盖意图,二选一

## 第 3 步 — 收尾汇报

告诉用户:

> 已完成。产出: N 个 skill (已安装到 <位置>)、INDEX.md、GLOSSARY.md、DIGEST.md (精华长文,约 X 字)。
> 如需持续进化,可以喂给 darwin-skill: `darwin evolve books/<slug>/`
> 它会用这里的 test-prompts.json 做 ratcheting 自动进化。

最后把 `PIPELINE_STATE.md` 标记为全部完成。
