#!/usr/bin/env python3
"""compile_single.py — 从 Capability Bundle 确定性编译 single 入口（v0.2，Bundle 原生）。

输入是唯一编译事实源 Capability Bundle（ADR-002）：

    <bundle-dir>/                    # 通常是 books/<slug>/.cangjie/capabilities/
    ├── verified.yaml                # capability-bundle.schema.json
    ├── destinations.json            # 去向映射
    ├── cards/<slug>.md              # RIA 能力卡（R/I/A1/A2/E/B，正文逐字保留）
    └── book/{overview.md,glossary.md}

输出（--variant single）：1 个发现入口 + 全部能力卡 + overview/glossary/cheatsheet/索引。
--variant router 生成 compact pack 的来源路由入口视图（晋级能力在路由表标注改由独立 Skill 处理）。

本脚本纯确定性、不调用模型。主入口 description、核心原则、意图路由全部来自 Bundle，脚本不猜测。
v0.1 的 --map 模式（Phase 0 原型）已由 `cangjie.py migrate-legacy` + Bundle 取代。

用法: python3 scripts/compile_single.py --bundle <dir> --out <dir> [--variant single|router]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import TOOL_VERSION, load_yaml  # noqa: E402

MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)#\s]+?)(?:#[^)\s]*)?\)")


def sanitize_links(text: str, available: set[str]) -> str:
    """把指向未随产物分发文件的相对链接降级为纯文本，避免死链。"""

    def repl(m: re.Match) -> str:
        target = m.group(2)
        if target.startswith(("http://", "https://", "mailto:", "/")):
            return m.group(0)
        return m.group(0) if target.lstrip("./") in available else m.group(1)

    return MD_LINK_RE.sub(repl, text)


def active_capabilities(bundle: dict) -> list[dict]:
    return [c for c in bundle["capabilities"] if c.get("status", "active") == "active"]


def promoted_capabilities(bundle: dict) -> list[dict]:
    return [c for c in active_capabilities(bundle) if c.get("promotion", {}).get("destination") == "promoted"]


def router_table(caps: list[dict], variant: str) -> str:
    rows = ["| 用户意图 | 先读 | 补读/备注 |", "|---|---|---|"]
    for cap in caps:
        intents = "；".join(cap["intents"])
        card = f"references/capabilities/{cap['slug']}.md"
        extra = "、".join(f"references/capabilities/{s}.md" for s in cap.get("also_read", [])) or "—"
        if variant == "router" and cap.get("promotion", {}).get("destination") == "promoted":
            extra = f"已晋级为独立 Skill `{cap['slug']}`（已安装时优先直接使用；本卡仅作原文与背景补充）"
        rows.append(f"| {intents} | {card} | {extra} |")
    return "\n".join(rows)


def build_entry_md(bundle: dict, variant: str) -> str:
    entry = bundle["entry"] if variant == "single" else bundle["router_entry"]
    caps = active_capabilities(bundle)
    book = bundle["book"]
    entrypoint_count = 1 if variant == "single" else 1 + len(promoted_capabilities(bundle))
    fm_lines = [
        "---",
        f"name: {entry['name']}",
        "description: |",
        *[f"  {line}" for line in entry["description"].strip().splitlines()],
        "metadata:",
        f"  cangjie.generated-by: {TOOL_VERSION}",
        f"  cangjie.variant: {variant}",
        f"  cangjie.bundle-id: {bundle['bundle_id']}",
        f"  cangjie.capability-count: {len(caps)}",
        f"  cangjie.entrypoint-count: {entrypoint_count}",
        "---",
        "",
    ]
    e = bundle["entry"]
    principles = "\n".join(f"{i}. {p}" for i, p in enumerate(e["core_principles"], 1))
    out_of_scope = "\n".join(f"- {x}" for x in e["out_of_scope"])
    stops = "\n".join(f"- {x}" for x in e["stop_conditions"])

    body = f"""# {book['title']} — {'全书能力入口' if variant == 'single' else '来源路由入口（compact pack）'}

## 触发与不触发

**适用**：与本书能力域相关的咨询与任务（见下方路由表的意图列）。
**不适用**：
{out_of_scope}

## 核心原则（常驻速览，概览类问题读到这里即可回答）

{principles}

## 能力路由（先读本表，按意图加载 1 张能力卡）

{router_table(caps, variant)}

**非能力类查询**：
- 书名/作者/章节/整书概览 → references/overview.md
- 术语解释 → references/glossary.md
- 决策规则速查（不需要原文依据时） → references/cheatsheet.md
- 完整意图与关键词索引（本表未覆盖的意图先查这里） → references/capability-index.md

## 加载规则

- 每次任务先读本文件，再按路由表加载 **1** 张能力卡；任务明确跨域时最多加载 2 张。
- 概览/书名类问题不加载能力卡，用「核心原则」与 overview.md 回答。
- 路由表与 capability-index.md 都无法命中的意图，明确告知超出本书范围，不要硬套。

## 边界与判停

{stops}
"""
    return "\n".join(fm_lines) + body


def build_index_md(caps: list[dict]) -> str:
    rows = ["# 能力索引（完整版）", "", "| capability_id | 标题 | 重要度 | 意图 | 关键词 | 能力卡 |", "|---|---|---|---|---|---|"]
    for c in caps:
        rows.append(
            f"| {c['capability_id']} | {c['title']} | {c['importance']} | {'；'.join(c['intents'])} | "
            f"{'、'.join(c['keywords'])} | capabilities/{c['slug']}.md |"
        )
    return "\n".join(rows) + "\n"


def build_cheatsheet_md(caps: list[dict], book: dict) -> str:
    rows = [f"# 决策规则速查 — {book['title']}", "", "| 能力 | 一句话规则 |", "|---|---|"]
    for c in caps:
        rows.append(f"| {c['title']} | {c['one_liner']} |")
    rows.append("")
    rows.append("> 速查只给结论；需要原文依据、案例或反例时读对应能力卡。")
    return "\n".join(rows) + "\n"


def build_tree(bundle_dir: Path, variant: str) -> dict[str, str]:
    """返回 {相对路径: 内容}。纯函数，供 compile_pack.py 与 cangjie.py 复用。"""
    bundle = load_yaml(bundle_dir / "verified.yaml")
    caps = active_capabilities(bundle)

    files: dict[str, str] = {}
    files["SKILL.md"] = build_entry_md(bundle, variant)
    for cap in caps:
        files[f"references/capabilities/{cap['slug']}.md"] = (bundle_dir / cap["card"]).read_text(encoding="utf-8")
    files["references/capability-index.md"] = build_index_md(caps)
    files["references/cheatsheet.md"] = build_cheatsheet_md(caps, bundle["book"])

    available = {p.removeprefix("references/") for p in files if p.startswith("references/")}
    for name in ("overview.md", "glossary.md"):
        src = bundle_dir / "book" / name
        if src.exists():
            files[f"references/{name}"] = sanitize_links(src.read_text(encoding="utf-8"), available)
    return files


def write_tree(files: dict[str, str], out: Path) -> None:
    for rel, content in files.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", required=True, help="Capability Bundle 目录（含 verified.yaml）")
    ap.add_argument("--out", required=True)
    ap.add_argument("--variant", choices=["single", "router"], default="single")
    args = ap.parse_args()

    files = build_tree(Path(args.bundle), args.variant)
    write_tree(files, Path(args.out))
    print(f"已生成 {args.variant} 产物: {args.out}（{len(files)} 个文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
