# {{BOOK_TITLE}} — Skill Index

> 本书由 book2skill 蒸馏, 共产出 **{{N}}** 个 skills。
> 处理时间: {{DATE}}

## 关于这本书

- **作者**: {{AUTHOR}}
- **出版年**: {{YEAR}}
- **一句话主旨**: {{ONE_LINE_THEME}}
- **整书理解**: 见 [BOOK_OVERVIEW.md](./BOOK_OVERVIEW.md)

---

## Skill 列表 (按主题分组)

### {{主题 1}}

- [`{{skill-slug-1}}`](./{{skill-slug-1}}/SKILL.md) — {{一句话描述}}
- [`{{skill-slug-2}}`](./{{skill-slug-2}}/SKILL.md) — {{一句话描述}}

### {{主题 2}}

- [`{{skill-slug-3}}`](./{{skill-slug-3}}/SKILL.md) — {{一句话描述}}

---

## 引用图

```mermaid
graph LR
    A[skill-a] -->|depends-on| B[skill-b]
    A -.->|contrasts-with| C[skill-c]
    B ===>|composes-with| D[skill-d]
```

图例:
- `-->`  depends-on
- `-.->` contrasts-with
- `===>` composes-with

---

## 推荐学习顺序

(从依赖图的叶子节点开始, 向上)

1. **{{skill-a}}** — 最基础, 没有前置
2. **{{skill-b}}** — 依赖 skill-a
3. **{{skill-c}}** — 依赖 skill-a, 与 skill-b 互补
...

---

## 接入 darwin-skill

所有 skill 均带有 `test-prompts.json` (darwin-skill 兼容格式), 可直接接入自动进化:

```
darwin evolve books/{{book-slug}}/
```

---

## 审计轨迹

- 候选单元池: [candidates/](./candidates/)
- 被淘汰的候选 (含原因): [rejected/](./rejected/)
- BOOK_OVERVIEW: [BOOK_OVERVIEW.md](./BOOK_OVERVIEW.md)
