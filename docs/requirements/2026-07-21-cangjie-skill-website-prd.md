# 仓颉 Skill 官方网站产品需求文档（PRD）

- 文档版本：V1.0
- 日期：2026-07-21
- 产品阶段：MVP 已实现，待推送、合并并正式部署
- 适用对象：产品、设计、前端、维护者、社区贡献者
- 需求基线：codex/website-mvp 分支

## 1. 文档目的

本文件用于统一仓颉 Skill 官方网站的产品范围、页面功能、数据规则、投稿审核流程、安装体验和验收标准。

它同时承担三项作用：

1. 作为当前 MVP 的功能说明，描述网站已经具备的能力。
2. 作为开发验收依据，明确每项功能的输入、行为、状态和结果。
3. 作为后续迭代边界，区分必须完成、可继续优化和暂不建设的功能。

本文优先描述产品行为。具体代码结构、组件名称和技术实现可以调整，但不得改变已经确认的用户流程。

## 2. 产品概述

### 2.1 产品名称

- 中文名：仓颉 Skill
- 英文名：Cangjie Skill
- 产品形态：知识蒸馏方法论官网 + 开放 Skill Registry

### 2.2 一句话定位

把书籍、课程、长视频、播客和其他高价值内容中的方法论，蒸馏成 Agent 可以直接安装、调用和复用的 Skills。

### 2.3 产品要解决的问题

网站需要解决四个核心问题：

1. 用户不知道仓颉 Skill 是什么，也不知道它与普通摘要、笔记和提示词的区别。
2. 用户知道某个 Skill 存在，但很难根据真实任务找到合适的 Skill Pack。
3. Skill 的安装方式过于技术化，普通用户不应该自己判断不同 Agent 的目录和复制命令。
4. 社区成员希望贡献 Skill，但项目不需要为首版建设账号、数据库和独立审核后台。

### 2.4 核心解决方案

- 用首页解释价值并完成用户分流。
- 用教程页教用户完成“选择—安装—调用—验证”。
- 用 Registry 展示并检索已经蒸馏好的 Skill Packs。
- 用统一安装提示词把安装工作交给 Agent。
- 用 GitHub Pull Request 作为公开、透明、可审计的投稿审核机制。

## 3. 产品目标与非目标

### 3.1 MVP 产品目标

| 编号 | 目标 | 成功结果 |
|---|---|---|
| G-01 | 帮助新用户理解仓颉 Skill | 用户能说清 Skill Pack、原子 Skill 和普通摘要的区别 |
| G-02 | 帮助用户找到合适的 Skill | 用户能通过搜索和筛选进入一个 Pack 详情页 |
| G-03 | 降低安装门槛 | 用户只需复制一条提示词给 Agent，不必手动判断目录 |
| G-04 | 完成一次真实调用 | 用户安装后能用自然语言让 Agent 调用对应方法 |
| G-05 | 建立公开投稿闭环 | 贡献者能生成标准 Registry 文件并进入 GitHub PR 审核 |
| G-06 | 保持低运维成本 | 网站不依赖账号系统、数据库和独立后端 |

### 3.2 MVP 明确不做

- 不做站内账号、登录和用户资料。
- 不做独立管理后台。
- 不做收藏、点赞、评分、评论和关注。
- 不做站内支付、交易和商业分成。
- 不做在线运行或沙箱执行陌生 Skill。
- 不做自动安装本地文件的桌面客户端。
- 不做每个原子 Skill 的独立详情页。
- 不做复杂推荐算法、个性化推荐和外部搜索服务。
- 不做多语言站点和深色模式。
- 不做复杂动效和高成本视觉系统。
- 不把原始受版权保护的书籍、课程、视频或音频作为 Registry 内容托管。

## 4. 用户角色

### 4.1 Skill 使用者

典型需求：

- 了解仓颉 Skill 的作用。
- 根据当前问题找到合适的 Pack。
- 把 Skill 安装到 Codex、Claude Code、Cursor、WorkBuddy 等 Agent。
- 确认安装是否成功并开始调用。

### 4.2 Skill 贡献者

典型需求：

- 提交一个已经公开到 GitHub 的 Skill 仓库。
- 提交一个尚未独立开源的本地 Skill 文件夹。
- 在提交前看到格式错误、敏感文件和目录问题。
- 保留自己的 GitHub 身份、仓库归属和维护权。

### 4.3 Registry 维护者

典型需求：

- 通过 Pull Request 查看所有变更。
- 自动验证 Registry Schema、目录和构建结果。
- 检查来源、版权、安全性、可执行性和重复度。
- 合并通过的投稿，并让网站自动更新。

### 4.4 Agent

Agent 是安装流程中的执行角色，需要：

- 读取统一安装规范。
- 识别自身运行环境和 Skills 目录。
- 检查来源仓库和文件结构。
- 安装全部必要文件。
- 处理冲突和风险。
- 汇报安装位置、安装结果和验证状态。

## 5. 核心用户旅程

### 5.1 使用 Skill 的主流程

~~~mermaid
flowchart LR
  A[进入官网] --> B[理解仓颉 Skill]
  B --> C[搜索或筛选 Skill Pack]
  C --> D[查看详情与使用场景]
  D --> E[复制 Agent 安装提示词]
  E --> F[Agent 读取安装规范]
  F --> G[Agent 检查并完成安装]
  G --> H[用户描述真实任务]
  H --> I[确认 Skill 已正确触发]
~~~

### 5.2 投稿审核主流程

~~~mermaid
flowchart LR
  A[选择投稿方式] --> B[填写 Registry 信息]
  B --> C[浏览器本地校验]
  C --> D[生成 entry.yaml 或 ZIP]
  D --> E[创建 GitHub Pull Request]
  E --> F[自动 Schema 与构建检查]
  F --> G[维护者人工审核]
  G --> H[合并到 main]
  H --> I[网站自动重新构建并上线]
~~~

## 6. 信息架构

### 6.1 核心路由

| 路由 | 页面 | 主要目标 |
|---|---|---|
| / | 首页 | 解释产品、展示规模、分流到使用、浏览和投稿 |
| /learn | 使用教程 | 教会用户选择、安装、调用和验证 Skill |
| /skills | Skills 目录 | 搜索、筛选并浏览 Skill Packs |
| /skills/[slug] | Skill Pack 详情 | 理解用途、复制安装提示词、查看来源 |
| /submit | 提交 Skill | 生成投稿文件并进入 GitHub PR 流程 |
| /install/cangjie-skill.md | Agent 安装规范 | 供 Agent 读取，不作为普通营销页面 |

### 6.2 全站导航

页头必须包含：

- 仓颉 Skill 品牌入口，点击返回首页。
- 使用教程。
- Skills。
- 提交 Skill。
- GitHub 外部链接。

当前路由需要通过 aria-current 标识。外部 GitHub 链接在新窗口打开。

页脚必须包含：

- 品牌与一句话说明。
- 使用教程。
- Skill 目录。
- 参与共建。
- GitHub。

## 7. 功能优先级定义

| 优先级 | 含义 |
|---|---|
| P0 | MVP 必须具备；缺失会导致核心流程无法完成 |
| P1 | 上线后应优先完善；不会阻断主流程 |
| P2 | 后续增长或体验增强 |

本文中标记“已实现”表示当前分支已有对应功能；“待发布”表示代码已存在，但尚未进入正式 GitHub Pages；“后续”表示尚未实现。

## 8. 首页需求

### 8.1 页面目标

首页只承担三项任务：

1. 让第一次访问的人迅速理解产品价值。
2. 让使用者进入 Skill 目录或教程。
3. 让贡献者进入投稿流程。

### 8.2 Hero 模块

| 需求编号 | 优先级 | 状态 | 需求 |
|---|---|---|---|
| FR-HOME-001 | P0 | 已实现 | 展示主标题“把知识，变成 AI 可以执行的方法” |
| FR-HOME-002 | P0 | 已实现 | 展示仓颉 Skill 是知识蒸馏方法和开放 Skill 目录 |
| FR-HOME-003 | P0 | 已实现 | 提供“浏览 Skills”主按钮，进入 /skills |
| FR-HOME-004 | P0 | 已实现 | 提供“从零开始使用”按钮，进入 /learn |

### 8.3 Registry 数据概览

首页必须从 Registry 构建时动态计算并展示：

- Skill Pack 数。
- 原子 Skill 总数。
- Knowledge Domains 数。
- Contributor 数。

当前数据基线：

- 22 个 Skill Packs。
- 300 个原子 Skills。
- 23 个知识领域。
- 2 个来源贡献者。

禁止在页面组件中手工维护这些数字。新增或删除 Registry 条目后，统计必须自动变化。

### 8.4 三步使用说明

步骤固定为：

1. 选择 Skill Pack。
2. 交给 Agent 安装。
3. 描述真实任务。

安装说明不得再把 git clone、cp -R 或某一个 Agent 的目录作为普通用户默认流程。

### 8.5 精选 Skill Packs

| 需求编号 | 优先级 | 状态 | 需求 |
|---|---|---|---|
| FR-HOME-010 | P0 | 已实现 | 从 featured: true 的 Registry 条目中读取精选 Pack |
| FR-HOME-011 | P0 | 已实现 | 首页最多展示 6 个精选 Pack |
| FR-HOME-012 | P0 | 已实现 | 卡片展示质量、原子 Skill 数、名称、简介、领域和详情入口 |
| FR-HOME-013 | P0 | 已实现 | 提供查看全部入口 |

### 8.6 共建入口

首页底部必须明确说明：

- 无需注册独立账号。
- 投稿生成标准 Registry 文件。
- GitHub Pull Request 是审核入口。

主按钮进入 /submit。

## 9. 使用教程需求

### 9.1 页面目标

教程页帮助用户完成以下认知：

- Skill Pack 是什么。
- 如何选择 Pack。
- 如何把安装交给 Agent。
- 如何开始调用。
- 如何确认 Skill 已生效。

### 9.2 页面结构

教程由五个连续步骤和常见问题组成：

1. 理解 Skill Pack 目录。
2. 选择适合当前任务的 Pack。
3. 把安装提示词交给 Agent。
4. 用自然语言描述真实任务。
5. 验证 Skill 是否生效。
6. 常见问题。

桌面端展示页内目录；移动端可以隐藏目录，但正文锚点必须保留。

### 9.3 安装提示词示例

教程必须展示可理解的完整示例：

~~~text
请根据 https://cangjie-skill.pages.dev/install/cangjie-skill.md，
从 https://github.com/kangarooking/buffett-letters-skill
安装 buffett-letters-skill。
~~~

固定安装规范地址为：

https://cangjie-skill.pages.dev/install/cangjie-skill.md

该地址只有在官网部署完成后才可访问。发布前必须把安装规范文件与网站同时部署，避免生产页面引用 404。

### 9.4 Agent 安装结果说明

教程需要告诉用户 Agent 将自动完成：

- 识别当前 Agent。
- 判断全局或项目级 Skills 目录。
- 读取来源仓库。
- 检查 SKILL.md、风险和同名冲突。
- 安装脚本、模板与资源。
- 验证并报告安装结果。

以下情况 Agent 必须暂停并请求确认：

- 覆盖存在本地修改的同名 Skill。
- 执行未审查脚本。
- 需要密钥、凭证或个人信息。
- 需要提升系统权限。
- 来源不可验证或存在明显风险。

### 9.5 调用和验证

用户安装后可以直接描述业务任务，不要求记忆命令。

验证 Prompt 至少需要让 Agent 说明：

- 使用了哪个 Skill。
- 为什么选择它。
- 它要求遵循哪些步骤。

### 9.6 常见问题

P0 必须覆盖：

- Agent 没有识别 Skill。
- 一次安装多个 Skill 的冲突。
- Skill 是否会上传用户资料。
- 安装后是否需要新会话或重新扫描。

## 10. Skills 目录需求

### 10.1 页面目标

用户应当根据“我要解决什么问题”发现 Skill，而不只是按书名或仓库名浏览。

### 10.2 列表内容

每张 Skill Card 必须展示：

- 质量等级。
- 原子 Skill 数。
- Pack 名称。
- 一句话简介。
- 领域标签。
- 详情页入口。

### 10.3 搜索

当前本地搜索范围：

- 名称。
- slug。
- summary。
- domains。
- use_cases。

搜索行为：

- 不区分大小写。
- 去除首尾空格。
- 输入后即时过滤，不需要提交。
- 没有关键词时展示全部。

P1 扩展项：

- 把原子 Skill 名称和触发描述纳入索引。
- 支持拼音或中英文别名。
- 支持结果相关性排序。

### 10.4 筛选

P0 筛选维度：

- 领域。
- 质量：已验证、社区收录、实验性。
- 来源：GitHub 仓库、仓库内置。

筛选条件可以组合，结果取交集。

### 10.5 URL 状态

当前已实现：

- q：搜索关键词。
- domain：领域。
- quality：质量。

P1 要求：

- source 同样写入 URL。
- 页面加载时恢复全部筛选条件。
- 分享 URL 后接收者看到相同结果。

### 10.6 结果状态

必须包含：

- 全部结果计数。
- 筛选后的结果计数。
- 重置筛选。
- 无匹配结果空状态。
- 空状态中的“清空筛选”操作。

## 11. Skill Pack 详情页需求

### 11.1 页面目标

详情页需要回答四个问题：

1. 这是什么？
2. 它适合解决什么问题？
3. 怎样交给 Agent 安装？
4. 来源是否公开、当前质量状态是什么？

### 11.2 页面信息结构

顶部：

- 返回 Skills 目录。
- 质量等级。
- 原子 Skill 数。
- 领域。
- Pack 名称。
- 简介。

页内导航：

- 概览。
- 使用场景。
- 如何使用。
- 来源信息。

主体采用双栏结构：

- 左侧：概览、使用场景、使用步骤和来源。
- 右侧：Agent 安装卡和 Registry 元数据。

移动端右侧安装卡移动到正文前方，确保核心动作优先出现。

### 11.3 Agent 安装卡

| 需求编号 | 优先级 | 状态 | 需求 |
|---|---|---|---|
| FR-DETAIL-010 | P0 | 已实现 | 根据 Registry 条目自动生成安装提示词 |
| FR-DETAIL-011 | P0 | 已实现 | 提供“复制安装提示词”按钮 |
| FR-DETAIL-012 | P0 | 已实现 | 复制成功后显示短暂成功反馈 |
| FR-DETAIL-013 | P0 | 已实现 | 提供“查看安装规范”链接 |
| FR-DETAIL-014 | P0 | 已实现 | 提供“查看源代码”链接 |
| FR-DETAIL-015 | P0 | 已实现 | 不把手动 Git 命令作为默认安装流程 |

GitHub 来源的提示词格式：

~~~text
请根据 {安装规范 URL}，从 {source_url} 安装 {slug}。
~~~

仓库内置来源的提示词格式：

~~~text
请根据 {安装规范 URL}，
从 {source_url} 中的 {skill_path} 安装 {slug}。
~~~

### 11.4 概览

概览需要展示：

- Pack 简介。
- 原子 Skill 数。
- 领域数量。
- 支持语言数量。

### 11.5 使用场景

每个 Pack 展示 1—6 个 use_cases。使用场景必须描述用户任务，不应只是抽象主题词。

正确示例：

- 分析企业长期价值。
- 检查投资决策的关键假设。

不推荐示例：

- 投资。
- 思考。

### 11.6 如何使用

固定为三步：

1. 把安装提示词发给 Agent。
2. 说清楚真实任务。
3. 确认调用了正确方法。

页面需要提供一条通用调用示例。

### 11.7 来源信息

必须展示：

- GitHub 仓库路径。
- 可点击的源仓库入口。
- Registry 的 slug、质量、领域、语言、来源类型和状态。
- Registry 文件的修改路径。

## 12. Agent 安装规范需求

### 12.1 文件与地址

- 源文件：website/public/install/cangjie-skill.md
- 正式地址：https://cangjie-skill.pages.dev/install/cangjie-skill.md
- 内容类型：Markdown 文本。
- 目标读者：Agent。

### 12.2 安装位置判断

规范必须包含常见 Agent 的 Skills 目录：

- Codex。
- Claude Code。
- Cursor。
- Windsurf。
- Gemini CLI。
- QoderWork。
- WorkBuddy。
- 其他 Agent 的兜底判断方式。

如果用户明确要求安装到当前项目，优先使用项目级目录；否则使用全局目录。

### 12.3 来源检查

Agent 必须：

- 确认 URL 可访问。
- 记录仓库版本或 commit。
- 在临时目录检查，不直接覆盖。
- 阅读 README 和 SKILL.md。
- 检查脚本、外部下载、凭证要求和目录冲突。

### 12.4 安装范围

Agent需要查找全部 SKILL.md，并把包含 SKILL.md 的目录及其必要脚本、模板和资源完整安装。

不得复制：

- .git。
- 构建缓存。
- .env。
- 密钥。
- 无关大型素材。
- 明显不属于 Skill 运行所需的文件。

### 12.5 冲突策略

- 内容与版本相同：跳过并说明。
- 可以安全升级：保留必要配置后更新。
- 存在本地修改：停止覆盖并询问。
- 无法判断安全性：停止并说明。

### 12.6 安装结果

Agent 最终必须报告：

- 来源。
- 版本或 commit。
- 安装目录。
- 已安装或已更新的 Skill。
- 被跳过的内容。
- 风险提示。
- 验证结果。

安装成功后不得自动执行 Skill 的业务任务，除非用户同时提出该任务。

## 13. 提交 Skill 页面需求

### 13.1 页面目标

让贡献者在没有账号系统和后台的情况下，生成符合规范的投稿文件，并进入 GitHub Pull Request 审核。

### 13.2 审核流程说明

页面顶部展示四步：

1. 填写信息。
2. 发起 PR。
3. 自动检查。
4. 人工审核。

页面必须说明：

- 所有审核公开发生在 GitHub。
- 网站不会在后台保存所填信息。
- 自动检查通过不代表一定合并。

### 13.3 投稿模式 A：公开 GitHub 仓库

适用于已经公开开源的 Skill。

输入：

- Pack 名称。
- slug。
- 简介。
- GitHub 仓库 URL。
- 原子 Skill 数量。
- 语言。
- 领域标签。
- 使用场景。
- 投稿确认。

输出：

- registry/{slug}/entry.yaml。
- YAML 预览。
- 复制 YAML。
- 下载 entry.yaml。
- 打开 GitHub 新建文件页面。

GitHub URL 必须：

- 使用 HTTPS。
- 域名为 github.com。
- 至少包含 owner 和 repository 两级路径。
- 自动移除结尾的 .git 和斜杠。

### 13.4 投稿模式 B：本地 Skill 文件夹

适用于尚未建立独立公开仓库的 Skill。

用户在浏览器中选择本地文件夹。网站只在浏览器本地读取和打包，不把文件上传到网站服务器。

输出 ZIP 结构：

~~~text
registry/{slug}/
├── entry.yaml
└── skill/
    ├── README.md
    ├── atomic-skill-a/
    │   └── SKILL.md
    └── atomic-skill-b/
        └── SKILL.md
~~~

Registry 字段：

- source_type 为 bundled。
- source_url 指向仓颉 Skill 主仓库。
- skill_path 为 registry/{slug}/skill。

### 13.5 本地文件夹校验

必须拦截：

- 找不到 SKILL.md。
- 总大小超过 20 MB。
- 包含 .env。
- 包含 id_rsa 或 id_ed25519。
- 包含 credentials.json。
- 包含 pem、key 或 p12 文件。

必须忽略：

- .DS_Store。
- Thumbs.db。
- node_modules。

警告但不阻断：

- 缺少 README.md。

检测通过后，页面自动把 SKILL.md 数量写入原子 Skill 数量。

### 13.6 表单规则

| 字段 | 规则 |
|---|---|
| name | 必填，2—80 字符 |
| slug | 必填，小写英文、数字、连字符，最长 64 |
| summary | 必填，10—240 字符 |
| repositoryUrl | GitHub 模式必填 |
| skillCount | 正整数，最小 1 |
| domains | 至少 1 个，支持中文或英文逗号 |
| languages | zh-CN、en、ja，可多选 |
| useCases | 每行 1 个，至少 1 个，最多取前 6 个 |
| agreement | 必须勾选 |

### 13.7 Slug 生成

名称输入时可以自动生成 slug：

- 转为小写。
- 非字母数字替换为连字符。
- 去除首尾连字符。
- 最长 64 字符。

用户手动修改 slug 后，不再被名称变化自动覆盖。

中文名称无法自动生成有效英文 slug 时，用户必须手动填写。

### 13.8 草稿与隐私

当前实现：

- 普通字符串字段保存到浏览器 localStorage。
- 所选文件夹不会保存。
- 所选文件夹不会自动上传。
- 页面不会把表单内容发送到独立服务器。

P1：

- 正确保存和恢复多语言选择。
- 提供“清除草稿”。
- 在不同投稿模式间切换时保留有效字段。

### 13.9 生成结果

提交表单后必须：

- 显示生成的 YAML。
- 启用复制按钮。
- 展示下一步说明。
- 根据模式展示 entry.yaml 下载或完整 ZIP 下载。
- GitHub 模式展示创建文件入口。
- 失败时在表单附近展示明确错误。

## 14. Registry 数据需求

### 14.1 单一数据源

Registry 是网站 Skill 数据的唯一来源：

~~~text
registry/{slug}/entry.yaml
~~~

页面不得另外维护一份 Skill 列表或统计 JSON。

### 14.2 Schema 文件

Schema 路径：

~~~text
schemas/registry-entry.schema.json
~~~

使用 JSON Schema Draft 2020-12。

### 14.3 必填字段

| 字段 | 类型 | 说明 |
|---|---|---|
| schema_version | 常量 1 | Registry 格式版本 |
| slug | string | 唯一 URL 标识 |
| name | string | 展示名称 |
| summary | string | 一句话简介 |
| source_type | enum | github 或 bundled |
| source_url | URI | GitHub 来源地址 |
| skill_count | integer | 原子 Skill 数 |
| domains | string[] | 领域 |
| language | enum[] | zh-CN、en、ja |
| status | enum | active、experimental、archived |
| quality | enum | verified、community、experimental |
| use_cases | string[] | 1—6 个使用场景 |

### 14.4 可选字段

| 字段 | 说明 |
|---|---|
| skill_path | bundled 模式下的仓库内路径 |
| featured | 是否进入首页精选 |
| install | 兼容旧数据的手动 clone/copy 信息，当前 UI 不作为主流程 |

### 14.5 质量等级

- verified：维护者已检查内容、结构和主要使用方式。
- community：社区投稿，已通过基本审核，但不代表官方背书。
- experimental：仍在试验，结构、兼容性或效果可能变化。

新投稿默认使用 community，不能由普通投稿者自行标记 verified。

### 14.6 内容状态

- active：正常展示和使用。
- experimental：展示但明确提示实验性。
- archived：不再维护。

P1 需要明确 archived 是否默认从目录隐藏；当前 Schema 已支持，但页面尚未做单独处理。

### 14.7 目录校验

自动校验必须保证：

- 每个 Registry 子目录都有 entry.yaml。
- 文件夹名等于 slug。
- slug 不重复。
- 所有字段符合 Schema。
- source_url 是 GitHub HTTPS URL。
- 至少存在一个 Registry 条目。
- 可以计算 Pack 和原子 Skill 总数。

## 15. GitHub PR 审核需求

### 15.1 原则

GitHub PR 同时承担：

- 投稿队列。
- 身份归属。
- 讨论记录。
- 修改历史。
- 自动检查结果。
- 人工审核记录。

### 15.2 自动检查

当 Pull Request 修改以下路径时触发：

- registry/**。
- schemas/**。
- website/**。
- .github/workflows/**。

自动执行：

1. npm ci。
2. Registry Schema 校验。
3. 单元测试。
4. Astro 类型检查。
5. 静态站点构建。

### 15.3 人工审核

维护者至少检查：

- 来源是否公开、真实和可追溯。
- 投稿者是否有权公开内容。
- 是否包含受版权限制的原始材料。
- 是否包含密钥、凭证、隐私或恶意代码。
- Skill 是否有明确触发条件、输入、步骤和输出。
- 是否真正形成可执行方法，而不是普通摘要。
- 是否与现有内容高度重复。
- Registry 简介和 use_cases 是否准确、不过度宣传。

### 15.4 审核结果

- 通过：合并到 main，网站自动更新。
- 请求修改：在 PR 中说明问题，贡献者继续提交。
- 拒绝：关闭 PR，并保留公开原因。

## 16. 状态与异常需求

### 16.1 搜索无结果

展示：

- “没有找到匹配的 Skill”。
- 建议更换关键词或清空筛选。
- 清空筛选按钮。

### 16.2 安装规范不可访问

正式上线验收时必须检查固定 URL 返回 200。

如果安装规范 URL 不可访问：

- 不得宣称 Agent 安装流程已经正式可用。
- 发布流程应视为未完成。
- P1 可以在页面增加“规范暂不可用”的构建期检测或状态提示。

### 16.3 Clipboard 不可用

当前复制功能依赖 navigator.clipboard。

P1 需要：

- 捕获复制失败。
- 提示用户手动选择文本。
- 不把复制失败误显示为成功。

### 16.4 GitHub 不可用

如果 GitHub 新建文件页面无法打开：

- 用户仍可下载 entry.yaml 或 ZIP。
- 页面应保留手动 Fork 和 PR 的说明。

### 16.5 本地文件夹不受支持

文件夹选择依赖浏览器的 webkitdirectory 能力。P1 需要检测支持情况；不支持时提供 ZIP 或多文件选择的替代说明。

## 17. 安全、版权与隐私

### 17.1 安全原则

- 网站不在服务端运行投稿 Skill。
- 网站不自动执行上传文件中的脚本。
- 本地文件夹只在浏览器内检查和打包。
- Agent 安装前必须检查来源和冲突。
- 需要凭证、权限提升或覆盖修改时必须询问。

### 17.2 版权原则

允许：

- 投稿者自己创作的 Skill。
- 有明确授权的内容。
- 指向投稿者自行维护的公开 GitHub 仓库。
- 对知识方法的原创结构化表达。

不允许：

- 未授权完整书籍、课程、视频、音频和付费资料。
- 通过 Skill 变相分发原始受版权保护内容。
- 无法说明来源或授权状态的资料包。

### 17.3 隐私

- 不建立用户数据库。
- 不收集投稿文件。
- 不保存所选文件夹。
- localStorage 草稿只存在用户当前浏览器。
- 不在 MVP 中接入第三方行为分析。

## 18. 非功能需求

### 18.1 性能

- 网站必须静态生成。
- 首屏不依赖数据库或运行时 API。
- Registry 在构建期读取。
- 搜索和筛选在浏览器本地完成。
- 22 个 Pack 规模下操作应无明显延迟。

P1 性能目标：

- 桌面端 Lighthouse Performance ≥ 90。
- 移动端首屏主要内容在正常网络下 2.5 秒内可见。

### 18.2 响应式

必须支持：

- 桌面端。
- 平板。
- 宽度约 390px 的移动端。

移动端要求：

- 卡片单列。
- 筛选控件单列或双列。
- 详情页安装卡优先。
- 投稿表单和预览改为单列。
- 不产生影响主流程的横向滚动。

### 18.3 可访问性

当前基础要求：

- 提供跳到正文链接。
- 主导航有 aria-label。
- 当前页面使用 aria-current。
- 搜索结果数量使用 aria-live。
- 表单字段有 label。
- 按钮可通过键盘触发。
- 文本与背景具备基本对比度。

P1：

- 完成 WCAG 2.1 AA 基础检查。
- 为复制成功和表单错误提供屏幕阅读器状态。
- 检查所有焦点样式。

### 18.4 SEO

当前已实现：

- 每页独立 title。
- 每页 description。
- lang=zh-CN。
- 静态可抓取 HTML。

P1：

- Open Graph。
- Twitter Card。
- canonical URL。
- sitemap.xml。
- robots.txt。
- Skill 详情结构化数据。

### 18.5 浏览器兼容

目标：

- 当前版本 Chrome、Edge、Safari、Firefox。

文件夹选择和 Clipboard API 必须重点验证兼容性。

## 19. 技术与部署约束

### 19.1 架构

- 框架：Astro 静态站点。
- 数据：YAML Registry。
- Schema：JSON Schema + Ajv。
- 投稿打包：JSZip。
- 测试：Vitest。
- 部署：GitHub Pages。
- 审核：GitHub Pull Request。
- 后端：无。
- 数据库：无。

### 19.2 GitHub Pages

部署触发：

- main 分支中的 registry/** 变化。
- schemas/** 变化。
- website/** 变化。
- deploy-pages 工作流变化。
- 手动 workflow_dispatch。

部署需要：

- GitHub Pages Source 设置为 GitHub Actions。
- main 包含网站、Registry 和安装规范。
- 构建时 SITE_URL 为 https://kangarooking.github.io。
- base 为 /cangjie-skill。

### 19.3 发布前阻断项

正式发布前必须全部完成：

- 网站分支推送到 GitHub。
- PR 检查通过。
- 合并到 main。
- Pages 启用 GitHub Actions。
- 首页返回 200。
- /skills 返回 200。
- 任一详情页返回 200。
- /submit 返回 200。
- /install/cangjie-skill.md 返回 200。
- 详情页复制的固定安装 URL 可被 Agent 访问。

## 20. 当前实现状态

### 20.1 已实现

- 五个核心页面。
- 22 个动态 Skill Pack 详情页。
- 22 个 Pack、300 个原子 Skill 的 Registry。
- 搜索和领域、质量、来源筛选。
- SkillHub 风格的详情页信息层级。
- Agent 安装提示词。
- 统一 Agent 安装规范。
- GitHub 仓库投稿。
- 本地文件夹投稿。
- YAML 预览、复制和下载。
- 本地 ZIP 打包。
- Schema 校验。
- 单元测试、类型检查和静态构建。
- PR 模板。
- CI 工作流。
- GitHub Pages 部署工作流。

### 20.2 已配置但待发布

- 正式官网。
- 固定安装规范 URL。
- main 合并后的自动部署。

### 20.3 当前测试基线

- Registry：22 Packs、300 Atomic Skills。
- 单元测试：9 个。
- Astro 类型错误：0。
- 静态 HTML 页面：26 个。

测试数量和数据量会随功能变化更新，不应作为永久硬编码指标。

## 21. MVP 验收标准

### 21.1 用户使用闭环

- [ ] 用户可从首页进入 Skill 目录。
- [ ] 用户可搜索“投资”等关键词并看到相关 Pack。
- [ ] 用户可组合领域、质量和来源筛选。
- [ ] 用户可进入任意详情页。
- [ ] 用户可复制完整 Agent 安装提示词。
- [ ] 安装提示词中的规范 URL 返回 200。
- [ ] Agent 能根据规范找到对应来源并完成安装。
- [ ] 用户能按照教程验证 Skill 已生效。

### 21.2 投稿闭环

- [ ] GitHub 模式能生成符合 Schema 的 entry.yaml。
- [ ] GitHub 模式能下载文件并打开新建文件入口。
- [ ] 本地模式能识别 SKILL.md 数量。
- [ ] 本地模式能阻止敏感文件和超大文件夹。
- [ ] 本地模式能生成正确目录结构的 ZIP。
- [ ] PR 能触发自动检查。
- [ ] Registry 变更合并后网站内容自动更新。

### 21.3 质量闭环

- [ ] npm run validate:registry 通过。
- [ ] npm test 通过。
- [ ] npm run check 通过。
- [ ] npm run build 通过。
- [ ] 桌面端关键页面无明显布局错误。
- [ ] 移动端核心操作可完成。
- [ ] 用户已有的无关仓库文件未被修改。

## 22. 后续迭代建议

### 22.1 P1：上线可靠性

- 正式发布 Pages。
- 部署后健康检查。
- 固定安装规范 URL 的 CI 检查。
- Clipboard 失败回退。
- 文件夹选择兼容提示。
- 所有筛选条件 URL 化。
- 草稿清除和多语言恢复。
- archived 条目的展示策略。

### 22.2 P1：发现效率

- 把原子 Skill 名称纳入搜索。
- 增加来源作者展示。
- 增加更新时间和版本。
- 增加相似 Skill 和相关 Pack。
- 提供分类落地页。

### 22.3 P1：可信度

- 展示审核时间和审核者。
- 展示测试报告或验证摘要。
- 展示来源 commit 或版本。
- 增加安全声明和版权声明页面。

### 22.4 P2：社区能力

- 贡献者主页。
- 收藏、评分和评论。
- 排行榜和趋势。
- 版本更新提醒。
- Skill 兼容性矩阵。

这些能力不得在 MVP 主流程稳定前引入数据库和账号系统。

## 23. 产品原则

后续所有需求和设计决策应遵循：

1. 先帮助用户解决真实任务，再展示项目概念。
2. 安装优先交给 Agent，不把目录知识转嫁给普通用户。
3. Registry 是唯一数据源。
4. GitHub PR 是首版审核后台。
5. 来源、授权、审核过程必须公开可追溯。
6. 默认不执行、不上传、不索取凭证。
7. 功能优先于视觉复杂度。
8. 先保持静态、低成本和可维护，再扩展社区能力。

## 24. 相关文件

- 功能规格：docs/plans/2026-07-13-cangjie-skill-website-mvp-functional-spec.md
- Agent 安装调整：docs/plans/2026-07-13-agent-install-detail-redesign.md
- Registry Schema：schemas/registry-entry.schema.json
- Registry 数据：registry/
- 官网源码：website/
- Agent 安装规范：website/public/install/cangjie-skill.md
- 贡献说明：CONTRIBUTING.md
- PR 模板：.github/pull_request_template.md
- Registry 检查：.github/workflows/registry-check.yml
- Pages 部署：.github/workflows/deploy-pages.yml
