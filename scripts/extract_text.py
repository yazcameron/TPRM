"""Extract text from intake materials (txt, md, html, json, docx, pdf)."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def extract_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paras: list[str] = []
    for para in root.iter(f"{WORD_NS}p"):
        texts = [t.text or "" for t in para.iter(f"{WORD_NS}t")]
        line = "".join(texts).strip()
        if line:
            paras.append(line)
    return "\n".join(paras)


def extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"Cannot extract PDF {path.name}: install pypdf, or paste extracted text."
            ) from exc
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n\n".join(pages).strip()


def extract_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".html", ".htm", ".csv"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, indent=2)
    if suffix == ".docx":
        return extract_docx(path)
    if suffix == ".pdf":
        return extract_pdf(path)
    return path.read_text(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract text from TPRM intake files")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, help="Directory to write .txt extracts")
    args = parser.parse_args(argv)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
    for src in args.files:
        if not src.exists():
            print(f"missing: {src}", flush=True)
            return 1
        text = extract_file(src)
        if args.out:
            dest = args.out / (src.stem + ".txt")
            dest.write_text(text, encoding="utf-8")
            print(dest)
        else:
            print(f"===== {src.name} =====")
            print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
