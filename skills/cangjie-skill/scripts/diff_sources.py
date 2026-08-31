#!/usr/bin/env python3
"""diff_sources.py — 两个版本的块清单 → change-set（Phase 2B，纯确定性）。

判定规则（确定性部分）：
- content_hash 相同                → unchanged / exact_duplicate（同版本内重复出现时）
- 同 heading_path 且哈希不同       → modified（是否为 correction/contradiction 属语义判断，
                                     标记 requires_human_confirmation 交给 Agent 复核）
- 新版本独有                        → additive
- 旧版本独有                        → deletion（不物理删除历史证据，只进影响分析）

near_duplicate / correction / contradiction 的语义定性不在本脚本伪造——路线 C 下由 Agent
按 methodology 合并规则复核后回填 change-set。

用法: python3 scripts/diff_sources.py <old-chunks.jsonl> <new-chunks.jsonl> --out <change-set.json> [--pack <slug>]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import dump_json  # noqa: E402


def load_chunks(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def diff(old: list[dict], new: list[dict]) -> list[dict]:
    old_by_hash = {c["content_hash"]: c for c in old}
    new_by_hash = {c["content_hash"]: c for c in new}
    changes: list[dict] = []

    unchanged_hashes = old_by_hash.keys() & new_by_hash.keys()

    old_rest = [c for c in old if c["content_hash"] not in unchanged_hashes]
    new_rest = [c for c in new if c["content_hash"] not in unchanged_hashes]

    # 同 heading_path 配对为 modified
    old_by_path: dict[str, list[dict]] = {}
    for c in old_rest:
        old_by_path.setdefault(" / ".join(c["heading_path"]), []).append(c)

    for c in new_rest:
        path_key = " / ".join(c["heading_path"])
        pool = old_by_path.get(path_key)
        if pool:
            o = pool.pop(0)
            changes.append({
                "change_type": "modified",
                "chunk_id": c["chunk_id"],
                "old_hash": o["content_hash"],
                "new_hash": c["content_hash"],
                "heading_path": c["heading_path"],
                "requires_human_confirmation": True,
                "note": "同章节内容变化；是否为 correction/contradiction 需 Agent 语义复核",
            })
        else:
            changes.append({
                "change_type": "additive",
                "chunk_id": c["chunk_id"],
                "old_hash": None,
                "new_hash": c["content_hash"],
                "heading_path": c["heading_path"],
                "requires_human_confirmation": False,
                "note": "新增内容，进入影响分析与增量候选提取",
            })

    for pool in old_by_path.values():
        for o in pool:
            changes.append({
                "change_type": "deletion",
                "chunk_id": o["chunk_id"],
                "old_hash": o["content_hash"],
                "new_hash": None,
                "heading_path": o["heading_path"],
                "requires_human_confirmation": True,
                "note": "来源撤回/删除；不立即物理删除历史证据，先计算受影响能力",
            })
    return changes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("old_chunks")
    ap.add_argument("new_chunks")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pack", default="")
    args = ap.parse_args()

    old = load_chunks(Path(args.old_chunks))
    new = load_chunks(Path(args.new_chunks))
    changes = diff(old, new)
    unchanged = len({c["content_hash"] for c in old} & {c["content_hash"] for c in new})

    change_set = {
        "schema_version": 1,
        "change_id": time.strftime("chg-%Y%m%d-%H%M%S"),
        "content_pack": args.pack,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "base_version": old[0]["version_id"] if old else None,
        "new_version": new[0]["version_id"] if new else None,
        "changes": changes,
        "summary": {
            "added": sum(1 for c in changes if c["change_type"] == "additive"),
            "removed": sum(1 for c in changes if c["change_type"] == "deletion"),
            "modified": sum(1 for c in changes if c["change_type"] == "modified"),
            "unchanged": unchanged,
        },
    }
    dump_json(Path(args.out), change_set)
    s = change_set["summary"]
    print(f"change-set: {args.out}（+{s['added']} / -{s['removed']} / ~{s['modified']} / ={s['unchanged']}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
