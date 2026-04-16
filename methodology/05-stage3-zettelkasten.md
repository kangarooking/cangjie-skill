# 阶段 3 — Zettelkasten 链接 + INDEX

## 目标

把原子 skill 之间的关系显式化,形成一个可导航的网络,而不是一堆孤立文件。

## 三类关系

1. **依赖 (depends-on)**: A 的使用前提是先理解 B
   - 例: "检查清单决策" 依赖 "多元思维模型" (因为清单的项来自模型)

2. **对比 (contrasts-with)**: A 和 B 是两种可选方案,看情境选一
   - 例: "正向推理" 对比 "逆向思维"

3. **组合 (composes-with)**: A 和 B 经常配合使用
   - 例: "能力圈判断" 组合 "安全边际"

## 执行步骤

1. 列出阶段 2 产出的所有 skill
2. 两两扫描,识别是否存在上述三类关系
3. 在每个 skill 的 frontmatter `related_skills` 字段填入:
   ```yaml
   related_skills:
     - slug: multi-mental-models
       relation: depends-on
     - slug: forward-reasoning
       relation: contrasts-with
   ```
4. 在每个 skill 的 SKILL.md 末尾追加"相关 skills"段,用自然语言说明关系
5. 生成 `books/<slug>/INDEX.md` (模板 `templates/INDEX.md.template`)

## INDEX.md 必须包含

- 书的基本信息 (作者/年份/一句话主旨)
- 所有 skill 的列表,按主题分组
- 引用图 (mermaid flowchart 或 graph)
- 推荐学习顺序 (从依赖关系推出)

## 节制原则

**不要硬造关系**。如果两个 skill 之间没有真正的依赖/对比/组合关系,就不要写 related_skills。宁可稀疏也不要制造虚假链接。

一个经验值: 一本书拆出 10 个 skill,合理的关系数大约是 8–15 条。低于 5 条说明拆得太独立 (可能单元选得不对),高于 25 条说明在硬凑关系。
