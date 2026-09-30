#!/usr/bin/env python3
"""impact_analysis.py — 依赖图构建 + change-set 影响范围分析（Phase 2B，纯确定性）。

build 模式：从 Capability Bundle（+ 可选 chunks.jsonl）构建带类型的依赖图
（dependency-graph.schema.json）：source→chunk→capability→entrypoint→eval。

analyze 模式：给定 change-set，沿图向下找：
1. 直接依赖变更块的能力（chunk_id 精确匹配，或 source_evidence.location 与块 heading_path 的文本匹配）；
2. 这些能力编译成的入口（single 入口 / 晋级 Skill / 来源路由入口）；
3. also_read 邻居能力（对比/组合关系需一并回归）；
4. 覆盖这些能力的评测用例。

匹配不到任何能力的 additive 变更 → 标注为"新知识候选"，交给 Agent 做增量提取。

用法:
  python3 scripts/impact_analysis.py build --bundle <dir> [--chunks <chunks.jsonl>] --out <graph.json>
  python3 scripts/impact_analysis.py analyze --graph <graph.json> --change-set <cs.json> --out <report.md>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import TOOL_VERSION, dump_json, load_json, load_yaml  # noqa: E402


def build_graph(bundle_dir: Path, chunks_path: Path | None) -> dict:
    bundle = load_yaml(bundle_dir / "verified.yaml")
    router_name = bundle["router_entry"]["name"]
    nodes: list[dict] = []
    edges: list[dict] = []

    def add_node(node_id: str, node_type: str, label: str = "") -> None:
        nodes.append({"node_id": node_id, "node_type": node_type, "label": label})

    chunks = []
    if chunks_path and chunks_path.exists():
        chunks = [json.loads(l) for l in chunks_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        if chunks:
            sv = f"{chunks[0]['source_id']}@{chunks[0]['version_id']}"
            add_node(sv, "source_version")
            for c in chunks:
                add_node(c["chunk_id"], "chunk", " / ".join(c["heading_path"]))
                edges.append({"from": sv, "to": c["chunk_id"], "edge_type": "contains"})

    add_node(router_name, "entrypoint", "来源路由入口")
    for cap in bundle["capabilities"]:
        cid = cap["capability_id"]
        add_node(cid, "capability", cap["title"])
        # 证据边：chunk_id 精确匹配 + location 与 heading_path 的文本匹配
        for ev in cap.get("source_evidence", []):
            for chunk_id in ev.get("chunk_ids", []):
                edges.append({"from": chunk_id, "to": cid, "edge_type": "supports", "evidence": "chunk_ids"})
            loc = str(ev.get("location", "")).strip()
            if loc and chunks:
                # 章节粒度匹配：location 的任一段与块 heading 的任一段互为子串即建边。
                # 宁可过近似（多回归）不可漏（少回归）。
                loc_segs = [s.strip() for s in loc.split("/") if len(s.strip()) >= 3]
                for c in chunks:
                    hp_segs = [s for s in c["heading_path"] if len(s) >= 3]
                    if any(ls in hs or hs in ls for ls in loc_segs for hs in hp_segs):
                        edges.append({"from": c["chunk_id"], "to": cid, "edge_type": "supports",
                                      "evidence": f"location~heading(章节粒度): {loc}"})
        # 编译去向
        if cap.get("promotion", {}).get("destination") == "promoted":
            add_node(cap["slug"], "entrypoint", f"晋级 Skill: {cap['title']}")
            edges.append({"from": cid, "to": cap["slug"], "edge_type": "compiled_as"})
        edges.append({"from": cid, "to": router_name, "edge_type": "served_by"})
        # 邻居
        slug_to_id = {c["slug"]: c["capability_id"] for c in bundle["capabilities"]}
        for sib in cap.get("also_read", []):
            if sib in slug_to_id:
                edges.append({"from": cid, "to": slug_to_id[sib], "edge_type": "composes_with"})

    return {
        "schema_version": 1,
        "content_pack": bundle["book"].get("source_pack", bundle["bundle_id"]),
        "generated_by": TOOL_VERSION,
        "nodes": nodes,
        "edges": edges,
    }


def analyze(graph: dict, change_set: dict) -> str:
    edges = graph["edges"]
    labels = {n["node_id"]: n.get("label", "") for n in graph["nodes"]}
    node_types = {n["node_id"]: n["node_type"] for n in graph["nodes"]}
    chunk_headings = {n["node_id"]: n.get("label", "") for n in graph["nodes"] if n["node_type"] == "chunk"}

    affected_caps: dict[str, list[str]] = {}
    orphan_changes: list[dict] = []

    for ch in change_set["changes"]:
        hit = False
        # 1) chunk_id 精确匹配
        for e in edges:
            if e["edge_type"] in ("supports", "contradicts", "examples") and e["from"] == ch["chunk_id"]:
                affected_caps.setdefault(e["to"], []).append(f"{ch['change_type']}:{ch['chunk_id']}")
                hit = True
        # 2) heading_path 文本匹配（新版本块的 chunk_id 不在旧图中时）
        if not hit and ch.get("heading_path"):
            hp_new = " / ".join(ch["heading_path"])
            for cid_chunk, hp in chunk_headings.items():
                if hp and (hp in hp_new or hp_new in hp):
                    for e in edges:
                        if e["edge_type"] == "supports" and e["from"] == cid_chunk:
                            affected_caps.setdefault(e["to"], []).append(f"{ch['change_type']}:{hp_new}")
                            hit = True
        if not hit and ch["change_type"] == "additive":
            orphan_changes.append(ch)

    # 沿图向下：能力 → 入口 / 邻居 / 评测
    affected_entrypoints: set[str] = set()
    neighbor_caps: set[str] = set()
    affected_evals: set[str] = set()
    for cap in affected_caps:
        for e in edges:
            if e["from"] == cap and e["edge_type"] in ("compiled_as", "served_by"):
                affected_entrypoints.add(e["to"])
            if e["edge_type"] in ("composes_with", "compared_with", "depends_on") and cap in (e["from"], e["to"]):
                other = e["to"] if e["from"] == cap else e["from"]
                if node_types.get(other) == "capability" and other not in affected_caps:
                    neighbor_caps.add(other)
            if e["edge_type"] == "covers" and e["to"] == cap:
                affected_evals.add(e["from"])

    lines = ["# 影响范围分析", "",
             f"- change-set: `{change_set['change_id']}`（+{change_set['summary']['added']} / "
             f"-{change_set['summary']['removed']} / ~{change_set['summary']['modified']}）", ""]
    lines.append(f"## 受影响能力（{len(affected_caps)}）\n")
    for cap, reasons in sorted(affected_caps.items()):
        lines.append(f"- `{cap}` {labels.get(cap, '')} ← {'; '.join(sorted(set(reasons))[:3])}")
    lines.append(f"\n## 需重编译/回归的入口（{len(affected_entrypoints)}）\n")
    for ep in sorted(affected_entrypoints):
        lines.append(f"- `{ep}` {labels.get(ep, '')}")
    lines.append(f"\n## 需一并回归的邻居能力（{len(neighbor_caps)}）\n")
    for cap in sorted(neighbor_caps):
        lines.append(f"- `{cap}` {labels.get(cap, '')}")
    if affected_evals:
        lines.append(f"\n## 覆盖这些能力的评测（{len(affected_evals)}）\n")
        lines += [f"- `{e}`" for e in sorted(affected_evals)]
    lines.append(f"\n## 未命中任何既有能力的新增块（{len(orphan_changes)}）——新知识候选\n")
    for ch in orphan_changes:
        lines.append(f"- {ch['chunk_id']} [{' / '.join(ch.get('heading_path', []))}]")
    lines.append("\n> 未受影响的能力/入口不重编译，文件哈希保持不变（增量验收要求 §6.5）。")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="mode", required=True)
    b = sub.add_parser("build")
    b.add_argument("--bundle", required=True)
    b.add_argument("--chunks", default=None)
    b.add_argument("--out", required=True)
    a = sub.add_parser("analyze")
    a.add_argument("--graph", required=True)
    a.add_argument("--change-set", required=True)
    a.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.mode == "build":
        graph = build_graph(Path(args.bundle), Path(args.chunks) if args.chunks else None)
        dump_json(Path(args.out), graph)
        print(f"依赖图: {args.out}（{len(graph['nodes'])} nodes / {len(graph['edges'])} edges）")
    else:
        report = analyze(load_json(Path(args.graph)), load_json(Path(args.change_set)))
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(report, encoding="utf-8")
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
