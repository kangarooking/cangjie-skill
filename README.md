# Cangjie Skill

A generator workflow for turning books into reusable AI skills.

`cangjie-skill` is the upstream toolchain behind the published book skill packs in this workspace. Its job is not to be a single end-user skill. Its job is to generate other skills systematically.

## 它是做什么的

`cangjie-skill` 把一本长文本材料拆成一套可调用的 AI skills。它解决的不是“怎么回答一个问题”，而是“怎么把一本书里的方法论稳定地变成一组技能模块”。

## 它做了哪些事情

- 抽取原则、框架、案例、反例、术语
- 做候选单元筛选和验证
- 把合格的方法论单元转成统一格式的 `SKILL.md`
- 给 skill 建立引用关系和导航结构
- 生成 `BOOK_OVERVIEW.md`、`INDEX.md`、`test-prompts.json`

## 生成流程

当前仓库里的工作流分为这些阶段：

1. `Stage 0`: understanding the whole book
2. `Stage 1`: parallel extraction of candidate units
3. `Stage 1.5`: validation and filtering
4. `Stage 2`: RIA++ skill construction
5. `Stage 3`: Zettelkasten-style linking
6. `Stage 4`: pressure testing

## 它已经生成了什么

- `poor-charlies-almanack-skill`
- `no-rules-rules-skill`

后续还可以继续生成更多书本 skill packs。

## 效果示例

### 示例 1

**用户需求**

“我想把一本书里的核心方法论抽成可复用的 AI skills，而不是只做读书摘要。”

**cangjie-skill 如何判断**

- 先看源材料是否存在可重复调用的方法论单元
- 再区分哪些内容适合做独立 skill，哪些只适合做候选或背景
- 最后输出结构化 skill 仓库，而不是一篇总结文章

**最终输出示例**

“输出将不是一个单文件摘要，而是一个多 skill 仓库：包含 `BOOK_OVERVIEW.md` 作为全局理解，`INDEX.md` 作为技能地图，若干 `*/SKILL.md` 作为独立模块，以及 `test-prompts.json` 用于验证触发场景。” 

### 示例 2

**用户需求**

“我不希望这本书只变成一个很长的说明文，我想要可以在 agent 里复用的技能包。”

**cangjie-skill 如何判断**

- 判断目标不是内容总结，而是结构化复用
- 优先生成可触发、可组合、可测试的 skill 单元
- 对没有独立价值的内容进行淘汰，不强行保留

**最终输出示例**

“系统会把内容拆成多个带触发条件、适用边界、使用方式和关联关系的 skills，而不是把整本书压缩成一篇泛化总结。” 

## 仓库结构

```text
cangjie-skill/
├── README.md
├── README.en.md
├── README.ja.md
├── LICENSE
├── GITHUB_REPO.md
├── SKILL.md
├── methodology/
├── extractors/
└── templates/
```

## More Skills

- `poor-charlies-almanack-skill`
  `https://github.com/kangarooking/poor-charlies-almanack-skill`
- `no-rules-rules-skill`
  `https://github.com/kangarooking/no-rules-rules-skill`

## License

MIT. See [LICENSE](./LICENSE).
