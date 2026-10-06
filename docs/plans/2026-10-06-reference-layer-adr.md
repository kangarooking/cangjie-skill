# ADR：查阅层（Reference Layer）— 让蒸馏产物既能"执行"也能"回源"

> 日期：2026-10-06 ｜ 状态：已采纳（向后兼容的可选增强）
> 背景：对标同类项目的分层加载与两级检索设计（如 virgiliojr94/book-to-skill 的按需章节文件、crayon-ai/book-to-webpage 的"先摘要后原文"检索）。

## 1. 问题

仓颉产物的能力卡面向**执行**（触发 → 方法论 → 步骤），但对**查阅类问题**没有可靠路径：
用户问"书里第 X 章说了什么 / 关于 Y 的原话是什么 / 这个结论的原文依据在哪一页"时，
agent 只能靠能力卡的 R 段（≤150 字引用）或记忆硬答——会编造页码、断章取义。

外部同类项目的共同解法是**分层回源**：
- book-to-skill：`SKILL.md` 只放索引（~4k token），`chapters/ch01-*.md` 每章一个（~1k token），
  问答时按需读对应章节文件再回答（宣称比整本塞上下文省 24–51× token）。
- crayon-ai：两级检索——先读章节摘要，需要精确原文再 grep 原文，回答带页码出处。

## 2. 决策

在 Capability Bundle 侧车新增可选的 **book 级查阅源**，由编译器自动打包并在入口写明查阅路由：

```
books/<slug>/.cangjie/capabilities/book/source/
├── chapters.md          # 章节摘要（每章: 定位(章节/页码) + 一句话 + 要点 + 关键原文位置）
└── fulltext.md          # 原书全文纯文本（可选；⚠ 版权敏感，只允许进本地产物，外发/发布前必须移除）
```

编译行为（`compile_single.py build_tree`）：
1. `book/source/chapters.md` 存在 → 打包为 `references/source/chapters.md`；
2. `book/source/fulltext.md` 存在 → 打包为 `references/source/fulltext.md`；
3. 入口「非能力类查询」新增一行（仅当 chapters.md 存在时写入）：
   书中具体内容/章节细节/原文说法 → `references/source/chapters.md`（两级检索：先查章节摘要，需要逐字原文且 fulltext.md 存在时再回源 fulltext）；
4. 「加载规则」新增一条：回答书中事实类问题必须回源 `references/source/` 核对，不得凭能力卡或记忆编造原文、页码、章节号。

## 3. 为什么这样做（备选方案对比）

| 方案 | 判定 |
|---|---|
| **A. book 级 source 侧车（本 ADR）** | 零 schema 改动、可选目录、single/pack 一处改动两边生效（pack 路由入口复用 `build_tree`）；晋级 Skill 保持自包含不携带查阅层，符合既有不变量 3 |
| B. 挂在 per-capability `resources/` | resources 语义是"能力配套资源"，逐能力重复声明章节文件 = 大量重复打包，且入口无法统一路由 |
| C. 随产物携带 `.cangjie/index/` SQLite | 检索强但宿主 agent 读 SQLite 不如读 Markdown 直接；保留为 `.cangjie/index/` 供流水线内检索用，不进产物 |
| D. 不做，靠能力卡 R 段回答查阅问题 | R 段 ≤150 字且只覆盖被建卡的内容，覆盖率远低于全书，必然诱发编造页码 |

## 4. chapters.md 产出方式

- 优先在阶段 0/1 顺手聚合：阶段 0 的骨架 + 阶段 1 分块时的 `heading_path` 天然构成章节地图，无需重读全书；
- 存量已蒸馏的书：按 `BOOK_OVERVIEW.md` + `coverage-audit.md` + 章节目录补写一次即可，不重跑流水线；
- 大书/套装：按分册标注册号；抽样蒸馏的书照实在文件头标注"采样蒸馏"。

## 5. 兼容性与安全

- **向后兼容**：`book/source/` 不存在时编译行为与改动前一致；已发布产物不受影响，更新时随 update 流程自然获得。
- **校验**：`validate_skill_pack.py` 无白名单限制，`references/source/*.md` 只受"UTF-8 + 链接存在"既有校验约束；入口只在文件真实存在时写入引用，不会产生死链。
- **版权**：fulltext.md 遵循"仅本地留存、不外发"的立场；`BUILD_MANIFEST.json` 如实登记文件哈希便于事后审计。引文红线（≤150 字/段）不变。
- **评测接口**：`output_cases` 可新增"查阅类 case"——prompt 为书中事实问题，assertions 断言回答含正确页码/原文命中（`contains`/`regex`），并配 `not_contains` 拒绝凭空编造的页码。

## 6. 配套：输入端确定性提取

同一背景下的第二个改动：新增 `scripts/extract_text.py`（详见该文件 docstring），
把 PDF/EPUB/DOCX/TXT 确定性转为 `*-fulltext.txt` + 提取报告（含扫描版检测与 OCR 指引），
补上"输入要求"环节缺失的备料自动化；常见环境实测 PyMuPDF / pypdf / python-docx 可直接可用，
ocrmypdf 缺失时自动检测并给出安装指引（不硬依赖）。
