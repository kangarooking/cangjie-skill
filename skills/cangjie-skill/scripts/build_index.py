#!/usr/bin/env python3
"""build_index.py — chunks.jsonl → SQLite FTS5 词法索引（Phase 2A MVP，不引入向量库）。

建索引:  python3 scripts/build_index.py <chunks.jsonl> [--db <lexical.sqlite>]
查询:    python3 scripts/build_index.py <chunks.jsonl> --query "杠杆 复利" [--limit 5] [--neighbors 1]

查询返回命中块及其邻接块（防断章取义），供检索式 extractor（case/counter-example/glossary）取材。
中文按字符 bigram 分词（FTS5 unicode61 对 CJK 不分词，入库前预处理）。
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

CJK_RE = re.compile(r"[\u4e00-\u9fff]+")


def cjk_bigram(text: str) -> str:
    """把连续中文串展开为 bigram 词序列，使 FTS5 能做中文子串匹配。"""

    def expand(m: re.Match) -> str:
        s = m.group(0)
        if len(s) == 1:
            return s
        return " ".join(s[i : i + 2] for i in range(len(s) - 1))

    return CJK_RE.sub(expand, text)


def build(chunks_path: Path, db_path: Path) -> int:
    chunks = [json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.unlink(missing_ok=True)
    con = sqlite3.connect(db_path)
    con.execute("CREATE TABLE chunks (seq INTEGER PRIMARY KEY, chunk_id TEXT, heading_path TEXT, text TEXT, keywords TEXT)")
    con.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(chunk_id, heading_path, body, keywords)")
    for seq, c in enumerate(chunks):
        hp = " / ".join(c["heading_path"])
        con.execute("INSERT INTO chunks VALUES (?,?,?,?,?)",
                    (seq, c["chunk_id"], hp, c["text"], " ".join(c.get("keywords", []))))
        con.execute("INSERT INTO chunks_fts VALUES (?,?,?,?)",
                    (c["chunk_id"], cjk_bigram(hp), cjk_bigram(c["text"]), cjk_bigram(" ".join(c.get("keywords", [])))))
    con.commit()
    con.close()
    print(f"索引已建: {db_path}（{len(chunks)} chunks）")
    return 0


def query(db_path: Path, q: str, limit: int, neighbors: int) -> int:
    con = sqlite3.connect(db_path)
    terms = " OR ".join(f'"{t}"' for t in cjk_bigram(q).split())
    rows = con.execute(
        "SELECT chunk_id FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?", (terms, limit)
    ).fetchall()
    if not rows:
        print("（无命中；建议放宽查询词或回退全量扫描）")
        return 0
    seen: set[int] = set()
    for (chunk_id,) in rows:
        (seq,) = con.execute("SELECT seq FROM chunks WHERE chunk_id=?", (chunk_id,)).fetchone()
        for s in range(max(0, seq - neighbors), seq + neighbors + 1):
            seen.add(s)
    for seq in sorted(seen):
        row = con.execute("SELECT chunk_id, heading_path, text FROM chunks WHERE seq=?", (seq,)).fetchone()
        if row:
            cid, hp, text = row
            print(f"\n===== {cid} [{hp}] =====\n{text[:1500]}")
    con.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("chunks")
    ap.add_argument("--db", default=None)
    ap.add_argument("--query", default=None)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--neighbors", type=int, default=1)
    args = ap.parse_args()

    chunks_path = Path(args.chunks)
    db_path = Path(args.db) if args.db else chunks_path.parent.parent / "index" / "lexical.sqlite"
    if args.query:
        return query(db_path, args.query, args.limit, args.neighbors)
    return build(chunks_path, db_path)


if __name__ == "__main__":
    raise SystemExit(main())
