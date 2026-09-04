#!/usr/bin/env python3
"""repair_flow.py — `cangjie.py repair` 的编排逻辑（Phase 3，路线 C）。

repair 是可回滚事务（方案 §7.3）。CLI 做确定性部分：校验失败案例 → 快照 → 生成诊断任务。
语义诊断与最小补丁由 Agent 完成；补丁经 apply_skill_patch.py 落盘（自动校验 + 失败回滚），
回归经 run_trigger_evals.py / run_output_evals.py 判分。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import create_run_workdir, load_yaml, new_run_id, snapshot_dir  # noqa: E402

DIAGNOSIS_TABLE = """\
| 类别 | 典型现象 | 主要修改点 | 必跑测试 |
|---|---|---|---|
| activation_miss | 该触发但没触发 | description、A2 | trigger 正例、验证集 |
| false_activation | 不该触发却触发 | description、B、兄弟区分 | near-miss 负例、兄弟混淆 |
| knowledge_gap | 缺事实、案例或术语 | references、I、A1 | 来源事实断言 |
| execution_gap | 会讲道理但不会做 | E、脚本、输出契约 | output eval |
| boundary_gap | 在不适用场景硬套 | B、判停条件 | edge/negative eval |
| structure_gap | 步骤顺序错误或前置条件缺失 | E、checklist | 流程断言 |
| tool_gap | 每次临时写重复脚本或工具调用失败 | scripts、compatibility | 集成测试 |
| preprocessing_gap | 上游漏字、表格错、时间轴错 | parser/IR，不应修 Skill 文案 | 预处理 golden set |
| eval_gap | 测试本身错误或过拟合 | eval 标签/断言 | 独立复核 |"""

REQUIRED_CASE_FIELDS = ("prompt", "actual", "expected", "severity")


def run_repair(pack: Path, case_path: Path) -> int:
    case = load_yaml(case_path)
    fc = case.get("failure_case", {})
    missing = [f for f in REQUIRED_CASE_FIELDS if not str(fc.get(f, "")).strip()]
    if missing or not case.get("skill"):
        raise SystemExit(f"failure case 缺少必填字段: {['skill'] if not case.get('skill') else []} + {missing}\n"
                         f"（schema: schemas/failure-case.schema.json；宿主拿不到执行轨迹时 actual 填 unavailable）")
    if fc["severity"] not in ("critical", "major", "minor"):
        raise SystemExit(f"severity 必须是 critical|major|minor，当前 {fc['severity']!r}")

    sidecar = pack / ".cangjie"
    run_id = new_run_id()
    workdir = create_run_workdir(sidecar, run_id)

    # 1. 只读快照目标 skill（能找到已发布目录时）
    target_hint = ""
    for candidate in (pack / case["skill"], pack.parent / case["skill"]):
        if candidate.is_dir():
            snap = snapshot_dir(candidate, sidecar / "snapshots", f"pre-repair-{case['skill']}")
            target_hint = f"已快照目标 skill: `{snap}`"
            break
    else:
        target_hint = "（未在本仓找到已发布 skill 目录；修复对象可能是 Bundle 能力卡，快照 Bundle 后再动手）"

    task = f"""# repair 诊断任务（run: {run_id}）

## 失败案例（{fc['severity']}）

- **skill**: `{case['skill']}`
- **prompt**: {fc['prompt']}
- **actual**: {fc['actual']}
- **expected**: {fc['expected']}

{target_hint}

## 你（Agent）要做的事，按序执行

1. **复现**：用 prompt 复现失败；宿主没有执行 Trace 就明确记录 unavailable，不得推测补齐；
2. **诊断分类**（写回 failure-case 的 diagnosis 字段，类别必须取自下表）：

{DIAGNOSIS_TABLE}

3. **最小补丁**：只改诊断影响范围内的文件（能力卡/Bundle 字段），不自由重写。
   把补丁文件放入 `{workdir}/patch/`，用
   `python3 scripts/apply_skill_patch.py apply --target <skill-dir> --patch-dir {workdir}/patch --snapshots {sidecar}/snapshots` 落盘；
4. **防过拟合**（方案 §7.4）：不把失败案例专有名词原样塞进 description；每修一个正例至少补一个语义近邻负例；
5. **回归**：目标失败案例 + 该 skill 全部回归 + 相邻 skill 混淆回归（run_trigger_evals.py 判分，validation 集在选版前保持隐藏）；
6. 通过后写 changelog；任何一步失败用 restore 回滚快照。

> preprocessing_gap 不要修 Skill 文案，去修上游解析；eval_gap 去修测试并记录理由。
"""
    (workdir / "repair-task.md").write_text(task, encoding="utf-8")
    (workdir / "patch").mkdir()
    print(task)
    print(f"诊断任务已生成: {workdir / 'repair-task.md'}")
    return 0
