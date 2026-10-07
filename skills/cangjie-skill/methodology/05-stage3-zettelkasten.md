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

## 执行步骤（v2.1 Bundle 版）

1. 列出阶段 2 登记进 Capability Bundle 的所有能力
2. 两两扫描,识别是否存在上述三类关系
3. 把关系写入 `verified.yaml` 中各能力的 `also_read` 字段（能力卡编译时生成"补读"列）;
   依赖/对比/组合的语义说明写在能力卡末尾的"相关能力"段
4. **回填 A2**: 链接关系确定后,回到每张能力卡的 A2 段,把阶段 2 留下的"与相邻能力的区分"
   初稿改成定稿 (同时同步 Bundle 中该能力的 `frontmatter.description`)
5. 把 `candidates/glossary.md` 整理提升为 `books/<slug>/GLOSSARY.md`,并复制到
   `.cangjie/capabilities/book/glossary.md`（编译时随产物分发）
6. 路由表 / 能力索引（capability-index.md）由 `cangjie.py compile` 从 Bundle 自动生成,
   **不再手写 INDEX.md**;legacy-pack 流程仍可用 `templates/INDEX.md.template`

## 编译生成的能力索引必须包含

- 书的基本信息 (作者/年份/一句话主旨)
- 所有能力的列表,按主题分组
- 意图/关键词 → 能力卡的映射
- 推荐学习顺序 (从依赖关系推出)

## 节制原则

**不要硬造关系**。如果两个 skill 之间没有真正的依赖/对比/组合关系,就不要写 related_skills。宁可稀疏也不要制造虚假链接。

一个经验值: 一本书拆出 10 个 skill,合理的关系数大约是 8–15 条。低于 5 条说明拆得太独立 (可能单元选得不对),高于 25 条说明在硬凑关系。
