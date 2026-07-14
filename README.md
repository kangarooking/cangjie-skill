<div align="center">

# Cangjie Skill

### 把书、长视频、播客里的方法论，蒸馏成可调用的 AI Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-f5c542.svg)](./LICENSE)
[![Method: RIA--TV++](https://img.shields.io/badge/Method-RIA--TV++-2ea44f.svg)](./SKILL.md)
[![Platform: OpenClaw](https://img.shields.io/badge/Platform-OpenClaw-1677ff.svg)](https://github.com/openclaw/openclaw)
[![Platform: Claude Code](https://img.shields.io/badge/Platform-Claude%20Code-f97316.svg)](https://code.claude.com/)

**读完、看完、听完之后，带走一套能调用的方法论。**

</div>

## 为什么做这件事

最近有一个很火的 idea：把同事蒸馏成 skill。即便一个人离职了，他的经验、语气、工作方式都会被 AI 一定程度替代。[nuwa-skill](https://github.com/alchaincyf/nuwa-skill) 就是做这件事的——创造"人类 skill"，比如马斯克 skill、巴菲特 skill。配套的 [darwin-skill](https://github.com/alchaincyf/darwin-skill) 负责让这些 skill 自动进化。

蒸馏人很有价值——nuwa-skill 已经证明了这一点。而蒸馏人**系统性表达过的内容**，则是另一个维度的补充：一本书、一场长访谈、一期播客、一个 B 站或 YouTube 长视频，都可能沉淀了作者花很长时间打磨出来的方法论。比起模仿一个人的表达方式，把他系统性输出的方法论拆出来、变成可以帮人解决实际问题的工具，同样是很有价值的事。

而且还有一个真实的痛点：你可能看了很多书、收藏了很多视频、听过很多播客，但就是运用不起来。尤其是各大平台每天都有大量干货长视频，时效性很强，内容又很长；它们往往不可能已经被 AI 训练过，也很难靠一次观看完整吸收。把这些内容蒸馏成 skill 之后，AI agent 可以帮你在真实场景中调用这些知识，而不是让它们躺在笔记、收藏夹或稍后再看列表里落灰。

所以 cangjie-skill 的目标很明确：**蒸馏所有值得蒸馏的高价值内容**。它不只适用于书，也适用于有字幕/转写文本的视频、播客、访谈、演讲、课程、长文和资料集。只要内容里存在可抽取、可验证、可迁移的方法论，就可以用 cangjie-skill 把它变成一套可独立调用、可组合使用、可压力测试的 AI skill 工具包。

如果要蒸馏视频内容，建议搭配 [video-downloader](https://github.com/kangarooking/kangarooking-skills/tree/main/video-downloader) skill 一起使用：先用它下载视频、提取字幕/音频转写和关键素材，再把得到的文本内容交给 cangjie-skill 做方法论抽取、skill 化和压力测试。

## 它解决了什么问题

- 看了很多书、视频、播客但用不起来——知识停留在"看过/听过/收藏过"层面，无法在真实决策中被调用
- 摘要、笔记、字幕整理只是压缩，不是结构化复用——读完/看完还是不知道"什么时候该用什么"
- 高价值内容里真正值得变成工具的内容只有一小部分——需要严格的筛选而不是照单全收
- 现有的阅读/观看/听课方法论都是给人看的，不是给 agent 用的——需要面向执行而非面向消费的蒸馏方法

## 它是怎么工作的

cangjie-skill 使用 **RIA-TV++** 流水线，把书籍、视频转写、播客文字稿、访谈记录等原始文本变成一组结构化的 skill。整个过程分七个阶段：

1. **整体内容理解（Adler 分析）**——借鉴 Mortimer Adler 的分析阅读法，对整份内容做结构、解释、批判、应用四步拆解，产出 `BOOK_OVERVIEW.md`
2. **并行提取**——同时派 5 个专项提取器（框架、原则、案例、反例、术语），从原文中提取候选方法论单元
3. **三重验证筛选**——每个候选必须通过三项检验：原内容中至少有 2 处独立佐证（跨域）、能回答内容里未明说的新问题（预测力）、不是常识（独特性）。通过率通常只有 25-50%
4. **RIA++ 构造**——将验证通过的内容按 R（原文引用）/ I（用自己的话重写）/ A1（书中案例）/ A2（未来触发场景）/ E（可执行步骤）/ B（边界与盲点）六个维度结构化
5. **Zettelkasten 链接**——找出 skill 之间的依赖、对比、组合关系，生成 `INDEX.md` 和引用图
6. **压力测试**——为每个 skill 设计包含诱饵题的测试用例（含跨 skill 混淆测试），未通过的回炉重做
7. **交付**——生成面向读者的 `DIGEST.md` 精华长文（不想读全书？看这篇就够），并把通过测试的 skill 安装到 Claude Code / Cursor 的 skills 目录，让它们真正可被调用

RIA-TV++ 这个名字拆开看：
- **RIA**：来自赵周《这样读书就够了》的便签拆书法（Reading / Interpretation / Appropriation）
- **TV**：Triple Verification，三重验证
- **++**：面向 agent 执行的扩展——E（Execution 可执行步骤）+ B（Boundary 边界）

## 效果示例

### 示例 1：从一本书/长视频到一套 skill 工具包

**用户需求**

"我想把一本书或一个 B 站/YouTube 长视频里的核心方法论抽成可复用的 AI skills，而不是只做摘要。"

**cangjie-skill 如何判断**

- 先看源材料是否存在可重复调用的方法论单元
- 再区分哪些内容适合做独立 skill，哪些只适合做候选或背景
- 最后输出结构化 skill 仓库，而不是一篇总结文章

**最终输出示例**

> 输出将不是一个单文件摘要，而是一个多 skill 仓库：包含 `BOOK_OVERVIEW.md` 作为全局理解，`INDEX.md` 作为技能地图，`DIGEST.md` 作为面向读者的精华长文，`GLOSSARY.md` 作为术语词典，若干 `*/SKILL.md` 作为独立模块，以及 `test-prompts.json` 用于验证触发场景。

### 示例 2：不是压缩，是结构化复用

**用户需求**

"我不希望这份内容只变成一个很长的说明文，我想要可以在 agent 里复用的技能包。"

**cangjie-skill 如何判断**

- 判断目标不是内容总结，而是结构化复用
- 优先生成可触发、可组合、可测试的 skill 单元
- 对没有独立价值的内容进行淘汰，不强行保留

**最终输出示例**

> 系统会把内容拆成多个带触发条件、适用边界、使用方式和关联关系的 skills，而不是把整份内容压缩成一篇泛化总结。

## 已生成的 skill packs

| 仓库 | 来源 | Skills 数 |
|------|------|-----------|
| [buffett-letters-skill](https://github.com/kangarooking/buffett-letters-skill) | 巴菲特致股东的信（1957-2023） | 20 |
| [cognitive-dividend-skill](https://github.com/kangarooking/cognitive-dividend-skill) | 《认知红利》 | 15 |
| [duan-yongping-skill](https://github.com/kangarooking/duan-yongping-skill) | 段永平投资问答录（商业逻辑+投资逻辑） | 15 |
| [viral-copywriting-skill](https://github.com/kangarooking/viral-copywriting-skill) | 《爆款文案》 | 14 |
| [copywriters-handbook-skill](https://github.com/kangarooking/copywriters-handbook-skill) | 《文案创作完全手册》 | 12 |
| [contagious-skill](https://github.com/kangarooking/contagious-skill) | 《疯传》 | 15 |
| [influence-skill](https://github.com/kangarooking/influence-skill) | 《影响力》 | 12 |
| [1000-true-fans-skill](https://github.com/kangarooking/1000-true-fans-skill) | 《1000个铁粉》 | 13 |
| [system-prompt-skills](https://github.com/kangarooking/system-prompt-skills) | 165 个 AI 产品系统提示词 | 15 |
| [X-growth-skills](https://github.com/kangarooking/X-growth-skills) | X（Twitter）起号、内容增长、算法、互动与变现实战资料集 | 15 |
| [poor-charlies-almanack-skill](https://github.com/kangarooking/poor-charlies-almanack-skill) | 《穷查理宝典》 | 12 |
| [no-rules-rules-skill](https://github.com/kangarooking/no-rules-rules-skill) | 《不拘一格：网飞的自由与责任工作法》 | 10 |
| [huangdi-neijing-skill](https://github.com/kangarooking/huangdi-neijing-skill) | 《黄帝内经》（素问+灵枢） | 22 |
| [first-principles-skill](https://github.com/kangarooking/first-principles-skill) | 《第一性原理》 | 10 |
| [mao-selected-works-skill](https://github.com/kangarooking/mao-selected-works-skill) | 《毛泽东选集》第 1-5 卷 | 25 |
| [qbdx-hub/buffett-letters-skill](https://github.com/qbdx-hub/buffett-letters-skill) | 沃伦·巴菲特 1957-2023 年致股东信 | 20 |
| [qbdx-hub/wo-yu-di-tan-skill](https://github.com/qbdx-hub/wo-yu-di-tan-skill) | 史铁生《我与地坛》 | 6 |
| [qbdx-hub/mingchao-those-things-skill](https://github.com/qbdx-hub/mingchao-those-things-skill) | 当年明月《明朝那些事儿》 | 7 |
| [qbdx-hub/sunzi-bingfa-skill](https://github.com/qbdx-hub/sunzi-bingfa-skill) | 《孙子兵法》 | 8 |
| [qbdx-hub/zhouyi-skill](https://github.com/qbdx-hub/zhouyi-skill) | 《周易》 | 8 |
| [qbdx-hub/high-math-vol1-ch1-skill](https://github.com/qbdx-hub/high-math-vol1-ch1-skill) | 高等数学上册第一章 | 8 |

## 视频蒸馏区

这些仓库来自长视频、课程或视频合集的字幕/转写文本，适合展示 cangjie-skill 对非书籍内容的方法论蒸馏能力。

| 仓库 | 来源 | Skills 数 |
|------|------|-----------|
| [ai-for-everyone-skill](https://github.com/kangarooking/ai-for-everyone-skill) | 吴恩达《AI for Everyone / 给所有人的 AI 入门课》视频课程 | 25 |
| [loop-engineering-skill](https://github.com/kangarooking/loop-engineering-skill) | Loop Engineering 长视频合集 | 8 |

后续计划蒸馏更多高价值书籍。候选书单包括但不限于：君主论。

补充外部来源（经对方作者同意引入）：

- 来源仓库：[ace3000chao/book2startup](https://github.com/ace3000chao/book2startup)
- 书目包括：《精益创业》《孙子兵法》《庄子》《易经》
- 来源仓库：[shenqistart/book2skill](https://github.com/shenqistart/book2skill)
- 书目包括：《缠论》《茶经》

## 仓库结构

```text
cangjie-skill/
├── README.md              ← 你正在看的
├── README.en.md           ← English version
├── README.ja.md           ← 日本語版
├── LICENSE                ← MIT
├── SKILL.md               ← 元 skill 定义（cangjie-skill 的完整执行规范）
├── methodology/           ← RIA-TV++ 各阶段的方法论文档
├── extractors/            ← 5 个并行提取器的 prompt 定义
└── templates/             ← SKILL.md / INDEX.md / BOOK_OVERVIEW.md 模板
```

## 生态

cangjie-skill 是一个更大的 skill 生态的一部分：

- [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) — 蒸馏人（思维方式、表达 DNA）
- **cangjie-skill**（本仓库）— 蒸馏书（方法论、框架、原则）
- [darwin-skill](https://github.com/alchaincyf/darwin-skill) — 进化任意 skill

三者咬合：nuwa 蒸馏人，cangjie 蒸馏书，darwin 让它们持续进化。

## More Skills

- [Buffett Letters Skill](https://github.com/kangarooking/buffett-letters-skill) — 巴菲特 60+ 年致股东信的 20 个投资判断 skill
- [Poor Charlie's Almanack Skill](https://github.com/kangarooking/poor-charlies-almanack-skill) — 查理·芒格核心思维方法的 12 个决策与判断 skill
- [No Rules Rules Skill](https://github.com/kangarooking/no-rules-rules-skill) — 网飞自由与责任文化的 10 个组织设计 skill
- [Cognitive Dividend Skill](https://github.com/kangarooking/cognitive-dividend-skill) — 《认知红利》思维升级的 15 个认知工具 skill
- [Duan Yongping Skill](https://github.com/kangarooking/duan-yongping-skill) — 段永平投资问答录的 15 个商业与投资 skill
- [Viral Copywriting Skill](https://github.com/kangarooking/viral-copywriting-skill) — 《爆款文案》的 14 个销售型文案写作与诊断 skill
- [Copywriters Handbook Skill](https://github.com/kangarooking/copywriters-handbook-skill) — 《文案创作完全手册》的 12 个销售型文案、标题与卖点转化 skill
- [Contagious Skill](https://github.com/kangarooking/contagious-skill) — 《疯传》的 15 个 STEPPS 传播策略与口碑诊断 skill
- [Influence Skill](https://github.com/kangarooking/influence-skill) — 《影响力》的 12 个说服心理、顺从机制与防御判断 skill
- [1000 True Fans Skill](https://github.com/kangarooking/1000-true-fans-skill) — 《1000个铁粉》的 13 个个人品牌、铁粉养成与信任变现 skill
- [System Prompt Skills](https://github.com/kangarooking/system-prompt-skills) — 从 165 个 AI 产品系统提示词蒸馏出的 15 个 system prompt 设计 skill
- [X Growth Skills](https://github.com/kangarooking/X-growth-skills) — X 起号、内容、算法、互动、复盘与变现的 15 个运营 skill
- [Huangdi Neijing Skill](https://github.com/kangarooking/huangdi-neijing-skill) — 《黄帝内经》素问12+灵枢10共22个思维方法 skill
- [First Principles Skill](https://github.com/kangarooking/first-principles-skill) — 《第一性原理》的 10 个认知拆解、破界创新与组织刷新 skill
- [Mao Selected Works Skill](https://github.com/kangarooking/mao-selected-works-skill) — 《毛泽东选集》第 1-5 卷的 25 个认知、战略、组织与执行方法 skill
- [qbdx-hub Buffett Letters Skill](https://github.com/qbdx-hub/buffett-letters-skill) — 沃伦·巴菲特 1957-2023 年致股东信的 20 个投资与资本配置 skill
- [qbdx-hub Wo Yu Di Tan Skill](https://github.com/qbdx-hub/wo-yu-di-tan-skill) — 《我与地坛》的 6 个限制、苦难、写作与自我安放 skill
- [qbdx-hub Mingchao Those Things Skill](https://github.com/qbdx-hub/mingchao-those-things-skill) — 《明朝那些事儿》的 7 个权力结构、制度失灵与历史表达 skill
- [qbdx-hub Sunzi Bingfa Skill](https://github.com/qbdx-hub/sunzi-bingfa-skill) — 《孙子兵法》的 8 个战略判断、资源控制与行动选择 skill
- [qbdx-hub Zhouyi Skill](https://github.com/qbdx-hub/zhouyi-skill) — 《周易》的 8 个处境诊断、时位判断与进退边界 skill
- [qbdx-hub High Math Vol. 1 Chapter 1 Skill](https://github.com/qbdx-hub/high-math-vol1-ch1-skill) — 高等数学上册第一章的 8 个极限、无穷小与连续性学习 skill
- [book2startup](https://github.com/ace3000chao/book2startup) — 经作者同意引入的外部来源，包含《精益创业》《孙子兵法》《庄子》《易经》相关 skills
- [book2skill](https://github.com/shenqistart/book2skill) — 经作者同意引入的外部来源，包含《缠论》《茶经》相关 AI-Agent skills

## 贡献者

感谢以下贡献者对 cangjie-skill 生态的补充：

- [shenqistart](https://github.com/shenqistart) — 贡献外部 [book2skill](https://github.com/shenqistart/book2skill) 引用，并补充中英日 README 更新
- [qbdx-hub](https://github.com/qbdx-hub) — 贡献 6 个 Cangjie 整书/章节蒸馏示例仓库，并补充中英日 README 引用

## 关于作者

**袋鼠帝 kangarooking** — AI 博主，独立开发者。AI Top 公众号「袋鼠帝 AI 客栈」主理人

<img src="https://raw.githubusercontent.com/kangarooking/cangjie-skill/main/assets/wechat-personal-qr.jpg" width="220" alt="袋鼠帝个人微信二维码">

火山引擎领航 KOL，百度千帆开发者大使，GLM 布道师，Trae 昆明第一任 Fellow

| 平台 | 链接 |
|------|------|
| 𝕏 Twitter（袋鼠帝） | https://x.com/aikangarooking |
| 小红书（袋鼠帝） | https://xhslink.com/m/5YejKvIDBbL |
| 抖音（袋鼠帝） | https://v.douyin.com/hYpsjphuuKc |
| 公众号 | 袋鼠帝 AI 客栈 |
| 视频号 | AI 袋鼠帝 |

微信公众号「袋鼠帝 AI 客栈」二维码：

![](https://raw.githubusercontent.com/kangarooking/cangjie-skill/main/assets/kangarooking-gzh.png)

如果你也想把书、长视频、播客、课程里的方法论蒸馏成可调用的 Agent Skills，欢迎加入 cangjie-skill 企微交流群：

<img src="https://raw.githubusercontent.com/kangarooking/cangjie-skill/main/assets/wecom-cangjie-group-qr.png" width="220" alt="cangjie-skill 企微交流群二维码">

## ⭐ Star History

如果这个项目帮到了你，点个 Star 支持一下～

<a href="https://www.star-history.com/?repos=kangarooking%2Fcangjie-skill&type=date&legend=top-left">
 <img alt="Star History Chart" src="./assets/star-history.svg" />
</a>

## License

MIT. See [LICENSE](./LICENSE).
