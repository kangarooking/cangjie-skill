#!/usr/bin/env python3
"""validate_skill_pack.py — 纯确定性 Skill 包静态校验（Phase 0 工具，不调用模型）。

校验内容：
1. 每个含 SKILL.md 的目录视为一个 Skill：frontmatter 必须可解析且含非空 name/description；
2. name 建议匹配 ^[a-z0-9][a-z0-9-]*$ 且与目录名一致（不一致仅告警）；
3. 全部 .md 文件必须是合法 UTF-8；
4. 全部 .md 文件中的相对引用（markdown 链接与裸 references/... 路径）必须存在；
5. 输出每个 Skill 的行数/字节数概览。

用法: python3 scripts/validate_skill_pack.py <dir> [<dir> ...]
退出码: 0 = 无 ERROR；1 = 存在 ERROR。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

MD_LINK_RE = re.compile(r"\]\(([^)#\s]+?)(?:#[^)\s]*)?\)")
BARE_REF_RE = re.compile(r"(?<![\w/(])((?:references|assets)/[\w\-./]+\.[a-zA-Z0-9]+)")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

errors: list[str] = []
warnings: list[str] = []


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def check_links(md_path: Path, text: str) -> None:
    base = md_path.parent
    seen: set[str] = set()
    for regex in (MD_LINK_RE, BARE_REF_RE):
        for m in regex.finditer(text):
            target = m.group(1).strip()
            if target in seen:
                continue
            seen.add(target)
            if target.startswith(("http://", "https://", "mailto:", "/")):
                continue
            if not (base / target).exists():
                errors.append(f"[broken-ref] {md_path}: `{target}` 不存在")


def check_skill(skill_md: Path) -> None:
    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append(f"[frontmatter] {skill_md}: frontmatter 缺失或不可解析")
        return
    name = fm.get("name")
    desc = fm.get("description")
    if not (isinstance(name, str) and name.strip()):
        errors.append(f"[frontmatter] {skill_md}: 缺少非空 name")
    else:
        if not NAME_RE.match(name):
            warnings.append(f"[name-style] {skill_md}: name `{name}` 不符合小写连字符风格")
        if name != skill_md.parent.name:
            warnings.append(f"[name-dir] {skill_md}: name `{name}` 与目录名 `{skill_md.parent.name}` 不一致")
    if not (isinstance(desc, str) and desc.strip()):
        errors.append(f"[frontmatter] {skill_md}: 缺少非空 description")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    skill_count = 0
    md_count = 0
    for root_arg in argv[1:]:
        root = Path(root_arg)
        if not root.is_dir():
            errors.append(f"[input] 目录不存在: {root}")
            continue
        for md in sorted(root.rglob("*.md")):
            md_count += 1
            try:
                text = md.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(f"[encoding] {md}: 非法 UTF-8")
                continue
            check_links(md, text)
            if md.name == "SKILL.md":
                skill_count += 1
                check_skill(md)
                lines = text.count("\n") + 1
                print(f"  skill: {md.parent.name:<28} {lines:>4} 行 {len(text.encode('utf-8')):>7} 字节")

    print(f"\n共扫描 {md_count} 个 .md，其中 {skill_count} 个 SKILL.md")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n结果: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
