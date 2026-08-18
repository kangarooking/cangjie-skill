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
3. 在每个 skill 的 SKILL.md 末尾“相关 skills”段写入结构化列表,例如 `depends-on: multi-mental-models`、`contrasts-with: forward-reasoning`,并用自然语言解释关系。不要把扩展字段写入 frontmatter。
4. 检查相关 skill 名称与实际目录一致,不存在的关系不得写入
5. **回填 A2**: 链接关系确定后,回到每个 skill 的 A2 段,把阶段 2 留下的"与相邻 skill 的区分"初稿改成定稿 (同时同步 frontmatter `description`)
6. 生成 `books/<slug>/INDEX.md` (模板 `templates/INDEX.md.template`)
7. 把 `candidates/glossary.md` 整理提升为 `books/<slug>/GLOSSARY.md` — 它是所有 skill 共享的术语词典,应在产出根目录可见,而不是埋在审计目录里; INDEX.md 中链接它

## INDEX.md 必须包含

- 书的基本信息 (作者/年份/一句话主旨)
- 所有 skill 的列表,按主题分组
- 引用图 (mermaid flowchart 或 graph)
- 推荐学习顺序 (从依赖关系推出)

## 节制原则

**不要硬造关系**。如果两个 skill 之间没有真正的依赖/对比/组合关系,就不要写关系条目。宁可稀疏也不要制造虚假链接。

一个经验值: 一本书拆出 10 个 skill,合理的关系数大约是 8–15 条。低于 5 条说明拆得太独立 (可能单元选得不对),高于 25 条说明在硬凑关系。
