#!/usr/bin/env python3
"""update_flow.py — `cangjie.py update` 的编排逻辑（Phase 2B，路线 C）。

CLI 只做确定性部分：登记来源 → 切块 → diff → change-set → 影响分析。
需要语义判断的节点（增量候选提取、correction/contradiction 定性、合并规则应用）
生成待处理 Agent 任务清单，由 Agent 按 methodology 完成后再交回 CLI 校验与重编译。
"""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from build_chunks import build as build_chunks_for  # noqa: E402
from cangjie_common import create_run_workdir, load_yaml, new_run_id, sha256_file  # noqa: E402
from diff_sources import diff as diff_chunks, load_chunks  # noqa: E402
from impact_analysis import analyze, build_graph  # noqa: E402
from cangjie_common import dump_json  # noqa: E402


def ensure_manifest(pack: Path) -> dict:
    manifest_path = pack / ".cangjie" / "manifest.yaml"
    if manifest_path.exists():
        return load_yaml(manifest_path)
    manifest = {"schema_version": 1, "content_pack": pack.name, "sources": []}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return manifest


def run_update(pack: Path, new_source: Path) -> int:
    sidecar = pack / ".cangjie"
    bundle_dir = sidecar / "capabilities"
    if not (bundle_dir / "verified.yaml").exists():
        raise SystemExit(f"未找到 Capability Bundle: {bundle_dir}/verified.yaml（旧 pack 先运行 migrate-legacy）")

    run_id = new_run_id()
    workdir = create_run_workdir(sidecar, run_id)

    # 1. 登记来源版本
    manifest_path = sidecar / "manifest.yaml"
    manifest = ensure_manifest(pack)
    source_id = f"src-{new_source.stem.lower().replace(' ', '-')[:32]}"
    version_id = f"sha256:{sha256_file(new_source)}"
    entry = next((s for s in manifest["sources"] if s["source_id"] == source_id), None)
    if entry is None:
        entry = {"source_id": source_id, "kind": "other", "title": new_source.stem,
                 "uri": new_source.resolve().as_uri(), "rights": "user-provided", "trust": "primary",
                 "versions": []}
        manifest["sources"].append(entry)
    if any(v["version_id"] == version_id for v in entry["versions"]):
        print(f"[skip] 该来源版本已登记（exact duplicate）: {version_id[:23]}…")
        return 0
    for v in entry["versions"]:
        if v["status"] == "active":
            v["status"] = "superseded"
    entry["versions"].append({"version_id": version_id, "added_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                              "parser": "build_chunks v1.0", "status": "active"})
    manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # 2. 切块（旧版本块先备份用于 diff）
    chunks_path = sidecar / "chunks" / "chunks.jsonl"
    old_chunks_backup = None
    if chunks_path.exists():
        old_chunks_backup = workdir / "old-chunks.jsonl"
        shutil.copyfile(chunks_path, old_chunks_backup)
    build_chunks_for(new_source, sidecar, source_id, 4000)

    # 3. diff → change-set
    old = load_chunks(old_chunks_backup) if old_chunks_backup else []
    new = load_chunks(chunks_path)
    changes = diff_chunks(old, new)
    change_set = {
        "schema_version": 1,
        "change_id": f"chg-{run_id}",
        "content_pack": pack.name,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "base_version": old[0]["version_id"] if old else None,
        "new_version": version_id,
        "changes": changes,
        "summary": {
            "added": sum(1 for c in changes if c["change_type"] == "additive"),
            "removed": sum(1 for c in changes if c["change_type"] == "deletion"),
            "modified": sum(1 for c in changes if c["change_type"] == "modified"),
            "unchanged": len({c["content_hash"] for c in old} & {c["content_hash"] for c in new}),
        },
    }
    cs_path = sidecar / "changes" / f"{change_set['change_id']}.json"
    dump_json(cs_path, change_set)

    # 4. 影响分析
    graph = build_graph(bundle_dir, chunks_path)
    dump_json(sidecar / "graph" / "dependencies.json", graph)
    report = analyze(graph, change_set)
    (workdir / "impact-report.md").write_text(report, encoding="utf-8")

    # 5. 生成待处理 Agent 任务（语义节点不由 CLI 伪造）
    pending = [f"# update 待处理任务（run: {run_id}）", "",
               f"change-set: `{cs_path}`；影响分析: `{workdir / 'impact-report.md'}`", "",
               "按 `methodology/` 合并规则逐项处理（CLI 不做语义判断）：", ""]
    need_confirm = [c for c in changes if c.get("requires_human_confirmation")]
    additive = [c for c in changes if c["change_type"] == "additive"]
    if additive:
        pending.append(f"1. **增量候选提取**：对 {len(additive)} 个新增块跑阶段 1（可用检索式取块），"
                       "新候选走阶段 1.5 三重验证 → 阶段 1.6 晋级门 → 更新 Bundle；")
    if need_confirm:
        pending.append(f"2. **人工确认项（{len(need_confirm)}）**：modified/deletion 块需定性 "
                       "correction / contradiction / near_duplicate，冲突不得静默综合（§6.4）；")
    pending += ["3. Bundle 更新后运行 `cangjie.py compile`（沿用原输出策略）重编译受影响入口；",
                "4. 运行受影响能力 + 邻居能力的回归评测（见影响分析报告）。", "",
                "> 未受影响的能力/入口不重编译，文件哈希保持不变。"]
    (workdir / "pending-tasks.md").write_text("\n".join(pending) + "\n", encoding="utf-8")

    print(report)
    print(f"待处理任务: {workdir / 'pending-tasks.md'}")
    return 0
