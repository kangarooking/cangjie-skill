#!/usr/bin/env python3
"""apply_skill_patch.py — 最小补丁事务：快照 → 覆盖补丁文件 → 校验 → 可回滚（Phase 2B/3）。

repair/update 的落盘环节。补丁是"文件覆盖层"（patch 目录里的文件按相对路径覆盖目标），
不做自由重写；应用前自动快照，校验失败自动回滚。

用法:
  python3 scripts/apply_skill_patch.py apply --target <skill-dir> --patch-dir <dir> --snapshots <dir>
  python3 scripts/apply_skill_patch.py restore --target <skill-dir> --snapshot <snapshot-dir>
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import WriterLock, snapshot_dir  # noqa: E402

SCRIPTS = Path(__file__).parent


def apply_patch(target: Path, patch_dir: Path, snapshots: Path) -> int:
    patch_files = [p for p in patch_dir.rglob("*") if p.is_file()]
    if not patch_files:
        raise SystemExit(f"补丁目录为空: {patch_dir}")

    with WriterLock(target):
        snap = snapshot_dir(target, snapshots, "pre-patch")
        print(f"已快照: {snap}")
        diff_lines = []
        for pf in patch_files:
            rel = pf.relative_to(patch_dir)
            dest = target / rel
            old = dest.read_text(encoding="utf-8") if dest.exists() else ""
            new = pf.read_text(encoding="utf-8")
            diff_lines.append(f"### {rel}: {'修改' if dest.exists() else '新增'}（{len(old)} → {len(new)} 字符）")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pf, dest)

        check = subprocess.run([sys.executable, str(SCRIPTS / "validate_skill_pack.py"), str(target)],
                               capture_output=True, text=True)
        if check.returncode != 0:
            shutil.rmtree(target)
            shutil.copytree(snap, target)
            print(check.stdout + check.stderr)
            raise SystemExit("[rollback] 补丁后校验失败，已自动恢复快照")

    print("\n".join(diff_lines))
    print(f"补丁已应用并通过校验（{len(patch_files)} 个文件）。回滚: apply_skill_patch.py restore --snapshot {snap}")
    return 0


def restore(target: Path, snapshot: Path) -> int:
    if not snapshot.is_dir():
        raise SystemExit(f"快照不存在: {snapshot}")
    with WriterLock(target):
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(snapshot, target)
    print(f"已恢复 {target} ← {snapshot}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="mode", required=True)
    a = sub.add_parser("apply")
    a.add_argument("--target", required=True)
    a.add_argument("--patch-dir", required=True)
    a.add_argument("--snapshots", required=True)
    r = sub.add_parser("restore")
    r.add_argument("--target", required=True)
    r.add_argument("--snapshot", required=True)
    args = ap.parse_args()
    if args.mode == "apply":
        return apply_patch(Path(args.target), Path(args.patch_dir), Path(args.snapshots))
    return restore(Path(args.target), Path(args.snapshot))


if __name__ == "__main__":
    raise SystemExit(main())
