# 仓颉 Skill 官网 GEO 设计

日期：2026-07-31

## 目标

让仓颉 Skill 官网不仅能被传统搜索引擎收录，也能被 ChatGPT、Google AI、Bing Copilot，以及依赖公开网页检索的中文 AI 产品准确理解、引用和回链。

GEO 不依赖“特殊 AI 标签”承诺展示。主体仍是可抓取、可索引、有清晰实体关系、答案直接且事实可验证的公开网页；`llms.txt` 等文件只作为补充导航。

## 覆盖范围

- 实体：明确“仓颉 Skill / Cangjie Skill”是什么、解决什么问题、与提示词和 MCP 的区别。
- 答案：建立 About 与 FAQ 页面，使用先给结论、再解释和引用来源的结构。
- 数据：公开机器可读的 Registry JSON、简版 `llms.txt` 和完整知识快照 `llms-full.txt`。
- 爬虫：允许搜索与 AI 检索爬虫访问公开页面，同时保留统一 Sitemap。
- 结构化数据：为 About、FAQ、Registry 等可见内容输出匹配的 Schema.org JSON-LD。
- 验证：测试页面、数据文件、Sitemap、robots 和多种 User-Agent 的线上可访问性。

## 信息架构

### `/about/`

回答：

1. 仓颉 Skill 是什么；
2. 它和一次性提示词、MCP 的区别；
3. Registry 的数据来源和质量状态；
4. 如何安装、使用和参与共建；
5. 哪些页面是项目事实的权威来源。

页面使用 AboutPage 结构化数据，并把官网、GitHub、Registry 和安装教程连接成同一实体。

### `/faq/`

建立面向自然语言问题的答案中心。每个答案保持短段落、直接结论和可追溯链接；页面可见内容与 FAQPage JSON-LD 一致。

### 机器可读入口

- `/llms.txt`：项目摘要、核心事实和优先阅读链接。
- `/llms-full.txt`：项目定义、常见问题、Registry 概览及所有 Skill Pack 的文本快照。
- `/registry.json`：从 `registry/{slug}/entry.yaml` 构建，不维护第二份手工目录。

## 数据流

`registry/{slug}/entry.yaml` 是 Registry 唯一事实源。Astro 构建时读取 YAML，同时生成网页目录、详情页、Sitemap、`registry.json` 和 `llms-full.txt`。统计数字由构建函数动态计算，避免文案与目录漂移。

## 爬虫策略

`robots.txt` 明确允许 OAI-SearchBot、ChatGPT-User、GPTBot、Googlebot、Bingbot 和 Baiduspider 访问公开内容，并保留通配允许规则与标准 Sitemap 地址。

这项配置只解决“允许访问”，不代表任何平台保证收录、训练或引用。平台是否展示仍取决于索引状态、内容质量、查询相关性和各平台规则。

## 质量与安全

- 不写无法由仓库或 Registry 证明的规模、兼容性和效果数据。
- 结构化数据必须与页面可见内容一致。
- 不制造评价、评分、作者身份或商业承诺。
- 机器可读文件只暴露已经公开的网站与 Registry 信息。
- 旧域名、Pages 域名和新自定义域名继续由 Cloudflare 配置承载；Canonical 统一到 `https://www.cangjie-skill.com`。

## 验收标准

- About、FAQ、`llms.txt`、`llms-full.txt`、`registry.json` 均在线返回 200。
- Registry JSON 可解析，Pack 数量和 Atomic Skills 总数与网站一致。
- FAQ JSON-LD 与可见问答一一对应。
- Sitemap 收录新增 HTML 页面，不收录辅助文本和 JSON 文件。
- `npm run verify` 与 Cloudflare 构建通过。
- OAI-SearchBot、ChatGPT-User、Googlebot、Bingbot、Baiduspider 请求公开入口不被拒绝。
