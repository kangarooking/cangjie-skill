#!/usr/bin/env python3
"""benchmark.py — 聚合报告（Phase 3/4，路线 C）。

汇总一次迭代的全部可复算指标为 benchmark.json + benchmark.md：
- A 类静态 Token 指标（调用 count_tokens.py 的配置与产物）
- 触发/输出评测判分（run_trigger_evals / run_output_evals 的报告产物）
- 过程代理指标（runs/*/stage-usage.jsonl 若存在；标注为估算，非真实 token）

用法: python3 scripts/benchmark.py --token-config <token-config.json> [--eval-reports <dir>] [--sidecar <.cangjie>] --out <dir>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import TOOL_VERSION, dump_json, load_json  # noqa: E402

SCRIPTS = Path(__file__).parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--token-config", required=True)
    ap.add_argument("--eval-reports", default=None)
    ap.add_argument("--sidecar", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. A 类静态指标
    rc = subprocess.call([sys.executable, str(SCRIPTS / "count_tokens.py"), args.token_config, "--out", str(out_dir)])
    if rc != 0:
        raise SystemExit("count_tokens 失败")
    a_metrics = load_json(out_dir / "a-class-metrics.json")

    # 2. 评测报告
    eval_reports = []
    if args.eval_reports:
        for f in sorted(Path(args.eval_reports).glob("*.md")):
            eval_reports.append({"file": str(f), "title": f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ")})

    # 3. 过程代理指标（B 类）
    proxy = []
    if args.sidecar:
        for usage in sorted(Path(args.sidecar).glob("runs/*/stage-usage.jsonl")):
            rows = [json.loads(l) for l in usage.read_text(encoding="utf-8").splitlines() if l.strip()]
            proxy.append({
                "run": usage.parent.name,
                "tasks": len(rows),
                "prepared_input_chars": sum(r.get("prepared_input_chars", 0) for r in rows),
                "cache_hits": sum(1 for r in rows if r.get("reused_from_cache")),
                "retries": sum(r.get("retry_count", 0) for r in rows),
            })

    benchmark = {
        "tool": TOOL_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "a_class_metrics": a_metrics,
        "eval_reports": eval_reports,
        "process_proxy_metrics": proxy,
        "notes": [
            "A 类为固定 tokenizer 的文件计数与静态载荷模型，不代表宿主实际计费（§5.1）",
            "B 类为过程代理量（prepared_input），标注为估算，禁止改称真实 Prompt 输入",
            "路线 C 下不存在可信的 input/output/cached tokens，本报告不含这三项",
        ],
    }
    dump_json(out_dir / "benchmark.json", benchmark)

    lines = [f"# Benchmark 报告（{benchmark['generated_at']}）", "",
             f"- 工具: {TOOL_VERSION}",
             f"- A 类静态指标: `{out_dir / 'a-class-metrics.md'}`"]
    if eval_reports:
        lines.append("- 评测判分:")
        lines += [f"  - [{r['title']}]({r['file']})" for r in eval_reports]
    if proxy:
        lines.append("\n## 过程代理指标（估算，非真实 token）\n")
        lines.append("| run | 任务数 | prepared_input_chars | 缓存命中 | 重试 |")
        lines.append("|---|---|---|---|---|")
        lines += [f"| {p['run']} | {p['tasks']} | {p['prepared_input_chars']} | {p['cache_hits']} | {p['retries']} |"
                  for p in proxy]
    lines += ["", *(f"> {n}" for n in benchmark["notes"])]
    (out_dir / "benchmark.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"benchmark: {out_dir / 'benchmark.json'} / {out_dir / 'benchmark.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
