#!/usr/bin/env python3
"""select_output_strategy.py — auto 输出决策器（方案 §4.6.5，策略 single-first-v1）。

规则（首版）：
1. 用户明确目的（--purpose learning|reference|workflow|distribution）优先；
2. 未明确目的时：至少 3 个能力通过晋级门、且晋级门触发验证达到预注册阈值（TBD-after-baseline，
   基线前该分支不启用）→ 推荐 pack；
3. 其他情况一律推荐 single（single-first）。

输出可解释 decision report（output-decision.schema.json）。默认值只是推荐，不能取消用户显式选择。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import dump_json, load_yaml  # noqa: E402
from compile_single import active_capabilities, promoted_capabilities  # noqa: E402

POLICY = "single-first-v1"

PURPOSE_TO_MODE = {
    "learning": "single",
    "reference": "single",
    "workflow": "pack",
    "distribution": "pack",
}


def decide(bundle_dir: Path, requested: str, purpose: str | None, *, trigger_validation_ready: bool = False) -> dict:
    bundle = load_yaml(bundle_dir / "verified.yaml")
    caps = active_capabilities(bundle)
    promoted = promoted_capabilities(bundle)
    budget = int(bundle.get("promotion_budget", 8))

    reasons: list[str] = []
    if requested in ("single", "pack"):
        selected = requested
        reasons.append(f"用户显式选择 {requested}，auto 决策器不覆盖用户选择")
    elif purpose:
        selected = PURPOSE_TO_MODE[purpose]
        reasons.append(f"用户目的为 {purpose} → {selected}")
    elif len(promoted) >= 3 and trigger_validation_ready:
        selected = "pack"
        reasons.append(f"{len(promoted)} 个能力通过晋级门（>=3）且触发验证达到预注册阈值")
    else:
        selected = "single"
        if len(promoted) >= 3:
            reasons.append(
                f"{len(promoted)} 个能力通过晋级门，但触发验证阈值为 TBD-after-baseline 尚未启用；"
                "按 single-first 原则先推荐 single，拆分由使用证据驱动"
            )
        else:
            reasons.append(f"仅 {len(promoted)} 个能力通过晋级门（<3），不满足 pack 推荐条件")

    alternative = (
        f"compact pack（1 个来源路由入口 + {len(promoted)} 个晋级 Skill，共 {1 + len(promoted)} 个可发现入口）"
        if selected == "single"
        else f"single（1 个入口 + {len(caps)} 张内部能力卡）"
    )

    return {
        "schema_version": 1,
        "requested": requested,
        "selected": selected,
        "decision_policy": POLICY,
        "skill_budget": budget,
        "promoted_count": len(promoted),
        "capability_count": len(caps),
        "reasons": reasons,
        "alternative": alternative,
        "user_confirmed": requested != "auto",
        "preserve_strategy_on_update": True,
    }


def render_report(decision: dict, bundle_dir: Path) -> str:
    bundle = load_yaml(bundle_dir / "verified.yaml")
    return f"""# 输出策略决策报告

推荐：**{decision['selected']}**（requested: {decision['requested']}，策略 {decision['decision_policy']}）

理由：
{chr(10).join(f'- {r}' for r in decision['reasons'])}

产物：{'1 个 Skill + ' + str(decision['capability_count']) + ' 张内部能力卡 + 章节/术语/速查 references' if decision['selected'] == 'single' else f"1 个来源路由入口 + {decision['promoted_count']} 个晋级 Skill（共 {1 + decision['promoted_count']} 个可发现入口）"}
备选：{decision['alternative']}

> 来源：{bundle['book']['title']}（{decision['capability_count']} 个 active 能力，晋级预算 {decision['skill_budget']}）
> 请回答：按推荐 / 改成 single / 改成 pack。默认值只是推荐，不会取消你的显式选择。
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--requested", choices=["auto", "single", "pack"], default="auto")
    ap.add_argument("--purpose", choices=list(PURPOSE_TO_MODE), default=None)
    ap.add_argument("--out-json", default=None)
    args = ap.parse_args()

    decision = decide(Path(args.bundle), args.requested, args.purpose)
    print(render_report(decision, Path(args.bundle)))
    if args.out_json:
        dump_json(Path(args.out_json), decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
