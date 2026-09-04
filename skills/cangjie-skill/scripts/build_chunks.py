#!/usr/bin/env python3
"""build_chunks.py — 原生 Markdown/TXT → SourceDocument + 结构感知块（Phase 2A，纯确定性）。

产出（写入 <sidecar>/，默认 books/<slug>/.cangjie/）：
  normalized/<source-id>/<version-id>/document.json   # SourceDocument（contracts/source-document.schema.json）
  chunks/chunks.jsonl                                  # 结构感知块（contracts/chunk.schema.json）

块规则：尊重标题层级边界；单块目标 <= --max-chars（默认 4000 字符），超长段落按段切分；
每块保留 heading_path 与 element_ids，可回溯到原文。重复运行命中确定性缓存时跳过重算。

用法: python3 scripts/build_chunks.py <source.md> --sidecar <dir> [--source-id src-main-book] [--max-chars 4000]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cangjie_common import (  # noqa: E402
    cache_lookup,
    cache_store,
    deterministic_cache_key,
    dump_json,
    sha256_text,
)

IMPL_VERSION = "build_chunks v1.0"
SCHEMA_VERSION = "source-document@1/chunk@1"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
WORD_RE = re.compile(r"[\u4e00-\u9fff]|[A-Za-z0-9]+")


def parse_elements(text: str) -> list[dict]:
    """把 Markdown/TXT 解析为 SourceDocument elements（标题/段落/列表/代码）。"""
    elements: list[dict] = []
    heading_stack: list[tuple[int, str]] = []
    in_code = False
    buf: list[str] = []
    buf_type = "paragraph"

    def flush():
        nonlocal buf, buf_type
        content = "\n".join(buf).strip()
        buf = []
        if not content:
            return
        elements.append({
            "element_id": f"el-{len(elements):06d}",
            "type": buf_type,
            "text": content,
            "heading_path": [h for _, h in heading_stack],
            "page": None,
            "time_start_ms": None,
            "time_end_ms": None,
            "bbox": None,
            "asset_ref": None,
            "confidence": None,
            "content_hash": f"sha256:{sha256_text(content)}",
        })

    for line in text.splitlines():
        if line.strip().startswith("```"):
            if in_code:
                buf.append(line)
                flush()
                buf_type = "paragraph"
                in_code = False
            else:
                flush()
                buf_type = "code"
                buf.append(line)
                in_code = True
            continue
        if in_code:
            buf.append(line)
            continue
        m = HEADING_RE.match(line)
        if m:
            flush()
            level, title = len(m.group(1)), m.group(2).strip()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))
            buf_type = "heading"
            buf = [title]
            flush()
            buf_type = "paragraph"
            continue
        if not line.strip():
            flush()
            buf_type = "paragraph"
            continue
        if re.match(r"^\s*([-*+]|\d+\.)\s", line) and buf_type != "list":
            flush()
            buf_type = "list"
        buf.append(line)
    flush()
    return elements


def extract_keywords(text: str, limit: int = 12) -> list[str]:
    """确定性关键词预筛：词频最高的中文单字组成的双字串 + 英文词。够 FTS5 使用即可。"""
    freq: dict[str, int] = {}
    for m in re.finditer(r"[\u4e00-\u9fff]{2,6}|[A-Za-z][A-Za-z0-9-]{2,}", text):
        w = m.group(0).lower()
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]]


def group_chunks(elements: list[dict], source_id: str, version_id: str, max_chars: int) -> list[dict]:
    chunks: list[dict] = []
    cur: list[dict] = []
    cur_path: list[str] = []

    def flush():
        nonlocal cur
        if not cur:
            return
        text = "\n\n".join(e["text"] for e in cur)
        chunks.append({
            "chunk_id": f"ck-{sha256_text(version_id + text)[:12]}",
            "source_id": source_id,
            "version_id": version_id,
            "heading_path": cur[0]["heading_path"],
            "element_ids": [e["element_id"] for e in cur],
            "text": text,
            "char_count": len(text),
            "keywords": extract_keywords(text),
            "content_hash": f"sha256:{sha256_text(text)}",
        })
        cur = []

    for el in elements:
        # 标题边界或超长时开新块
        if el["type"] == "heading" and cur:
            flush()
        if cur and sum(len(e["text"]) for e in cur) + len(el["text"]) > max_chars:
            flush()
        if el["heading_path"] != cur_path:
            cur_path = el["heading_path"]
        cur.append(el)
    flush()
    return chunks


def build(source_path: Path, sidecar: Path, source_id: str, max_chars: int) -> dict:
    raw = source_path.read_text(encoding="utf-8")
    normalized = raw.replace("\r\n", "\n").strip() + "\n"
    version_id = f"sha256:{sha256_text(normalized)}"

    cache_root = sidecar / "cache"
    key = deterministic_cache_key("build_chunks", IMPL_VERSION, SCHEMA_VERSION,
                                  [version_id], {"max_chars": max_chars, "source_id": source_id})
    cached = cache_lookup(cache_root, "build_chunks", key)
    if cached:
        doc = json.loads((cached / "document.json").read_text(encoding="utf-8"))
        chunk_lines = (cached / "chunks.jsonl").read_text(encoding="utf-8")
        print(f"[cache-hit] build_chunks {key[:12]}")
    else:
        elements = parse_elements(normalized)
        doc = {
            "schema_version": 1,
            "source_id": source_id,
            "version_id": version_id,
            "title": source_path.stem,
            "media_type": "markdown" if source_path.suffix.lower() in (".md", ".markdown") else "txt",
            "language": ["zh-CN"],
            "parser": IMPL_VERSION,
            "elements": elements,
        }
        chunks = group_chunks(elements, source_id, version_id, max_chars)
        chunk_lines = "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in chunks)
        cache_store(cache_root, "build_chunks", key, {
            "document.json": json.dumps(doc, ensure_ascii=False, indent=1).encode("utf-8"),
            "chunks.jsonl": chunk_lines.encode("utf-8"),
        })

    out_doc = sidecar / "normalized" / source_id / version_id.removeprefix("sha256:")[:16] / "document.json"
    dump_json(out_doc, doc)
    chunks_path = sidecar / "chunks" / "chunks.jsonl"
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    chunks_path.write_text(chunk_lines, encoding="utf-8")

    n_chunks = chunk_lines.count("\n")
    print(f"SourceDocument: {out_doc}\nchunks: {chunks_path}（{len(doc['elements'])} elements → {n_chunks} chunks）")
    return {"version_id": version_id, "elements": len(doc["elements"]), "chunks": n_chunks}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source")
    ap.add_argument("--sidecar", required=True, help="侧车目录，如 books/<slug>/.cangjie")
    ap.add_argument("--source-id", default="src-main-book")
    ap.add_argument("--max-chars", type=int, default=4000)
    args = ap.parse_args()
    build(Path(args.source), Path(args.sidecar), args.source_id, args.max_chars)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
