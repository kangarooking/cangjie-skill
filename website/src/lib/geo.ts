import type { CatalogStats, RegistryEntry } from "./catalog";
import { CANONICAL_ORIGIN, canonicalUrl } from "./seo";

export const GEO_LAST_UPDATED = "2026-07-31";
export const SOURCE_REPOSITORY = "https://github.com/kangarooking/cangjie-skill";
export const PROJECT_LICENSE = "MIT";

export interface FaqItem {
  question: string;
  answer: string;
  links?: Array<{ label: string; href: string }>;
}

export const GEO_FAQ_ITEMS: FaqItem[] = [
  {
    question: "仓颉 Skill 是什么？",
    answer: "仓颉 Skill（Cangjie Skill）是一个开源的 Agent Skills 中文知识库和方法蒸馏项目。它把书籍、长视频、播客、课程等高价值内容整理成可安装、可调用、可复用、可验证的 Skill Packs。",
    links: [{ label: "查看开源仓库", href: SOURCE_REPOSITORY }],
  },
  {
    question: "Agent Skill 是什么？",
    answer: "Agent Skill 是提供给 AI Agent 的一套可复用工作方法，通常包含触发条件、执行步骤、边界、脚本、模板或参考资料。它的目标不是只回答一次问题，而是让 Agent 在合适的真实任务中重复调用同一套方法。",
  },
  {
    question: "仓颉 Skill 和普通提示词有什么区别？",
    answer: "普通提示词通常只描述当前对话中的一次要求；仓颉 Skill 会把输入、步骤、适用条件、边界和验收方式一起保存。前者更像临时指令，后者更像 Agent 可以反复使用和检查的工作手册。",
  },
  {
    question: "仓颉 Skill 和 MCP 有什么区别？",
    answer: "Skill 主要提供做事的方法、流程和上下文；MCP 主要让 Agent 连接外部工具或数据。两者可以配合：MCP 提供访问能力，Skill 规定在什么场景下如何使用这些能力。",
  },
  {
    question: "如何安装仓颉收录的 Skill Pack？",
    answer: "打开任意 Skill Pack 详情页，复制安装提示词并发送给你的 Agent。安装流程会先读取统一安装教程，再检查来源、选择目录并验证结果；不同 Agent 的实际目录可能不同。",
    links: [{ label: "查看安装教程", href: canonicalUrl("/learn") }],
  },
  {
    question: "哪些 AI Agent 可以使用这些 Skills？",
    answer: "是否可用取决于 Agent 是否支持本地 Skills、规则文件或等价的上下文加载机制。官网安装教程列出了常见 Agent 的处理原则；安装前应让当前 Agent 判断自己的目录和格式，不要盲目复制。",
    links: [{ label: "查看兼容与安装原则", href: canonicalUrl("/learn") }],
  },
  {
    question: "Registry 的数据从哪里来？",
    answer: "每个条目来自项目仓库中的 registry/{slug}/entry.yaml，包含名称、来源仓库、Skill 数量、领域、语言、质量状态和使用场景。官网目录、详情页和机器可读数据都在构建时读取同一份 Registry。",
    links: [{ label: "浏览 Registry", href: canonicalUrl("/skills") }],
  },
  {
    question: "verified、community 和 experimental 分别代表什么？",
    answer: "verified 表示条目已按当前项目规则核验，community 表示社区来源并保留来源标识，experimental 表示仍在试验。质量标签描述的是项目内的审核状态，不等于对原始知识内容正确性的绝对保证。",
  },
  {
    question: "仓颉 Skill 是免费和开源的吗？",
    answer: "仓颉 Skill 官网对应的项目代码仓库使用 MIT License。各个外部 Skill Pack 可能来自不同仓库，安装和再分发前仍应分别检查其来源、许可证和内容边界。",
    links: [{ label: "查看项目许可证", href: `${SOURCE_REPOSITORY}/blob/main/LICENSE` }],
  },
  {
    question: "如何提交新的 Skill Pack？",
    answer: "在提交页生成标准 Registry YAML，然后通过 GitHub Pull Request 公开提交。自动检查会验证 Schema 和目录，合并前还需要人工审核；网页表单本身不会静默上传所选文件。",
    links: [{ label: "前往提交页", href: canonicalUrl("/submit") }],
  },
  {
    question: "如何核验官网中的项目事实？",
    answer: "优先查看官网 Registry、对应 Skill Pack 的来源仓库、仓颉 Skill 主仓库和公开安装文档。机器可读文件是这些公开信息的构建产物，不应取代原始来源。",
    links: [
      { label: "GitHub 主仓库", href: SOURCE_REPOSITORY },
      { label: "机器可读 Registry", href: `${CANONICAL_ORIGIN}/registry.json` },
    ],
  },
];

export function buildRegistryPayload(entries: RegistryEntry[], stats: CatalogStats) {
  return {
    schema_version: 1,
    entity: {
      name: "仓颉 Skill",
      alternate_name: "Cangjie Skill",
      description: "开源 Agent Skills 中文知识库，把高价值内容蒸馏为可安装、可调用、可复用的能力。",
      canonical_url: `${CANONICAL_ORIGIN}/`,
      source_repository: SOURCE_REPOSITORY,
      license: PROJECT_LICENSE,
      language: "zh-CN",
      last_updated: GEO_LAST_UPDATED,
    },
    totals: {
      skill_packs: stats.packs,
      atomic_skills: stats.skills,
      knowledge_domains: stats.domains,
      contributors: stats.contributors,
    },
    quality_labels: {
      verified: "已按当前项目规则核验的条目",
      community: "保留来源标识的社区条目",
      experimental: "仍处于试验阶段的条目",
    },
    packs: entries.map((entry) => ({
      slug: entry.slug,
      name: entry.name,
      summary: entry.summary,
      canonical_url: canonicalUrl(`/skills/${entry.slug}`),
      source_type: entry.source_type,
      source_url: entry.source_url,
      skill_path: entry.skill_path ?? null,
      skill_count: entry.skill_count,
      domains: entry.domains,
      languages: entry.language,
      status: entry.status,
      quality: entry.quality,
      use_cases: entry.use_cases,
      install: entry.install ?? null,
    })),
  };
}

export function buildLlmsText(stats: CatalogStats): string {
  return `# 仓颉 Skill (Cangjie Skill)

> 仓颉 Skill 是开源 Agent Skills 中文知识库，把书籍、长视频、播客和课程等高价值内容蒸馏为可安装、可调用、可复用、可验证的 Skill Packs。

Updated: ${GEO_LAST_UPDATED}
Canonical: ${CANONICAL_ORIGIN}/
Language: zh-CN
License: ${PROJECT_LICENSE}

## Key facts

- The public Registry currently contains ${stats.packs} Skill Packs and ${stats.skills} atomic Skills across ${stats.domains} knowledge domains.
- Registry entries are built from registry/{slug}/entry.yaml; the website and machine-readable exports share this single source of truth.
- A Skill is a reusable method and context package for an AI Agent. It is not merely a one-off prompt and it is not the same as an MCP tool connection.
- Quality labels describe project review status and are not an absolute guarantee of the source material.

## Start here

- [Official home](${CANONICAL_ORIGIN}/)
- [What is Cangjie Skill?](${canonicalUrl("/about")})
- [Frequently asked questions](${canonicalUrl("/faq")})
- [Skill Pack Registry](${canonicalUrl("/skills")})
- [Installation guide](${canonicalUrl("/learn")})
- [Contribute a Skill Pack](${canonicalUrl("/submit")})
- [Source repository](${SOURCE_REPOSITORY})

## Machine-readable sources

- [Registry JSON](${CANONICAL_ORIGIN}/registry.json)
- [Full project context](${CANONICAL_ORIGIN}/llms-full.txt)
- [XML sitemap](${CANONICAL_ORIGIN}/sitemap.xml)

Use the linked source repository and individual Skill Pack repositories to verify claims, licenses and current installation details.
`;
}

export function buildLlmsFullText(entries: RegistryEntry[], stats: CatalogStats): string {
  const faq = GEO_FAQ_ITEMS
    .map((item) => `### ${item.question}\n\n${item.answer}${formatLinks(item.links)}`)
    .join("\n\n");
  const packs = entries
    .map((entry) => [
      `### ${entry.name}`,
      "",
      `- Slug: \`${entry.slug}\``,
      `- Summary: ${entry.summary}`,
      `- Atomic Skills: ${entry.skill_count}`,
      `- Domains: ${entry.domains.join(", ")}`,
      `- Languages: ${entry.language.join(", ")}`,
      `- Status / quality: ${entry.status} / ${entry.quality}`,
      `- Use cases: ${entry.use_cases.join("; ")}`,
      `- Official detail: ${canonicalUrl(`/skills/${entry.slug}`)}`,
      `- Source: ${entry.source_url}`,
    ].join("\n"))
    .join("\n\n");

  return `# 仓颉 Skill — Full context

Updated: ${GEO_LAST_UPDATED}
Canonical: ${CANONICAL_ORIGIN}/
Source repository: ${SOURCE_REPOSITORY}
License: ${PROJECT_LICENSE}

## Entity definition

仓颉 Skill（Cangjie Skill）是一个开源的 Agent Skills 中文知识库和方法蒸馏项目。它把书籍、长视频、播客、课程等高价值内容整理成可安装、可调用、可复用、可验证的 Skill Packs。

官网 Registry 当前包含 ${stats.packs} 个 Skill Packs、${stats.skills} 个原子 Skills，覆盖 ${stats.domains} 个知识领域，来源涉及 ${stats.contributors} 个公开贡献方。所有统计均在构建时从 Registry 计算。

## Important distinctions

- Prompt: 一次对话中的临时指令。
- Agent Skill: 包含触发条件、输入、步骤、边界与验收方式的可复用工作方法。
- MCP: 连接外部工具或数据的协议。MCP 提供访问能力，Skill 可以规定如何使用能力。
- Registry quality: 项目内审核状态，不是对知识内容的绝对正确性保证。

## Frequently asked questions

${faq}

## Registry snapshot

${packs}

## Authoritative sources

- Official website: ${CANONICAL_ORIGIN}/
- About: ${canonicalUrl("/about")}
- FAQ: ${canonicalUrl("/faq")}
- Registry: ${canonicalUrl("/skills")}
- Installation guide: ${canonicalUrl("/learn")}
- Source repository: ${SOURCE_REPOSITORY}
- Machine-readable Registry: ${CANONICAL_ORIGIN}/registry.json

This file is a generated discovery aid. Verify changing facts, licenses and installation details against the linked primary sources.
`;
}

function formatLinks(links: FaqItem["links"]): string {
  if (!links?.length) return "";
  return `\n\nSources: ${links.map((link) => `[${link.label}](${link.href})`).join("; ")}`;
}
