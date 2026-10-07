#!/usr/bin/env python3
"""count_tokens.py — A 类静态 Token 指标计算（Phase 0 工具，纯确定性，不调用模型）。

对三种版本形态计算：
- discovery_payload: 全部入口 SKILL.md 的 frontmatter name+description token 数之和（常驻发现目录成本）；
- per_task_payload: 单任务静态加载模型（见各 type 的定义，输出 min/median/max）；
- corpus_total: 版本目录内全部 .md 的 token 总量。

加载模型（静态假设，写死并随结果一起输出）：
- atomic_pack: 命中 1 个 Skill = 该 Skill 完整 SKILL.md；
- single:      任务 = 入口 SKILL.md + 1 张能力卡；upper = 入口 + 最大卡 + capability-index.md；
- compact_pack: 晋级命中 = 晋级 Skill 完整 SKILL.md；路由命中 = 路由入口 SKILL.md + 1 张能力卡。

用法: python3 scripts/count_tokens.py <config.json> [--out <dir>]
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

import tiktoken
import yaml

ENCODINGS = {}


def tok(text: str, enc_name: str) -> int:
    if enc_name not in ENCODINGS:
        ENCODINGS[enc_name] = tiktoken.get_encoding(enc_name)
    return len(ENCODINGS[enc_name].encode(text))


def frontmatter_name_desc(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    fm = yaml.safe_load(text[3:end])
    if not isinstance(fm, dict):
        return ""
    return f"{fm.get('name', '')}\n{fm.get('description', '')}"


def file_tokens(path: Path, enc: str) -> int:
    return tok(path.read_text(encoding="utf-8"), enc)


def stats(values: list[int]) -> dict:
    return {
        "min": min(values),
        "median": int(statistics.median(values)),
        "max": max(values),
        "n": len(values),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def measure_version(name: str, spec: dict, enc: str) -> dict:
    root = Path(spec["root"])
    vtype = spec["type"]
    result: dict = {"type": vtype, "root": str(root)}

    if vtype == "atomic_pack":
        entries = sorted(root.glob(spec.get("entry_glob", "*/SKILL.md")))
        result["entrypoint_count"] = len(entries)
        result["discovery_payload"] = sum(tok(frontmatter_name_desc(p), enc) for p in entries)
        result["per_task_payload"] = stats([file_tokens(p, enc) for p in entries])
        skill_dirs_md = [m for p in entries for m in p.parent.rglob("*.md")]
        result["corpus_installable"] = sum(file_tokens(m, enc) for m in skill_dirs_md)
        result["corpus_total"] = sum(file_tokens(m, enc) for m in sorted(root.rglob("*.md")))

    elif vtype == "single":
        entry = root / "SKILL.md"
        cards = sorted((root / "references" / "capabilities").glob("*.md"))
        entry_tok = file_tokens(entry, enc)
        card_toks = [file_tokens(c, enc) for c in cards]
        index_tok = file_tokens(root / "references" / "capability-index.md", enc)
        result["entrypoint_count"] = 1
        result["capability_count"] = len(cards)
        result["discovery_payload"] = tok(frontmatter_name_desc(entry), enc)
        result["entry_tokens"] = entry_tok
        result["per_task_payload"] = stats([entry_tok + c for c in card_toks])
        result["per_task_upper_bound"] = entry_tok + max(card_toks) + index_tok
        result["corpus_total"] = sum(file_tokens(m, enc) for m in sorted(root.rglob("*.md")))

    elif vtype == "compact_pack":
        router_root = root / spec["router"]
        router_entry = router_root / "SKILL.md"
        promoted = sorted(p for p in root.glob(spec.get("promoted_glob", "*/SKILL.md")) if p != router_entry)
        cards = sorted((router_root / "references" / "capabilities").glob("*.md"))
        router_tok = file_tokens(router_entry, enc)
        card_toks = [file_tokens(c, enc) for c in cards]
        promoted_toks = [file_tokens(p, enc) for p in promoted]
        entries = [router_entry, *promoted]
        result["entrypoint_count"] = len(entries)
        result["capability_count"] = len(cards)
        result["promoted_count"] = len(promoted)
        result["discovery_payload"] = sum(tok(frontmatter_name_desc(p), enc) for p in entries)
        result["per_task_payload_promoted_hit"] = stats(promoted_toks)
        result["per_task_payload_router_hit"] = stats([router_tok + c for c in card_toks])
        result["corpus_total"] = sum(file_tokens(m, enc) for m in sorted(root.rglob("*.md")))
    else:
        raise ValueError(f"未知版本类型: {vtype}")

    return result


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    cfg_path = Path(argv[1])
    out_dir = Path(argv[argv.index("--out") + 1]) if "--out" in argv else cfg_path.parent / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    report = {
        "tool": "count_tokens.py v0.1",
        "config": str(cfg_path),
        "config_sha256_16": sha256(cfg_path),
        "load_model_note": "见脚本 docstring；全部为静态假设，不代表任何宿主实际计费",
        "results": {},
    }
    for enc in cfg["tokenizers"]:
        report["results"][enc] = {
            vname: measure_version(vname, vspec, enc) for vname, vspec in cfg["versions"].items()
        }

    json_path = out_dir / "a-class-metrics.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# A 类静态 Token 指标\n", f"- 工具: {report['tool']}  配置: `{cfg_path}` (sha256:{report['config_sha256_16']})", "- 静态加载模型见 `scripts/count_tokens.py` docstring；不代表宿主实际计费。\n"]
    for enc, versions in report["results"].items():
        lines.append(f"## tokenizer = `{enc}`\n")
        lines.append("| 版本 | 入口数 | 发现负载(常驻) | 单任务负载 min/median/max | 语料总量 |")
        lines.append("|---|---|---|---|---|")
        for vname, r in versions.items():
            if r["type"] == "compact_pack":
                pt = r["per_task_payload_router_hit"]
                extra = r["per_task_payload_promoted_hit"]
                payload = f"路由 {pt['min']}/{pt['median']}/{pt['max']}；晋级 {extra['min']}/{extra['median']}/{extra['max']}"
            else:
                pt = r["per_task_payload"]
                payload = f"{pt['min']}/{pt['median']}/{pt['max']}"
            lines.append(f"| {vname} | {r['entrypoint_count']} | {r['discovery_payload']} | {payload} | {r['corpus_total']} |")
        lines.append("")
    md_path = out_dir / "a-class-metrics.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"已写出 {json_path} 与 {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
