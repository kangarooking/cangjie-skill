#!/usr/bin/env python3
"""compile_pack.py — 从 Capability Bundle 确定性编译 compact pack（方案 §4.6.3）。

产物固定为「1 个来源路由入口 + 少量晋级 Skill + 内部能力卡」：

    <out>/
    ├── <router-name>/                    # 来源路由入口（全部能力卡保留在其目录内）
    │   ├── SKILL.md
    │   └── references/...
    ├── <promoted-slug>/                  # 晋级 Skill：从同一 Bundle 编译的自包含入口
    │   └── SKILL.md
    └── capability-destinations.json      # 发布审计清单（不作为宿主发现入口）

硬不变量（编译时校验，违反即失败）：
1. 每个 active capability 恰好一个主要去向（promoted_to 或 served_by）；
2. 未晋级能力必须可经来源路由入口到达（能力卡 + 索引行都存在）；
3. 晋级 Skill 自包含，不引用跨 Skill 根目录的相对路径；
4. 可发现入口总数 <= promotion_budget（超出需 --allow-over-budget 并逐项解释）。

用法: python3 scripts/compile_pack.py --bundle <dir> --out <dir> [--allow-over-budget]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import TOOL_VERSION, dump_json, load_yaml  # noqa: E402
from compile_single import active_capabilities, build_tree, promoted_capabilities, write_tree  # noqa: E402


def build_promoted_skill_md(cap: dict, bundle: dict, card_text: str) -> str:
    fm = cap.get("frontmatter", {})
    description = fm.get("description") or f"{'；'.join(cap['intents'])}。{cap['one_liner']}"
    tags = fm.get("tags", [])
    lines = [
        "---",
        f"name: {cap['slug']}",
        "description: |",
        *[f"  {line}" for line in description.strip().splitlines()],
        "metadata:",
        f"  cangjie.generated-by: {TOOL_VERSION}",
        f"  cangjie.capability-id: {cap['capability_id']}",
        f"  cangjie.capability-revision: {cap['revision']}",
        f"  cangjie.bundle-id: {bundle['bundle_id']}",
        f"  cangjie.source-title: {bundle['book']['title']}",
    ]
    if tags:
        lines.append(f"  cangjie.tags: {', '.join(tags)}")
    lines += ["---", ""]
    return "\n".join(lines) + card_text


def compile_pack_tree(bundle_dir: Path, *, allow_over_budget: bool = False) -> dict[str, str]:
    """返回 {相对路径: 内容}，含路由入口、晋级 Skill 与 destinations 审计清单。"""
    bundle = load_yaml(bundle_dir / "verified.yaml")
    caps = active_capabilities(bundle)
    promoted = promoted_capabilities(bundle)
    router_name = bundle["router_entry"]["name"]
    budget = int(bundle.get("promotion_budget", 8))

    # 不变量 1：每个 active capability 恰好一个主要去向
    for cap in caps:
        dest = cap.get("promotion", {}).get("destination")
        if dest not in ("promoted", "router"):
            raise SystemExit(f"[invariant] {cap['capability_id']}: promotion.destination 必须是 promoted|router，当前 {dest!r}")

    # 不变量 4：入口预算
    entrypoint_count = 1 + len(promoted)
    if entrypoint_count > budget and not allow_over_budget:
        raise SystemExit(f"[invariant] 可发现入口 {entrypoint_count} 超出软预算 {budget}；确需超出请 --allow-over-budget 并在发布说明逐项解释")

    files: dict[str, str] = {}

    # 来源路由入口（复用 single 编译逻辑的 router 视图；全部能力卡保留）
    for rel, content in build_tree(bundle_dir, "router").items():
        files[f"{router_name}/{rel}"] = content

    # 晋级 Skill：自包含，不引用跨目录路径（不变量 3 由内容构造保证 + 校验兜底）
    for cap in promoted:
        card_text = (bundle_dir / cap["card"]).read_text(encoding="utf-8")
        skill_md = build_promoted_skill_md(cap, bundle, card_text)
        if "references/capabilities/" in skill_md or f"../{router_name}" in skill_md:
            raise SystemExit(f"[invariant] 晋级 Skill {cap['slug']} 引用了跨目录路径，必须自包含")
        files[f"{cap['slug']}/SKILL.md"] = skill_md

    # 不变量 2：未晋级能力在路由入口可达
    for cap in caps:
        if cap["promotion"]["destination"] == "router":
            card_rel = f"{router_name}/references/capabilities/{cap['slug']}.md"
            if card_rel not in files:
                raise SystemExit(f"[invariant] 未晋级能力 {cap['capability_id']} 在路由入口不可达（缺 {card_rel}）")

    destinations = {
        "generated_by": TOOL_VERSION,
        "bundle_id": bundle["bundle_id"],
        "router_entrypoint": router_name,
        "entrypoint_count": entrypoint_count,
        "capability_count": len(caps),
        "destinations": {
            cap["capability_id"]: (
                {"promoted_to": cap["slug"], "router_view": f"{router_name}/references/capabilities/{cap['slug']}.md"}
                if cap["promotion"]["destination"] == "promoted"
                else {"served_by": router_name, "card": f"{router_name}/references/capabilities/{cap['slug']}.md"}
            )
            for cap in caps
        },
    }
    import json

    files["capability-destinations.json"] = json.dumps(destinations, ensure_ascii=False, indent=2) + "\n"
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-over-budget", action="store_true")
    args = ap.parse_args()

    files = compile_pack_tree(Path(args.bundle), allow_over_budget=args.allow_over_budget)
    write_tree(files, Path(args.out))
    entry_count = sum(1 for rel in files if rel.endswith("/SKILL.md"))
    print(f"已生成 compact pack: {args.out}（{entry_count} 个入口，{len(files)} 个文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
