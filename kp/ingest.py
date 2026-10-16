"""Turn inputs/corpus into page-level text with printed folios, plus a manifest.

The manifest records every file: ok, duplicate (same bytes as an earlier file),
failed (with the reason) or unsupported. Nothing is dropped silently.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

SUPPORTED = {".pdf", ".docx", ".txt", ".md"}
_FOLIO = re.compile(r"^\s*(\d{1,3})\s*$", re.M)   # four digits is a year, not a page


class IngestError(Exception):
    pass


def printed_folio(page_text: str) -> int | None:
    """The page number printed on the page (outermost standalone number), if any."""
    hits = _FOLIO.findall(page_text or "")
    return int(hits[-1]) if hits else None


def doc_id_for(rel: Path) -> str:
    parts = Path(rel).with_suffix("").parts
    return "__".join(re.sub(r"[^a-z0-9]+", "-", part.casefold()).strip("-") for part in parts)


def page_label(page: dict) -> str:
    return str(page["printed_page"]) if page.get("printed_page") is not None else f"pdf:{page['pdf_page']}"


def pages_for(pages: list[dict], label: str) -> list[int]:
    label = str(label).strip()
    if label.startswith("pdf:"):
        n = int(label[4:])
        return [i for i, p in enumerate(pages) if p["pdf_page"] == n]
    n = int(label)
    return [i for i, p in enumerate(pages) if p["printed_page"] == n]


def extract_pages(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        import pymupdf
        with pymupdf.open(str(path)) as doc:
            out = []
            for i, page in enumerate(doc):
                text = page.get_text()
                out.append({"pdf_page": i + 1, "printed_page": printed_folio(text), "text": text})
            return out
    if suffix == ".docx":
        from docx import Document
        text = "\n".join(p.text for p in Document(str(path)).paragraphs)
        return [{"pdf_page": 1, "printed_page": None, "text": text}]
    return [{"pdf_page": 1, "printed_page": None, "text": path.read_text(encoding="utf-8", errors="replace")}]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_path(cfg) -> Path:
    return cfg.index_dir / "manifest.json"


def load_manifest(cfg) -> dict:
    path = _manifest_path(cfg)
    if not path.is_file():
        raise IngestError("the corpus has not been ingested: run `python -m kp ingest`")
    return json.loads(path.read_text(encoding="utf-8"))


def load_pages(cfg, doc_id: str) -> list[dict]:
    path = cfg.index_dir / "text" / f"{doc_id}.json"
    if not path.is_file():
        raise IngestError(f"unknown document {doc_id!r}: not in the ingested corpus")
    return json.loads(path.read_text(encoding="utf-8"))["pages"]


def _candidates(corpus: Path):
    for path in sorted(corpus.rglob("*")):
        if not path.is_file() or path.name.startswith(("~$", ".")) or path.name.lower() == "readme.md":
            continue
        yield path


def ingest(cfg) -> dict:
    if not cfg.corpus.is_dir():
        raise IngestError(f"no corpus folder at {cfg.corpus}: run `python -m kp init`")
    text_dir = cfg.index_dir / "text"
    text_dir.mkdir(parents=True, exist_ok=True)
    previous = {}
    if _manifest_path(cfg).is_file():
        previous = {d["doc_id"]: d for d in load_manifest(cfg)["documents"]}
    seen: dict[str, str] = {}
    docs, counts = [], {"ok": 0, "duplicate": 0, "failed": 0, "unchanged": 0, "unsupported": 0}
    for path in _candidates(cfg.corpus):
        rel = path.relative_to(cfg.corpus)
        entry = {"doc_id": doc_id_for(rel), "path": rel.as_posix(),
                 "collection": rel.parts[0] if len(rel.parts) > 1 else "default",
                 "sha256": None, "pages": 0, "status": "ok", "duplicate_of": None, "error": None}
        if path.suffix.lower() not in SUPPORTED:
            entry["status"] = "unsupported"
            entry["error"] = f"file type {path.suffix or '(none)'} is not supported"
            counts["unsupported"] += 1
            docs.append(entry)
            continue
        sha = _sha256(path)
        entry["sha256"] = sha
        if sha in seen:
            entry["status"], entry["duplicate_of"] = "duplicate", seen[sha]
            counts["duplicate"] += 1
            docs.append(entry)
            continue
        seen[sha] = entry["doc_id"]
        out = text_dir / f"{entry['doc_id']}.json"
        prev = previous.get(entry["doc_id"])
        if prev and prev["sha256"] == sha and prev["status"] == "ok" and out.is_file():
            entry["pages"] = prev["pages"]
            counts["unchanged"] += 1
            docs.append(entry)
            continue
        try:
            pages = extract_pages(path)
        except Exception as exc:  # any unreadable file is reported, never fatal
            entry["status"], entry["error"] = "failed", f"{type(exc).__name__}: {exc}"
            counts["failed"] += 1
            docs.append(entry)
            continue
        if not any(p["text"].strip() for p in pages):
            entry["status"] = "failed"
            entry["error"] = "no extractable text (scanned document? OCR is not supported)"
            counts["failed"] += 1
            docs.append(entry)
            continue
        out.write_text(json.dumps({"doc_id": entry["doc_id"], "pages": pages}, ensure_ascii=False),
                       encoding="utf-8")
        entry["pages"] = len(pages)
        counts["ok"] += 1
        docs.append(entry)
    keep = {d["doc_id"] for d in docs if d["status"] == "ok"}
    for stale in text_dir.glob("*.json"):
        if stale.stem not in keep:
            stale.unlink()
    manifest = {"generated": dt.datetime.now().isoformat(timespec="seconds"), "documents": docs}
    _manifest_path(cfg).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return counts
