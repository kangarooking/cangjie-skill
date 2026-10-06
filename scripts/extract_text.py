#!/usr/bin/env python3
"""extract_text.py — 文档 → 纯文本的确定性提取器（输入端备料，P1-2，不调模型、不联网）。

对应 ADR: docs/plans/2026-10-06-reference-layer-adr.md §6。作为阶段 1 的确定性备料:
把 PDF/EPUB/DOCX/TXT 转为干净 UTF-8 文本，并产出
机器可读的提取报告（后端、页数、字符数、扫描版判定与 OCR 指引）。

用法:
  python scripts/extract_text.py <input> [<input> ...] [--out DIR] [--no-page-marks]
  python scripts/extract_text.py --check

输出（默认 <input 同目录>/extract/）:
  <stem>-fulltext.txt          纯文本（UTF-8；PDF 每页带 [p.N] 页标记，--no-page-marks 关闭）
  <stem>-extract-report.json   提取报告

后端优先级:
  PDF : PyMuPDF(fitz) → pypdf → pdftotext（系统 PATH）；文本页字符数中位数低于阈值时
        判定 likely_scanned 并给出 ocrmypdf 指引（不自动 OCR）
  EPUB: 标准库 zipfile（container.xml → OPF spine 顺序逐 XHTML 提取）
  DOCX: python-docx → 标准库 zipfile+ElementTree 兜底
  TXT : UTF-8 → GB18030 编码尝试链，统一转 UTF-8
  MOBI/AZW3: 无后端，报错并给出 Calibre ebook-convert 转换指引

Windows 注意: python3 可能指向 WindowsApps 占位符，请用 `python`。
退出码: 0 = 全部成功；1 = 存在失败文件（其余照常产出）；2 = 用法错误。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")

SCAN_PAGE_CHARS = 50      # 单页字符数低于此视为疑似空白/扫描页
SCAN_RATIO = 0.6          # 疑似页占比超过此值 → likely_scanned

XML_TAGS = "{http://www.w3.org/XML/1998/namespace}lang"
BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "blockquote", "section", "br"}


# ---------- 通用工具 ----------

def norm_text(text: str) -> str:
    """统一换行与空白：保留段落结构，压掉行内多余空白与零宽字符。"""
    text = text.replace("\x00", "").replace("\u200b", "")
    lines = [re.sub(r"[ \t\u3000]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln != "" or True).strip() + "\n"


def page_mark(n: int, enabled: bool) -> str:
    return f"\n[p.{n}]\n" if enabled else "\n"


def write_outputs(out_dir: Path, stem: str, text: str, report: dict) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / f"{stem}-fulltext.txt"
    txt_path.write_text(text, encoding="utf-8")
    report["out_files"] = [str(txt_path)]
    rep_path = out_dir / f"{stem}-extract-report.json"
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["out_files"].append(str(rep_path))
    return report["out_files"]


def scanned_verdict(pages_chars: list[int] | None) -> tuple[bool, str]:
    """返回 (likely_scanned, 建议文本)。非 PDF 传 None。"""
    if not pages_chars:
        return False, ""
    suspect = sum(1 for c in pages_chars if c < SCAN_PAGE_CHARS)
    if suspect / len(pages_chars) >= SCAN_RATIO:
        return True, (
            "疑似扫描版 PDF（多数页无可提取文本层）。请先 OCR: "
            "pip install ocrmypdf 且安装 Tesseract（chi_sim 语言包）后运行 "
            "`ocrmypdf -l chi_sim --skip-text <in.pdf> <out.pdf>`，再重新提取。"
        )
    return False, ""


# ---------- PDF ----------

def extract_pdf(path: Path, page_marks_on: bool) -> tuple[str, dict]:
    pages: list[str] = []
    backend = None

    try:
        try:
            import pymupdf as fitz  # PyMuPDF 新版命名
        except ImportError:
            import fitz  # 旧版兼容

        backend = "pymupdf"
        with fitz.open(path) as doc:
            for page in doc:
                pages.append(page.get_text("text"))
    except ImportError:
        try:
            from pypdf import PdfReader

            backend = "pypdf"
            reader = PdfReader(str(path))
            for page in reader.pages:
                pages.append(page.extract_text() or "")
        except ImportError:
            pdftotext = shutil.which("pdftotext")
            if not pdftotext:
                raise RuntimeError(
                    "PDF 后端全缺：请 `pip install pymupdf`（推荐）或安装 poppler 的 pdftotext"
                )
            backend = "pdftotext"
            proc = subprocess.run(
                [pdftotext, "-enc", "UTF-8", str(path), "-"],
                capture_output=True, timeout=300,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"pdftotext 失败: {proc.stderr.decode('utf-8', 'ignore')[:200]}")
            pages = proc.stdout.decode("utf-8", "ignore").split("\x0c")

    pages_chars = [len(p.strip()) for p in pages]
    body = "\n".join(page_mark(i, page_marks_on) + p.strip() for i, p in enumerate(pages, 1) if p.strip())
    scanned, hint = scanned_verdict(pages_chars)
    report = {
        "format": "pdf", "backend": backend, "pages": len(pages),
        "chars": sum(pages_chars), "pages_chars_min": min(pages_chars) if pages_chars else 0,
        "likely_scanned": scanned,
        "warnings": ([hint] if scanned else []) + ([] if backend != "pypdf" else
                     ["pypdf 提取质量通常弱于 PyMuPDF，中文表格/公式建议 pip install pymupdf"]),
    }
    return norm_text(body), report


# ---------- EPUB ----------

class _HTMLText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def extract_epub(path: Path, page_marks_on: bool) -> tuple[str, dict]:
    with zipfile.ZipFile(path) as zf:
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        opf_path = next(e.attrib["full-path"] for e in container.iter()
                        if e.tag.endswith("rootfile"))
        opf_dir = opf_path.rsplit("/", 1)[0] if "/" in opf_path else ""
        opf = ET.fromstring(zf.read(opf_path))

        def _short(tag: str) -> str:
            return tag.rsplit("}", 1)[-1]

        manifest, spine = {}, []
        for e in opf.iter():
            if _short(e.tag) == "item":
                manifest[e.attrib["id"]] = (e.attrib.get("href", ""), e.attrib.get("media-type", ""))
            elif _short(e.tag) == "itemref":
                spine.append(e.attrib["idref"])

        chunks: list[str] = []
        n_docs = 0
        for idref in spine:
            href, mtype = manifest.get(idref, ("", ""))
            if not href or (mtype and "html" not in mtype):
                continue
            full = f"{opf_dir}/{href}" if opf_dir else href
            try:
                raw = zf.read(full).decode("utf-8", "ignore")
            except KeyError:
                continue
            parser = _HTMLText()
            parser.feed(raw)
            chunk = norm_text("".join(parser.parts))
            if chunk.strip():
                n_docs += 1
                chunks.append(page_mark(n_docs, page_marks_on) + chunk.strip())
    report = {
        "format": "epub", "backend": "zipfile+html.parser", "pages": n_docs,
        "chars": sum(len(c) for c in chunks), "likely_scanned": False,
        "warnings": (["spine 为空，未提取到任何文档"] if n_docs == 0 else []),
    }
    return norm_text("\n".join(chunks)), report


# ---------- DOCX ----------

def extract_docx(path: Path, page_marks_on: bool) -> tuple[str, dict]:
    backend = "python-docx"
    paras: list[str] = []
    try:
        import docx  # python-docx

        d = docx.Document(str(path))
        paras = [p.text for p in d.paragraphs]
    except ImportError:
        backend = "zipfile+ElementTree"
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        with zipfile.ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
            paras = ["".join(t.text or "" for t in p.iter(f"{ns}t")) for p in root.iter(f"{ns}p")]
    body = "\n".join(page_mark(i, False) + p.strip() for i, p in enumerate(paras, 1) if p.strip())
    report = {
        "format": "docx", "backend": backend, "pages": None,
        "chars": sum(len(p) for p in paras), "likely_scanned": False,
        "warnings": (["未提取到任何段落"] if not paras else []),
    }
    return norm_text(body), report


# ---------- TXT ----------

def extract_txt(path: Path, page_marks_on: bool) -> tuple[str, dict]:
    raw = path.read_bytes()
    warnings, encoding = [], None
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            text = raw.decode(enc)
            encoding = enc
            break
        except UnicodeDecodeError:
            continue
    if encoding is None:
        raise RuntimeError("无法识别文本编码（尝试过 utf-8/utf-8-sig/gb18030）")
    if encoding == "gb18030":
        warnings.append("源文件为 GBK/GB18030 编码，已转 UTF-8")
    report = {
        "format": "txt", "backend": f"decode:{encoding}", "pages": None,
        "chars": len(text), "likely_scanned": False, "warnings": warnings,
    }
    return norm_text(text), report


EXTRACTORS = {
    ".pdf": extract_pdf,
    ".epub": extract_epub,
    ".docx": extract_docx,
    ".txt": extract_txt,
    ".md": extract_txt,
}


# ---------- CLI ----------

def cmd_check() -> int:
    print("extract_text.py 依赖自检:")
    rows = [("fitz", "pymupdf", "PDF 首选后端"), ("pypdf", "pypdf", "PDF 备用后端"),
            ("docx", "python-docx", "DOCX 首选后端"), ("yaml", "pyyaml", "仓颉其他脚本需要")]
    ok_all = True
    for mod, pkg, why in rows:
        try:
            __import__(mod)
            print(f"  [ok]   {mod:12s} {why}")
        except ImportError:
            ok_all = ok_all and mod in ("pypdf", "docx")  # 二线后端缺省可容忍（fitz 缺才是问题）
            print(f"  [warn] {mod:12s} {why} → pip install {pkg}")
    for exe, why in (("pdftotext", "PDF 三线后端"), ("ocrmypdf", "扫描版 OCR（可选）"),
                     ("ebook-convert", "MOBI/AZW3 转换（可选）")):
        status = "ok" if shutil.which(exe) else "warn"
        print(f"  [{status:<4}] {exe:14s} {why}")
    print("check:", "PASS" if ok_all else "部分可用（至少需要 fitz/pypdf 之一 + docx/zipfile 之一）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="*", help="输入文件（PDF/EPUB/DOCX/TXT/MD）")
    ap.add_argument("--out", default=None, help="输出目录（默认 <input 同目录>/extract/）")
    ap.add_argument("--format", choices=["auto", *EXTRACTORS], default="auto")
    ap.add_argument("--no-page-marks", action="store_true", help="不写 [p.N] 页标记")
    ap.add_argument("--check", action="store_true", help="仅自检后端可用性")
    args = ap.parse_args()

    if args.check:
        return cmd_check()
    if not args.inputs:
        ap.print_help()
        return 2

    failed = 0
    for raw in args.inputs:
        path = Path(raw)
        report: dict = {"input": str(path)}
        try:
            if not path.is_file():
                raise RuntimeError(f"文件不存在: {path}")
            ext = f".{args.format}" if args.format != "auto" else path.suffix.lower()
            extractor = EXTRACTORS.get(ext)
            if extractor is None:
                if ext in (".mobi", ".azw3", ".azw"):
                    raise RuntimeError(
                        "MOBI/AZW3 无本地后端。请用 Calibre 转换后重试: "
                        "`ebook-convert <in.mobi> <out.epub>`"
                    )
                raise RuntimeError(f"不支持的格式: {ext}（支持 {', '.join(EXTRACTORS)}）")
            text, report = extractor(path, not args.no_page_marks)
            if not text.strip():
                raise RuntimeError("提取结果为空（可能整书无文本层，见扫描版指引）")
            out_dir = Path(args.out) if args.out else path.parent / "extract"
            outs = write_outputs(out_dir, path.stem, text, report)
            flag = " ⚠ likely_scanned" if report.get("likely_scanned") else ""
            print(f"[ok] {path.name}: {report['backend']}, {report['chars']} 字符{flag}")
            for w in report.get("warnings", []):
                print(f"     warn: {w}")
            print(f"     → {outs[0]}")
        except Exception as exc:  # 单文件失败不中断批量
            failed += 1
            report["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[FAIL] {path.name}: {report['error']}", file=sys.stderr)
            rep_dir = Path(args.out) if args.out else path.parent / "extract"
            try:
                (rep_dir / f"{path.stem}-extract-report.json").parent.mkdir(parents=True, exist_ok=True)
                (rep_dir / f"{path.stem}-extract-report.json").write_text(
                    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            except OSError:
                pass
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
