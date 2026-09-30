#!/usr/bin/env python3
"""cangjie.py — 仓颉统一薄 CLI（路线 C：只做编排与确定性操作，蒸馏仍由 Agent 完成）。

子命令：
  doctor          环境自检（无网络、无重依赖场景可通过核心检查）
  migrate-legacy  旧 one-to-one pack + 人工能力映射 → Capability Bundle（.cangjie/capabilities/）
  compile         Capability Bundle → single | compact pack（auto 决策 + 锁 + staging + 原子发布）
  replan-output   重新评估输出策略，只生成 side-by-side 预览，不迁移
  update          登记新来源 → diff → change-set → 影响分析 → 生成待处理 Agent 任务（不自动改 Skill）
  repair          校验失败案例 → 快照 → 生成诊断任务（语义修复由 Agent 完成后回归）
  rollback        恢复最近快照（--list 查看）
  eval            分发到触发评测（默认）或输出评测
  benchmark       分发到 benchmark.py

`compile` 的输入必须是已验证 Capability Bundle；本 CLI 不声称能从原始书籍一键蒸馏。
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import (  # noqa: E402
    TOOL_VERSION,
    WriterLock,
    atomic_publish,
    create_run_workdir,
    dump_json,
    load_yaml,
    new_run_id,
    sha256_file,
    snapshot_dir,
    split_frontmatter,
)

SCRIPTS = Path(__file__).parent


# ---------- doctor ----------

def cmd_doctor(_args) -> int:
    ok = True
    print(f"{TOOL_VERSION}\npython: {sys.version.split()[0]}")
    for mod, required in (("yaml", True), ("tiktoken", False), ("jsonschema", False)):
        try:
            __import__(mod)
            print(f"  [ok] {mod}")
        except ImportError:
            level = "缺失(必需)" if required else "缺失(可选)"
            print(f"  [{'FAIL' if required else 'warn'}] {mod} {level}")
            ok = ok and not required
    for rel in ("capability-bundle.schema.json", "registry-entry.schema.json", "contracts/source-document.schema.json"):
        p = SCRIPTS.parent / "schemas" / rel
        print(f"  [{'ok' if p.exists() else 'FAIL'}] schemas/{rel}")
        ok = ok and p.exists()
    print("doctor:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ---------- migrate-legacy ----------

ROUTER_GATE = {"independent_intent": False, "independent_contract": True, "independent_run": True,
               "independent_reuse": False, "independent_eval": True}
PROMOTED_GATE = {k: True for k in ROUTER_GATE}


def cmd_migrate_legacy(args) -> int:
    """人工能力映射 + 旧 pack → Capability Bundle。语义字段全部来自映射，不猜测。"""
    import yaml as _yaml

    m = load_yaml(Path(args.map))
    pack = Path(args.pack)
    bundle_dir = pack / ".cangjie" / "capabilities"
    (bundle_dir / "cards").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "book").mkdir(exist_ok=True)

    capabilities = []
    for cap in m["capabilities"]:
        src_md = pack / cap["slug"] / "SKILL.md"
        fm, body = split_frontmatter(src_md.read_text(encoding="utf-8"))
        dest = cap.get("pack_destination", "router")
        header = (
            f"<!-- capability_id: {cap['id']} | revision: 1 | status: active -->\n"
            f"<!-- 来源: {m['book']['source_pack']}/{cap['slug']}/SKILL.md（正文逐字保留） -->\n\n"
        )
        (bundle_dir / "cards" / f"{cap['slug']}.md").write_text(header + body, encoding="utf-8")
        capabilities.append({
            "capability_id": cap["id"],
            "revision": 1,
            "status": "active",
            "aliases": [],
            "supersedes": [],
            "merged_into": None,
            "split_into": [],
            "slug": cap["slug"],
            "title": cap["title"],
            "importance": cap["importance"],
            "importance_rationale": cap["importance_rationale"],
            "one_liner": cap["one_liner"],
            "intents": cap["intents"],
            "keywords": cap["keywords"],
            "also_read": cap.get("also_read", []),
            "card": f"cards/{cap['slug']}.md",
            "frontmatter": {"description": str(fm.get("description", "")).strip(),
                            "tags": fm.get("tags", [])},
            "source_evidence": [{"source_id": "src-main-book", "location": str(fm.get("source_chapter", ""))}],
            "promotion": {"destination": dest,
                          "gate": PROMOTED_GATE if dest == "promoted" else dict(ROUTER_GATE),
                          "notes": cap.get("promotion_notes", "")},
        })

    bundle = {
        "schema_version": 1,
        "bundle_id": f"bundle.{m['entry']['name']}",
        "book": m["book"],
        "entry": m["entry"],
        "router_entry": m["router_entry"],
        "promotion_budget": m.get("promotion_budget", 8),
        "capabilities": capabilities,
    }
    (bundle_dir / "verified.yaml").write_text(
        _yaml.safe_dump(bundle, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")

    dump_json(bundle_dir / "destinations.json", {
        "bundle_id": bundle["bundle_id"],
        "destinations": {c["capability_id"]: ({"promoted_to": c["slug"]} if c["promotion"]["destination"] == "promoted"
                                              else {"served_by": m["router_entry"]["name"]})
                         for c in capabilities},
    })

    for src_name, dst_name in (("BOOK_OVERVIEW.md", "overview.md"), ("GLOSSARY.md", "glossary.md")):
        src = pack / src_name
        if src.exists():
            shutil.copyfile(src, bundle_dir / "book" / dst_name)

    print(f"Capability Bundle 已生成: {bundle_dir}（{len(capabilities)} 个能力）")
    return 0


# ---------- compile ----------

def cmd_compile(args) -> int:
    from compile_pack import compile_pack_tree
    from compile_single import build_tree, write_tree
    from select_output_strategy import decide, render_report

    bundle_dir = Path(args.bundle)
    sidecar = bundle_dir.parent if bundle_dir.name == "capabilities" else bundle_dir
    run_id = new_run_id()
    workdir = create_run_workdir(sidecar, run_id)

    decision = decide(bundle_dir, args.output, args.purpose)
    dump_json(workdir / "output-decision.json", decision)
    (workdir / "output-decision.md").write_text(render_report(decision, bundle_dir), encoding="utf-8")
    print(render_report(decision, bundle_dir))
    if args.output == "auto" and not args.yes:
        print("auto 模式需要用户轻确认；确认后请加 --yes 重新运行（按推荐），或显式 --output single|pack。")
        return 2

    selected = decision["selected"]
    files = build_tree(bundle_dir, "single") if selected == "single" else compile_pack_tree(
        bundle_dir, allow_over_budget=args.allow_over_budget)

    target = Path(args.out)
    staging = target.parent / f".staging-{run_id}-{target.name}"
    if staging.exists():
        shutil.rmtree(staging)
    write_tree(files, staging)

    check = subprocess.run([sys.executable, str(SCRIPTS / "validate_skill_pack.py"), str(staging)],
                           capture_output=True, text=True)
    (workdir / "staging-validation.log").write_text(check.stdout + check.stderr, encoding="utf-8")
    if check.returncode != 0:
        print(check.stdout + check.stderr)
        raise SystemExit("[hard-gate] staging 校验未通过，已保留 staging 供排查，不发布")

    with WriterLock(target):
        if target.exists():
            snap = snapshot_dir(target, sidecar / "snapshots", f"pre-{run_id}")
            print(f"已快照旧版本: {snap}")
        atomic_publish(staging, target, {
            "bundle_id": load_yaml(bundle_dir / "verified.yaml")["bundle_id"],
            "bundle_sha256": sha256_file(bundle_dir / "verified.yaml"),
            "variant": selected,
            "run_id": run_id,
            "decision": decision,
        }, allow_overwrite_edits=args.force_overwrite)

    print(f"已原子发布 {selected} 产物到 {target}（run: {run_id}）")
    return 0


# ---------- replan-output ----------

def cmd_replan_output(args) -> int:
    from select_output_strategy import decide, render_report

    bundle_dir = Path(args.pack) / ".cangjie" / "capabilities"
    decision = decide(bundle_dir, "auto", args.purpose)
    print(render_report(decision, bundle_dir))
    print("（dry-run 预览：未做任何迁移；确认变更请显式运行 compile 并选择新的 --output）")
    return 0


# ---------- update / repair / rollback / eval / benchmark ----------

def cmd_update(args) -> int:
    from update_flow import run_update  # Phase 2B

    return run_update(Path(args.pack), Path(args.add))


def cmd_repair(args) -> int:
    from repair_flow import run_repair  # Phase 3

    return run_repair(Path(args.pack), Path(args.case))


def cmd_rollback(args) -> int:
    sidecar = Path(args.pack) / ".cangjie"
    snaps = sorted((sidecar / "snapshots").glob("*")) if (sidecar / "snapshots").exists() else []
    if args.list or not args.to:
        print("可用快照：" + ("\n  " + "\n  ".join(s.name for s in snaps) if snaps else " (无)"))
        return 0
    snap = sidecar / "snapshots" / args.to
    if not snap.is_dir():
        raise SystemExit(f"快照不存在: {snap}")
    target = Path(args.target)
    with WriterLock(target):
        if target.exists():
            snapshot_dir(target, sidecar / "snapshots", "pre-rollback")
            shutil.rmtree(target)
        shutil.copytree(snap, target)
    print(f"已回滚 {target} ← {snap.name}")
    return 0


def _dispatch(script: str, extra: list[str]) -> int:
    return subprocess.call([sys.executable, str(SCRIPTS / script), *extra])


def main() -> int:
    # 这两个命令需要把未知选项原样透传给子工具。argparse 的子解析器
    # 会在 `--token-config` 这类选项上提前报错，因此在根解析前直接分发。
    if len(sys.argv) > 1 and sys.argv[1] == "benchmark":
        return _dispatch("benchmark.py", sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "eval":
        extra = sys.argv[2:]
        script = "run_trigger_evals.py"
        if extra and extra[0] in {"trigger", "output"}:
            script = "run_output_evals.py" if extra[0] == "output" else script
            extra = extra[1:]
        return _dispatch(script, extra)

    ap = argparse.ArgumentParser(prog="cangjie", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor")

    p = sub.add_parser("migrate-legacy")
    p.add_argument("--map", required=True, help="人工能力映射 capability-map.yaml")
    p.add_argument("--pack", required=True, help="旧 one-to-one pack 目录")

    p = sub.add_parser("compile")
    p.add_argument("--bundle", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--output", choices=["auto", "single", "pack"], default="auto")
    p.add_argument("--purpose", choices=["learning", "reference", "workflow", "distribution"], default=None)
    p.add_argument("--yes", action="store_true", help="auto 模式下按推荐执行（轻确认）")
    p.add_argument("--allow-over-budget", action="store_true")
    p.add_argument("--force-overwrite", action="store_true", help="丢弃已发布目录中的本地手工修改")

    p = sub.add_parser("replan-output")
    p.add_argument("--pack", required=True)
    p.add_argument("--purpose", choices=["learning", "reference", "workflow", "distribution"], default=None)
    p.add_argument("--dry-run", action="store_true", default=True)

    p = sub.add_parser("update")
    p.add_argument("--pack", required=True)
    p.add_argument("--add", required=True, help="新增来源文件（Markdown/TXT）")

    p = sub.add_parser("repair")
    p.add_argument("--pack", required=True)
    p.add_argument("--case", required=True, help="failure-case YAML（failure-case.schema.json）")

    p = sub.add_parser("rollback")
    p.add_argument("--pack", required=True)
    p.add_argument("--target", help="要恢复的已发布目录")
    p.add_argument("--to", default=None)
    p.add_argument("--list", action="store_true")

    for name, script in (("eval", "run_trigger_evals.py"), ("benchmark", "benchmark.py")):
        p = sub.add_parser(name, add_help=False)
        p.add_argument("extra", nargs=argparse.REMAINDER)
        p.set_defaults(script=script)

    args = ap.parse_args()
    if args.cmd == "doctor":
        return cmd_doctor(args)
    if args.cmd == "migrate-legacy":
        return cmd_migrate_legacy(args)
    if args.cmd == "compile":
        return cmd_compile(args)
    if args.cmd == "replan-output":
        return cmd_replan_output(args)
    if args.cmd == "update":
        return cmd_update(args)
    if args.cmd == "repair":
        return cmd_repair(args)
    if args.cmd == "rollback":
        return cmd_rollback(args)
    return _dispatch(args.script, args.extra)


if __name__ == "__main__":
    raise SystemExit(main())
