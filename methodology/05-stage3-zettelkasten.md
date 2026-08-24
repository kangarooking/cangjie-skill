# 阶段 3 — Zettelkasten 链接 + INDEX

## 目标

把原子 skill 之间的关系显式化,形成一个可导航的网络,而不是一堆孤立文件。

本阶段还有一个新增目标: **术语反向注入**。意思是先生成全书共享 `GLOSSARY.md`,再把每个 skill 实际用到的作者特定术语回填到该 skill 内部。这样单个 skill 被独立调用时,也不会因为脱离全书语境而失义。

## 三类关系

1. **依赖 (depends-on)**: A 的使用前提是先理解 B
   - 例: "检查清单决策" 依赖 "多元思维模型" (因为清单的项来自模型)

2. **对比 (contrasts-with)**: A 和 B 是两种可选方案,看情境选一
   - 例: "正向推理" 对比 "逆向思维"

3. **组合 (composes-with)**: A 和 B 经常配合使用
   - 例: "能力圈判断" 组合 "安全边际"

## 执行步骤

1. 列出阶段 2 产出的所有 skill。
2. 两两扫描,识别是否存在上述三类关系。
3. 在每个 skill 的 frontmatter `related_skills` 字段填入:
   ```yaml
   related_skills:
     - slug: multi-mental-models
       relation: depends-on
     - slug: forward-reasoning
       relation: contrasts-with
   ```
4. 在每个 skill 的 `SKILL.md` 末尾追加"相关 skills"段,用自然语言说明关系。
5. **回填 A2**: 链接关系确定后,回到每个 skill 的 A2 段,把阶段 2 留下的"与相邻 skill 的区分"初稿改成定稿 (同时同步 frontmatter `description`)。
6. 生成 `books/<slug>/INDEX.md` (模板 `templates/INDEX.md.template`)。
7. 把 `candidates/glossary.md` 整理提升为 `books/<slug>/GLOSSARY.md` — 它是所有 skill 共享的术语词典,应在产出根目录可见,而不是埋在审计目录里; INDEX.md 中链接它。
8. 执行术语反向注入: 扫描每个 skill 正文,凡出现 `GLOSSARY.md` 中的作者特定术语,在该 skill 末尾追加"本 skill 术语表"。

## 术语反向注入规则

### 为什么要做

`GLOSSARY.md` 是全书共享词典,适合读者浏览整包 skill。但 agent 实际调用时,常常只读取某一个 skill 的 `SKILL.md`。如果这个 skill 使用了作者自定义术语,却没有解释,agent 可能会按普通词义理解,导致执行偏差。

### 怎么做

1. 从 `GLOSSARY.md` 中筛出作者特定术语,不要收录普通词。
2. 扫描每个 skill 的 R / I / A1 / A2 / E / B 六段。
3. 如果某个 skill 使用了术语,在该 skill 末尾加入:

   ```markdown
   ## 本 skill 术语表

   - **{{术语 1}}**: {{一句话解释,使用作者在本书中的含义}}
   - **{{术语 2}}**: {{一句话解释}}
   ```

4. 每个 skill 只注入实际用到的 2–5 条术语。
5. 如果某个 skill 没有用到作者特定术语,不要硬加术语表。

### 质量要求

- 术语解释必须来自 `GLOSSARY.md`,不能在单个 skill 中重新发明定义。
- 每条解释用一句话,只解释当前 skill 执行所需的含义。
- 不要把 `GLOSSARY.md` 全量复制进每个 skill,否则会让 skill 变得臃肿。

## INDEX.md 必须包含

- 书的基本信息 (作者/年份/一句话主旨)
- 所有 skill 的列表,按主题分组
- 引用图 (mermaid flowchart 或 graph)
- 推荐学习顺序 (从依赖关系推出)
- 术语词典链接: `GLOSSARY.md`
- 质量记分卡链接: `SCORECARD.md` (阶段 5 生成后回填)

## 记分卡指标

本阶段结束时,为阶段 5 的 `SCORECARD.md` 暂存以下数据:

- skill 总数
- 关系总数
- depends-on / contrasts-with / composes-with 数量
- 每个 skill 注入的术语数
- 未使用术语表的 skill 数

## 节制原则

**不要硬造关系**。如果两个 skill 之间没有真正的依赖/对比/组合关系,就不要写 related_skills。宁可稀疏也不要制造虚假链接。

一个经验值: 一本书拆出 10 个 skill,合理的关系数大约是 8–15 条。低于 5 条说明拆得太独立 (可能单元选得不对),高于 25 条说明在硬凑关系。

术语注入也要节制: 每个 skill 只保留理解和执行它真正需要的术语。