#!/usr/bin/env python3
"""run_output_evals.py — 输出评测的确定性环节（Phase 3，路线 C）。

  prepare  为每条 output case 生成 old/new/without 三个匿名任务包（盲测：包名随机化标签，
           映射表单独存放，不给评审者）
  score    对记录的输出跑机械断言（contains/not_contains/regex/file_exists/json_path），
           机械断言先于 LLM judge；盲评分歧样本留给人工复核

outputs 目录约定: <outputs>/<case_id>/<variant-label>.md（variant-label 来自 prepare 的映射表）

用法:
  python3 scripts/run_output_evals.py prepare <suite.json> --out <dir> [--variants old_skill,new_skill,without_skill]
  python3 scripts/run_output_evals.py score   <suite.json> --outputs <dir> --mapping <mapping.json> --out <report.md>
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import dump_json, load_json  # noqa: E402


def check_assertion(a: dict, text: str, base: Path) -> bool:
    kind, value = a["kind"], a["value"]
    if kind == "contains":
        return value in text
    if kind == "not_contains":
        return value not in text
    if kind == "regex":
        return re.search(value, text) is not None
    if kind == "file_exists":
        return (base / value).exists()
    if kind == "json_path":  # 简化版: 顶层 key 存在于输出中的 JSON 块
        try:
            data = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
        except Exception:
            return False
        cur = data
        for part in value.lstrip("$.").split("."):
            if not isinstance(cur, dict) or part not in cur:
                return False
            cur = cur[part]
        return True
    raise ValueError(f"未知断言类型: {kind}")


def cmd_prepare(suite_path: Path, out_dir: Path, variants: list[str]) -> int:
    suite = load_json(suite_path)
    rng = random.Random(suite.get("split_seed", 42))
    out_dir.mkdir(parents=True, exist_ok=True)
    mapping: dict[str, dict[str, str]] = {}
    for c in suite.get("output_cases", []):
        labels = [f"v{chr(65 + i)}" for i in range(len(variants))]
        rng.shuffle(labels)
        mapping[c["case_id"]] = dict(zip(labels, variants))
        case_dir = out_dir / c["case_id"]
        case_dir.mkdir(exist_ok=True)
        for label in labels:
            dump_json(case_dir / f"task-{label}.json", {
                "case_id": c["case_id"], "variant_label": label, "prompt": c["prompt"],
                "input_files": c.get("input_files", []),
                "instruction": "按 prompt 完成任务，输出保存为同目录 <label>.md。评审者不知道你是哪个版本。",
            })
    dump_json(out_dir / "mapping.json", mapping)
    print(f"已生成 {len(mapping)} 条 output 任务（每条 {len(variants)} 个匿名变体）→ {out_dir}\n"
          f"映射表 {out_dir / 'mapping.json'} 不要给评审 sub-agent。")
    return 0


def cmd_score(suite_path: Path, outputs: Path, mapping_path: Path, out_path: Path) -> int:
    suite = load_json(suite_path)
    mapping = load_json(mapping_path)
    lines = [f"# 输出评测机械断言判分 — {suite['target']}", ""]
    totals: dict[str, list[int]] = {}
    for c in suite.get("output_cases", []):
        case_map = mapping.get(c["case_id"], {})
        lines.append(f"## {c['case_id']}\n")
        lines.append("| 变体 | 断言通过 | 明细 |")
        lines.append("|---|---|---|")
        for label, variant in sorted(case_map.items()):
            f = outputs / c["case_id"] / f"{label}.md"
            if not f.exists():
                lines.append(f"| {variant} | — | 输出缺失: {f.name} |")
                continue
            text = f.read_text(encoding="utf-8")
            results = [(a, check_assertion(a, text, f.parent)) for a in c["assertions"]]
            passed = sum(1 for _, ok in results if ok)
            detail = "; ".join(f"{'✓' if ok else '✗'}{a['kind']}:{a['value'][:24]}" for a, ok in results)
            lines.append(f"| {variant} | {passed}/{len(results)} | {detail} |")
            totals.setdefault(variant, []).append(int(passed == len(results)))
        lines.append("")
    lines.append("## 汇总（全部断言通过的 case 比例）\n")
    for variant, arr in sorted(totals.items()):
        lines.append(f"- {variant}: {sum(arr)}/{len(arr)}")
    lines.append("\n> 机械断言先于 LLM judge；A/B 盲评与分歧样本人工复核另行进行，此处不自动宣布非劣。")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("suite")
    p.add_argument("--out", required=True)
    p.add_argument("--variants", default="old_skill,new_skill,without_skill")
    c = sub.add_parser("score")
    c.add_argument("suite")
    c.add_argument("--outputs", required=True)
    c.add_argument("--mapping", required=True)
    c.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.mode == "prepare":
        return cmd_prepare(Path(args.suite), Path(args.out), args.variants.split(","))
    return cmd_score(Path(args.suite), Path(args.outputs), Path(args.mapping), Path(args.out))


if __name__ == "__main__":
    raise SystemExit(main())
