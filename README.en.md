# Cangjie Skill

A generator workflow for turning books into reusable AI skills.

`cangjie-skill` is the upstream system behind the published skill-pack repositories in this workspace. It is not mainly an end-user skill. It is a production workflow for generating structured, reusable skills from long-form material.

## What It Does

- extracts principles, frameworks, cases, counter-examples, and glossary items
- filters candidate units before they become standalone skills
- converts selected units into a consistent `SKILL.md` format
- links related skills into a navigable graph
- generates supporting files such as `BOOK_OVERVIEW.md`, `INDEX.md`, and `test-prompts.json`

## Pipeline

1. Stage 0: whole-book understanding
2. Stage 1: parallel extraction
3. Stage 1.5: validation and filtering
4. Stage 2: RIA++ skill construction
5. Stage 3: graph linking
6. Stage 4: pressure testing

## What It Has Already Generated

- `poor-charlies-almanack-skill`
- `no-rules-rules-skill`

## Example Outcomes

### Example 1

**User need**

"I want to turn a book into reusable AI skills, not just a long reading summary."

**How cangjie-skill reasons**

- checks whether the source has reusable methodological units
- separates standalone skills from background-only material
- outputs a structured skill repository instead of a single summary file

**Example output**

"The result will not be one summary document. It will be a multi-skill repository with `BOOK_OVERVIEW.md`, `INDEX.md`, multiple `*/SKILL.md` files, and `test-prompts.json` for trigger testing."

### Example 2

**User need**

"I want something my agent can repeatedly use, not a long explanatory article."

**How cangjie-skill reasons**

- optimizes for structured reuse rather than narrative compression
- prefers triggerable, composable, testable skill units
- rejects material that does not deserve to become a standalone skill

**Example output**

"The system produces multiple skill modules with trigger conditions, boundaries, execution patterns, and related-skill links, rather than flattening the source into one generalized note."

## Repository Structure

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
