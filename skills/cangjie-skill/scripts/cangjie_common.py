#!/usr/bin/env python3
"""cangjie_common.py — 仓颉确定性脚本的共享工具（路线 C：纯本地、不调模型）。

提供：frontmatter 解析、哈希、确定性缓存键、per-run workdir、writer lock、
staging + 原子发布、发布哈希登记与本地手改检测（方案 §4.4/§4.6.3/§13A 非功能矩阵）。
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import uuid
from pathlib import Path

import yaml

TOOL_VERSION = "cangjie-tools v2.5.0"


# ---------- 基础 IO ----------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: 期望 YAML mapping")
    return data


def dump_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


# ---------- frontmatter ----------

def split_frontmatter(text: str) -> tuple[dict, str]:
    """返回 (frontmatter dict, body)。无 frontmatter 时返回 ({}, 原文)。"""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = yaml.safe_load(text[3:end])
            if isinstance(fm, dict):
                return fm, text[end + 4 :].lstrip("\n")
    return {}, text


# ---------- 确定性缓存（方案 §4.4 A 类） ----------

def deterministic_cache_key(stage_name: str, implementation_version: str, stage_schema_version: str,
                            ordered_input_hashes: list[str], normalized_parameters: dict) -> str:
    payload = "\n".join([
        stage_name,
        implementation_version,
        stage_schema_version,
        *ordered_input_hashes,
        json.dumps(normalized_parameters, ensure_ascii=False, sort_keys=True),
    ])
    return sha256_text(payload)


def cache_lookup(cache_root: Path, stage: str, key: str) -> Path | None:
    p = cache_root / stage / key
    return p if p.is_dir() else None


def cache_store(cache_root: Path, stage: str, key: str, files: dict[str, bytes]) -> Path:
    """临时目录写入后原子 rename，避免半写缓存。"""
    final = cache_root / stage / key
    if final.exists():
        return final
    tmp = cache_root / stage / f".tmp-{key}-{uuid.uuid4().hex[:8]}"
    tmp.mkdir(parents=True)
    for rel, data in files.items():
        f = tmp / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
    try:
        tmp.rename(final)
    except OSError:
        shutil.rmtree(tmp, ignore_errors=True)  # 并发下另一个 writer 已完成
    return final


# ---------- run workdir / writer lock（方案 §15.17） ----------

def new_run_id() -> str:
    return time.strftime("run-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]


def create_run_workdir(sidecar: Path, run_id: str | None = None) -> Path:
    run_id = run_id or new_run_id()
    workdir = sidecar / "runs" / run_id
    workdir.mkdir(parents=True, exist_ok=False)
    return workdir


class WriterLock:
    """同一目标 pack 同时只允许一个 writer。O_EXCL 创建锁文件，崩溃后可依据 pid/时间人工清理。"""

    def __init__(self, target: Path):
        self.lock_path = target.with_name(target.name + ".cangjie-lock")

    def __enter__(self):
        try:
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise SystemExit(
                f"目标已被另一个 writer 锁定: {self.lock_path}\n"
                f"若确认无并发运行，删除该锁文件后重试。"
            )
        os.write(fd, f"pid={os.getpid()} time={time.strftime('%F %T')}\n".encode())
        os.close(fd)
        return self

    def __exit__(self, *exc):
        self.lock_path.unlink(missing_ok=True)
        return False


# ---------- staging + 原子发布 + 手改检测（方案 §4.6.3/§6.5） ----------

MANIFEST_NAME = "BUILD_MANIFEST.json"


def collect_published_hashes(out_dir: Path) -> dict[str, str]:
    return {
        str(p.relative_to(out_dir)): sha256_file(p)
        for p in sorted(out_dir.rglob("*"))
        if p.is_file() and p.name != MANIFEST_NAME
    }


def detect_local_edits(target: Path) -> list[str]:
    """比对目标目录当前文件与 BUILD_MANIFEST 发布哈希，返回被手工修改/删除的文件列表。"""
    manifest_path = target / MANIFEST_NAME
    if not manifest_path.exists():
        return []
    published = load_json(manifest_path).get("published_hashes", {})
    edited = []
    for rel, digest in published.items():
        f = target / rel
        if not f.exists():
            edited.append(f"{rel} (已删除)")
        elif sha256_file(f) != digest:
            edited.append(rel)
    return edited


def atomic_publish(staging: Path, target: Path, manifest_extra: dict, *, allow_overwrite_edits: bool = False) -> None:
    """staging 校验通过后原子替换发布目录。检测到本地手改且未显式允许时中止（三选一保护）。"""
    edits = detect_local_edits(target)
    if edits and not allow_overwrite_edits:
        raise SystemExit(
            "检测到已发布目录中的本地手工修改，拒绝静默覆盖：\n  - "
            + "\n  - ".join(edits)
            + "\n请三选一：\n  1) --force-overwrite 丢弃本地修改\n  2) 把修改回填 Capability Bundle 后重编译\n  3) 中止（当前行为）"
        )
    manifest = {
        "tool": TOOL_VERSION,
        "published_hashes": collect_published_hashes(staging),
        "note": "update/重编译前比对 published_hashes；检测到本地手改不得静默覆盖",
        **manifest_extra,
    }
    dump_json(staging / MANIFEST_NAME, manifest)
    backup = None
    if target.exists():
        backup = target.with_name(target.name + f".prev-{uuid.uuid4().hex[:6]}")
        target.rename(backup)
    try:
        staging.rename(target)
    except OSError:
        if backup is not None:
            backup.rename(target)  # 发布失败，恢复旧版本
        raise
    if backup is not None:
        shutil.rmtree(backup)


def snapshot_dir(src: Path, snapshots_root: Path, label: str) -> Path:
    """发布前快照，供 rollback 使用（RPO=0）。"""
    dest = snapshots_root / f"{time.strftime('%Y%m%d-%H%M%S')}-{label}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest)
    return dest
