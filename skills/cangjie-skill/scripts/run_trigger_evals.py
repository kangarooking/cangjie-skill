#!/usr/bin/env python3
"""run_trigger_evals.py — 触发评测的确定性环节（Phase 3，路线 C）。

路线 C 下 CLI 不能替宿主跑模型；本脚本负责三件确定性的事：

  split    固定种子做 60/40 train/validation 切分（validation 在选版前保持隐藏）
  prepare  生成盲测任务包：只含 prompt + 候选 skill 目录清单，隐藏 expected/notes，
           由主流程逐条交给干净 sub-agent，结果写 results.jsonl
  score    对照 suite 判分：precision/recall/F1、兄弟混淆率、逐条配对结果
           （不做统计非劣声明——那需要预注册界值与配对检验，见方案 §10.3）

results.jsonl 每行: {"case_id": "...", "run": 1, "selected_skill": "<slug>|none"}

用法:
  python3 scripts/run_trigger_evals.py split   <suite.json>
  python3 scripts/run_trigger_evals.py prepare <suite.json> --skills <slug1,slug2,...> --out <dir> [--set train|validation|all]
  python3 scripts/run_trigger_evals.py score   <suite.json> --results <results.jsonl> --out <report.md>
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import dump_json, load_json  # noqa: E402


def split_cases(suite: dict) -> tuple[list[dict], list[dict]]:
    cases = list(suite["trigger_cases"])
    rng = random.Random(suite.get("split_seed", 42))
    rng.shuffle(cases)
    k = round(len(cases) * suite.get("train_ratio", 0.6))
    return cases[:k], cases[k:]


def cmd_split(suite_path: Path) -> int:
    suite = load_json(suite_path)
    train, val = split_cases(suite)
    out = {"suite_id": suite["suite_id"], "seed": suite.get("split_seed", 42),
           "train": [c["case_id"] for c in train], "validation": [c["case_id"] for c in val]}
    dump_json(suite_path.with_suffix(".split.json"), out)
    print(f"train {len(train)} / validation {len(val)} → {suite_path.with_suffix('.split.json')}")
    return 0


def cmd_prepare(suite_path: Path, skills: list[str], out_dir: Path, which: str) -> int:
    suite = load_json(suite_path)
    train, val = split_cases(suite)
    cases = {"train": train, "validation": val, "all": train + val}[which]
    out_dir.mkdir(parents=True, exist_ok=True)
    for c in cases:
        runs = c.get("runs", 3)
        packet = {
            "case_id": c["case_id"],
            "runs": runs,
            "prompt": c["prompt"],
            "instruction": (
                "你是一个未参与蒸馏的干净 agent。给定用户 prompt 与已安装 skill 清单，"
                "判断该激活哪一个 skill（或 none）。输出 JSON: "
                '{"selected_skill": "<slug>|none", "reason": "..."}。'
                "每条 prompt 独立判断，重复运行之间不携带记忆。"
            ),
            "installed_skills": skills,
        }
        dump_json(out_dir / f"{c['case_id']}.json", packet)
    (out_dir / "README.md").write_text(
        f"# 盲测任务包（{which}, {len(cases)} 条）\n\n"
        "每个 JSON 是一条盲测任务：把 prompt + installed_skills 交给干净 sub-agent，"
        "按 instruction 输出;结果按行追加到 results.jsonl:\n"
        '`{"case_id": ..., "run": 1, "selected_skill": ...}`\n\n'
        "**不要**把 suite 中的 expected/notes 给 sub-agent。\n", encoding="utf-8")
    print(f"已生成 {len(cases)} 个盲测任务包 → {out_dir}")
    return 0


def cmd_score(suite_path: Path, results_path: Path, out_path: Path) -> int:
    suite = load_json(suite_path)
    target = suite["target"]
    by_case = {c["case_id"]: c for c in suite["trigger_cases"]}
    results = [json.loads(l) for l in results_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    tp = fp = fn = tn = 0
    sibling_total = sibling_confused = 0
    rows = ["| case | expected | selected | 判定 |", "|---|---|---|---|"]
    for r in results:
        c = by_case.get(r["case_id"])
        if not c:
            continue
        selected = r.get("selected_skill", "none")
        triggered = selected == target
        exp = c["expected"]
        if exp == "should_trigger":
            verdict = "TP" if triggered else "FN"
            tp += triggered
            fn += not triggered
        elif exp in ("should_not_trigger", "edge_case"):
            verdict = "FP" if triggered else "TN"
            fp += triggered
            tn += not triggered
        else:  # sibling
            sibling_total += 1
            correct = selected == c.get("sibling_target")
            if triggered:
                sibling_confused += 1
                verdict = "混淆(FP)"
                fp += 1
            else:
                verdict = "OK" if correct else f"未中兄弟({selected})"
                tn += 1
        rows.append(f"| {r['case_id']}#r{r.get('run', 1)} | {exp} | {selected} | {verdict} |")

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    confusion = sibling_confused / sibling_total if sibling_total else 0.0

    report = (f"# 触发评测判分 — {target}\n\n"
              f"- runs: {len(results)}（TP {tp} / FP {fp} / FN {fn} / TN {tn}）\n"
              f"- precision {precision:.3f} / recall {recall:.3f} / **F1 {f1:.3f}**\n"
              f"- 兄弟混淆率: {confusion:.3f}（{sibling_confused}/{sibling_total}）\n\n"
              + "\n".join(rows)
              + "\n\n> 本报告只给原始配对计数与比率；统计非劣需预注册界值 + McNemar/配对 Bootstrap（§10.3），不在此自动宣布。\n")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(report)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="mode", required=True)
    s = sub.add_parser("split")
    s.add_argument("suite")
    p = sub.add_parser("prepare")
    p.add_argument("suite")
    p.add_argument("--skills", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--set", dest="which", choices=["train", "validation", "all"], default="train")
    c = sub.add_parser("score")
    c.add_argument("suite")
    c.add_argument("--results", required=True)
    c.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.mode == "split":
        return cmd_split(Path(args.suite))
    if args.mode == "prepare":
        return cmd_prepare(Path(args.suite), args.skills.split(","), Path(args.out), args.which)
    return cmd_score(Path(args.suite), Path(args.results), Path(args.out))


if __name__ == "__main__":
    raise SystemExit(main())
