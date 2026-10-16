"""Evidence Records: parse, verify every quote against the corpus, and enforce write-once."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from kp.ingest import IngestError, load_manifest, load_pages, pages_for
from kp.issues import Issue
from kp.textutil import normalize_for_match

NOT_FOUND = "NOT FOUND IN SOURCES"
REQUIRED_META = ("question_id", "question", "date", "engine")
_FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
_SECTION = re.compile(r"(?m)^##\s+(.+?)\s*$")
_PASSAGE = re.compile(r'^\[E(?P<eid>\d+)\]\s+"(?P<quote>.+)"\s+(?:—|–|--|-)\s+'
                      r'(?P<doc>[a-z0-9_\-]+),\s+p\.\s*(?P<page>pdf:\d+|\d+)'
                      r'(?:,\s+para\s+(?P<para>\d+))?\s*$')
_REF = re.compile(r"\[E(\d+)\]")


@dataclass
class Passage:
    eid: int
    quote: str
    doc_id: str
    page: str
    para: int | None


@dataclass
class EvidenceRecord:
    path: Path
    meta: dict
    answer: str
    passages: list[Passage] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)


def parse_record(path: Path) -> EvidenceRecord:
    text = Path(path).read_text(encoding="utf-8")
    rec = EvidenceRecord(path=Path(path), meta={}, answer="")
    m = _FRONT.match(text)
    if not m:
        rec.parse_errors.append("missing front matter block (--- ... ---)")
        body = text
    else:
        for line in m.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                rec.meta[key.strip()] = value.strip()
        body = text[m.end():]
    parts = _SECTION.split(body)
    sections = {parts[i].strip().casefold(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}
    rec.answer = sections.get("answer", "").strip()
    for line in sections.get("passages", "").splitlines():
        line = line.strip()
        if not line:
            continue
        pm = _PASSAGE.match(line)
        if not pm:
            rec.parse_errors.append(f"passage line not in the required format: {line[:80]}")
            continue
        rec.passages.append(Passage(int(pm["eid"]), pm["quote"], pm["doc"], pm["page"],
                                    int(pm["para"]) if pm["para"] else None))
    return rec


def quote_on_page(pages: list[dict], label: str, quote: str) -> bool:
    """The quote must appear verbatim on the labelled page (or run onto the next one)."""
    q = normalize_for_match(quote)
    if not q:
        return False
    for i in pages_for(pages, label):
        page_norm = normalize_for_match(pages[i]["text"])
        span = pages[i]["text"] + ("\n" + pages[i + 1]["text"] if i + 1 < len(pages) else "")
        pos = normalize_for_match(span).find(q)
        if 0 <= pos < len(page_norm):
            return True
    return False


def evidence_files(cfg) -> list[Path]:
    return sorted(p for p in cfg.dir("evidence").glob("*.md") if p.name.lower() != "readme.md")


def check_record(cfg, rec: EvidenceRecord) -> list[Issue]:
    where = rec.path.name
    issues = [Issue("error", where, e) for e in rec.parse_errors]
    for key in REQUIRED_META:
        if not rec.meta.get(key):
            issues.append(Issue("error", where, f"front matter is missing '{key}'"))
    engine = rec.meta.get("engine", "")
    if engine and engine not in ("local", "notebooklm"):
        issues.append(Issue("error", where, f"engine must be local or notebooklm, got {engine!r}"))
    if not rec.answer:
        issues.append(Issue("error", where, "the ## Answer section is empty"))
        return issues
    if engine == "notebooklm":
        issues.append(Issue("info", where, "quote fidelity: not applicable (NotebookLM answer stored verbatim)"))
        return issues
    if rec.answer.strip() == NOT_FOUND and not rec.passages:
        return issues
    ids = {p.eid for p in rec.passages}
    refs = {int(r) for r in _REF.findall(rec.answer)}
    if not refs:
        issues.append(Issue("error", where, f"the answer cites no passages: use [E1]… or write {NOT_FOUND}"))
    for r in sorted(refs - ids):
        issues.append(Issue("error", where, f"answer cites [E{r}] but no such passage is listed"))
    for r in sorted(ids - refs):
        issues.append(Issue("warning", where, f"passage [E{r}] is listed but never cited in the answer"))
    try:
        ok_docs = {d["doc_id"] for d in load_manifest(cfg)["documents"] if d["status"] == "ok"}
    except IngestError as exc:
        return issues + [Issue("error", where, str(exc))]
    for p in rec.passages:
        if p.doc_id not in ok_docs:
            issues.append(Issue("error", where, f"[E{p.eid}] cites unknown document {p.doc_id!r}"))
        elif not quote_on_page(load_pages(cfg, p.doc_id), p.page, p.quote):
            issues.append(Issue("error", where,
                                f"[E{p.eid}] quote not found on {p.doc_id} p. {p.page} (quotes must be verbatim)"))
    return issues


def check_evidence(cfg) -> list[Issue]:
    registry_path = cfg.dir("evidence") / ".hashes.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.is_file() else {}
    issues: list[Issue] = []
    for path in evidence_files(cfg):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if path.name in registry and registry[path.name] != digest:
            issues.append(Issue("error", path.name, "changed after it was first checked: evidence is "
                                "write-once. Restore the original or save a corrected record under a new name"))
            continue
        found = check_record(cfg, parse_record(path))
        issues += found
        if path.name not in registry and not any(i.level == "error" for i in found):
            registry[path.name] = digest
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
    return issues
