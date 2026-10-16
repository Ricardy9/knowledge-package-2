"""The Evidence Ledger: every claim in a draft maps to a ledger row and an Evidence Record."""
from __future__ import annotations

import csv
import re
from pathlib import Path

from kp.evidence import parse_record
from kp.issues import Issue

LEDGER_COLUMNS = ["claim_id", "draft", "marker", "claim", "evidence_file", "passages",
                  "source_tier", "confidence", "corroboration", "notes"]
TIERS = {"1", "2", "3"}
CONFIDENCE = {"high", "medium", "low"}
CORROBORATION = {"corroborated", "single-source", "temporal-consistency", "not-applicable"}
NON_DRAFT_FILES = {"readme.md", "issues_for_the_lead.md"}
_MARKER = re.compile(r"\[\^(\d+)\](?!:)")
_DEF = re.compile(r"(?m)^\[\^(\d+)\]:\s*(.+?)\s*$")


class LedgerError(Exception):
    pass


def ledger_path(cfg) -> Path:
    return cfg.dir("working_drafts") / "evidence_ledger.csv"


def load_ledger(cfg) -> list[dict]:
    path = ledger_path(cfg)
    if not path.is_file():
        raise LedgerError("package/06_working_drafts/evidence_ledger.csv not found: run `python -m kp init`")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != LEDGER_COLUMNS:
            raise LedgerError(f"evidence_ledger.csv columns must be exactly: {','.join(LEDGER_COLUMNS)}")
        rows = []
        for row in reader:
            if None in row:
                raise LedgerError(f"evidence_ledger.csv line {reader.line_num}: too many columns; "
                                  "put claims or notes that contain commas in double quotes")
            rows.append({k: (v or "").strip() for k, v in row.items()})
        return rows


def check_ledger(cfg, rows) -> list[Issue]:
    issues: list[Issue] = []
    seen = set()
    for n, row in enumerate(rows, start=2):
        where = f"evidence_ledger.csv line {n} ({row['claim_id'] or 'no id'})"
        def err(msg):
            issues.append(Issue("error", where, msg))
        if not row["claim_id"]:
            err("claim_id is empty")
        elif row["claim_id"] in seen:
            err(f"duplicate claim_id {row['claim_id']}")
        seen.add(row["claim_id"])
        for key in ("draft", "marker", "evidence_file"):
            if not row[key]:
                err(f"{key} is empty")
        if not row["claim"]:
            err("claim is empty")
        if row["source_tier"] not in TIERS:
            err(f"source_tier must be one of {sorted(TIERS)}")
        if row["confidence"] not in CONFIDENCE:
            err(f"confidence must be one of {sorted(CONFIDENCE)}")
        if row["corroboration"] not in CORROBORATION:
            err(f"corroboration must be one of {sorted(CORROBORATION)}")
        if not row["evidence_file"]:
            continue
        if "/" in row["evidence_file"] or "\\" in row["evidence_file"]:
            err("evidence_file must be a file name inside package/05_evidence (sweeps are never evidence)")
            continue
        path = cfg.dir("evidence") / row["evidence_file"]
        if not path.is_file():
            err(f"evidence file {row['evidence_file']} does not exist in package/05_evidence")
            continue
        rec = parse_record(path)
        wanted = [p.strip() for p in row["passages"].split(";") if p.strip()]
        if rec.meta.get("engine") == "local":
            if not wanted:
                err("passages is empty: name the Evidence Record passages, e.g. E1;E2")
            known = {f"E{p.eid}" for p in rec.passages}
            for p in wanted:
                if p not in known:
                    err(f"passage {p} is not in {row['evidence_file']}")
    return issues


def list_drafts(cfg) -> list[Path]:
    return sorted(p for p in cfg.dir("working_drafts").glob("*.md")
                  if p.name.lower() not in NON_DRAFT_FILES and not p.name.startswith(("_", "review_notes")))


def draft_definitions(cfg) -> dict[tuple[str, str], str]:
    out = {}
    for draft in list_drafts(cfg):
        for num, text in _DEF.findall(draft.read_text(encoding="utf-8")):
            out[(draft.name, num)] = text
    return out


def check_drafts(cfg, rows) -> list[Issue]:
    issues: list[Issue] = []
    ledger = {(r["draft"], r["marker"]) for r in rows}
    drafts = {d.name: d for d in list_drafts(cfg)}
    for name, path in drafts.items():
        text = path.read_text(encoding="utf-8")
        markers = set(_MARKER.findall(text))
        defs = {num for num, _ in _DEF.findall(text)}
        for m in sorted(markers, key=int):
            if m not in defs:
                issues.append(Issue("error", name, f"marker [^{m}] has no note definition"))
            if (name, m) not in ledger:
                issues.append(Issue("error", name, f"marker [^{m}] has no evidence ledger row"))
        for d in sorted(defs - markers, key=int):
            issues.append(Issue("warning", name, f"note [^{d}] is defined but never used"))
    for draft, marker in sorted(ledger):
        if draft not in drafts:
            issues.append(Issue("error", "evidence_ledger.csv", f"draft {draft} does not exist"))
        elif marker not in set(_MARKER.findall(drafts[draft].read_text(encoding="utf-8"))):
            issues.append(Issue("error", "evidence_ledger.csv", f"marker [^{marker}] is not in {draft}"))
    return issues
