# Cangjie Skill

Distill a book into a set of executable AI skills.

## Why This Exists

There's a recent viral idea: distilling colleagues into AI skills. Even after someone leaves, their experience, tone, and work style can be partially replicated by AI. [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) does exactly this — creating "human skills" like an Elon Musk skill or a Warren Buffett skill. The companion [darwin-skill](https://github.com/alchaincyf/darwin-skill) handles automatic skill evolution.

Distilling people is valuable — nuwa-skill has already proven this. Distilling what people have **written** is a complementary dimension: a book represents years of deliberate thinking — the distilled essence of careful reflection. Rather than imitating someone's expression style, extracting their systematically produced methodologies into tools that help people solve real problems is equally valuable.

There's also a real pain point: you might read many books but struggle to apply them. Knowledge stays at the "I've read it" level and never gets activated in real decisions. Once a book is distilled into skills, an AI agent can invoke that knowledge in real scenarios — instead of letting it gather dust in your notes.

So cangjie-skill has one clear goal: **distill every book worth distilling**, turning each high-value book into a set of independently callable, composable, and pressure-testable AI skill packs.

## What Problems It Solves

- Reading many books but never applying them — knowledge stays at "I've read it" and never activates in real decisions
- Book summaries and reading notes are compression, not structured reuse — you still don't know "when to use what"
- Only a small fraction of a book deserves to become a tool — strict filtering is needed, not wholesale inclusion
- Existing reading methodologies are designed for human readers, not agent executors — distillation must be execution-oriented, not reading-oriented

## How It Works

cangjie-skill uses the **RIA-TV++** pipeline to transform a book from raw text into a set of structured skills. The process has six stages:

1. **Whole-Book Comprehension (Adler Analysis)** — Structural, interpretive, critical, and applicability analysis using Mortimer Adler's method, producing `BOOK_OVERVIEW.md`
2. **Parallel Extraction** — Five specialized extractors (frameworks, principles, cases, counter-examples, glossary) run simultaneously to pull candidate units from the source text
3. **Triple Verification** — Each candidate must pass three checks: at least 2 independent supporting passages (cross-domain), ability to answer a novel question (predictive power), and non-commonsense uniqueness. Pass rate is typically 25-50%
4. **RIA++ Construction** — Verified content is structured into six dimensions: R (original quote) / I (own-words reconstruction) / A1 (book cases) / A2 (future trigger scenarios) / E (executable steps) / B (boundaries & blind spots)
5. **Zettelkasten Linking** — Dependency, contrast, and composition relationships between skills are identified, producing `INDEX.md` with a reference graph
6. **Pressure Testing** — Test prompts including bait questions are designed for each skill; failures go back for full reconstruction

The name RIA-TV++ breaks down as:
- **RIA**: From Zhao Zhou's bookmark method (Reading / Interpretation / Appropriation)
- **TV**: Triple Verification
- **++**: Agent-oriented extensions — E (Execution) + B (Boundary)

## Effect Examples

### Example 1: From a Book to a Skill Pack

**User Need**

"I want to turn a book's core methodologies into reusable AI skills, not just a reading summary."

**How cangjie-skill reasons**

- Check whether the source material has reusable methodological units
- Distinguish what deserves to be a standalone skill vs. background material
- Output a structured skill repository, not a single summary document

**Example Output**

> The result will not be one summary document. It will be a multi-skill repository with `BOOK_OVERVIEW.md`, `INDEX.md`, multiple `*/SKILL.md` files, and `test-prompts.json` for trigger testing.

### Example 2: Structured Reuse, Not Compression

**User Need**

"I don't want a long explanatory article. I want a skill pack my agent can reuse."

**How cangjie-skill reasons**

- Target is structured reuse, not narrative compression
- Prioritize triggerable, composable, testable skill units
- Reject material that doesn't deserve standalone skill status

**Example Output**

> The system produces multiple skill modules with trigger conditions, boundaries, execution patterns, and related-skill links — rather than flattening the source into one generalized note.

## Generated Skill Packs

| Repository | Source | Skills |
|------------|--------|--------|
| [buffett-letters-skill](https://github.com/kangarooking/buffett-letters-skill) | Buffett's shareholder letters (1957-2023) | 20 |
| [cognitive-dividend-skill](https://github.com/kangarooking/cognitive-dividend-skill) | Cognitive Dividend | 15 |
| [duan-yongping-skill](https://github.com/kangarooking/duan-yongping-skill) | Duan Yongping's Q&A (business + investment logic) | 15 |
| [poor-charlies-almanack-skill](https://github.com/kangarooking/poor-charlies-almanack-skill) | Poor Charlie's Almanack | 12 |
| [no-rules-rules-skill](https://github.com/kangarooking/no-rules-rules-skill) | No Rules Rules | 10 |
| Huangdi Neijing Suwen (in this project) | Huangdi Neijing: Suwen | 10 |
| Huangdi Neijing Lingshu (in this project) | Huangdi Neijing: Lingshu | 8 |
| [first-principles-skill](https://github.com/kangarooking/first-principles-skill) | First Principles | 10 |

More high-value books are planned for distillation.

Additional external source (included with the author's permission):

- Source repository: [ace3000chao/book2startup](https://github.com/ace3000chao/book2startup)
- Included books: *The Lean Startup*, *The Art of War*, *Zhuangzi*, and *I Ching*

## Repository Structure

```text
cangjie-skill/
├── README.md              ← You are here
├── README.en.md           ← English version
├── README.ja.md           ← Japanese version
├── LICENSE                ← MIT
├── SKILL.md               ← Meta-skill definition (full execution spec for book2skill)
├── methodology/           ← RIA-TV++ stage-by-stage methodology docs
├── extractors/            ← Prompt definitions for the 5 parallel extractors
└── templates/             ← SKILL.md / INDEX.md / BOOK_OVERVIEW.md templates
```

## Ecosystem

cangjie-skill is part of a larger skill ecosystem:

- [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) — Distills people (thinking styles, expression DNA)
- **cangjie-skill** (this repo) — Distills books (methodologies, frameworks, principles)
- [darwin-skill](https://github.com/alchaincyf/darwin-skill) — Evolves any skill

They interlock: nuwa distills people, cangjie distills books, darwin keeps them evolving.

## More Skills

- [Buffett Letters Skill](https://github.com/kangarooking/buffett-letters-skill) — 20 investment reasoning skills from Buffett's 60+ years of shareholder letters
- [Poor Charlie's Almanack Skill](https://github.com/kangarooking/poor-charlies-almanack-skill) — 12 decision-making and judgment skills from Charlie Munger's core thinking methods
- [No Rules Rules Skill](https://github.com/kangarooking/no-rules-rules-skill) — 10 organizational design skills from Netflix's culture of freedom and responsibility
- [Cognitive Dividend Skill](https://github.com/kangarooking/cognitive-dividend-skill) — 15 cognitive tool skills for thinking upgrades from Cognitive Dividend
- [Duan Yongping Skill](https://github.com/kangarooking/duan-yongping-skill) — 15 business and investment skills from Duan Yongping's Q&A collection
- Huangdi Neijing Suwen Skill (in this project) — 10 traditional Chinese medicine observation and regulation skills from *Huangdi Neijing: Suwen*
- Huangdi Neijing Lingshu Skill (in this project) — 8 body-mind regulation and syndrome differentiation skills from *Huangdi Neijing: Lingshu*
- [First Principles Skill](https://github.com/kangarooking/first-principles-skill) — 10 skills on axiomatic reasoning, boundary-breaking innovation, and organizational refresh from *First Principles*

External Source (included with the author's permission):

- [book2startup](https://github.com/ace3000chao/book2startup) — includes skills distilled from *The Lean Startup*, *The Art of War*, *Zhuangzi*, and *I Ching*

## About the Author

**kangarooking** — AI blogger, indie developer. Creator of AI Top WeChat Official Account「袋鼠帝 AI 客栈」

Volcengine Navigation KOL, Baidu Qianfan Developer Ambassador, GLM Evangelist, Trae Kunming's First Fellow

| Platform | Link |
|----------|------|
| 𝕏 Twitter | https://x.com/aikangarooking |
| Xiaohongshu | https://xhslink.com/m/5YejKvIDBbL |
| Douyin | https://v.douyin.com/hYpsjphuuKc |
| WeChat Official Account | 袋鼠帝 AI 客栈 |
| WeChat Video Channel | AI 袋鼠帝 |

WeChat Official Account「袋鼠帝 AI 客栈」QR code:

![](https://raw.githubusercontent.com/kangarooking/cangjie-skill/main/assets/kangarooking-gzh.png)

## License

MIT. See [LICENSE](./LICENSE).
