"""The Question Bank: schema, the two required question rules, and query packs."""
from __future__ import annotations

import csv
import datetime as dt
import json
import re
from pathlib import Path

from kp.ingest import IngestError, load_manifest
from kp.issues import Issue

COLUMNS = ["id", "question", "theme", "collection", "priority", "status",
           "still_holds", "recency_floor", "notes"]
PRIORITIES = {"High": 0, "Medium": 1, "Low": 2}
STATUSES = {"Open", "Queried", "Drafted", "Needs follow-up", "Closed"}
SELECTABLE = {"Open", "Needs follow-up"}
_ID = re.compile(r"^Q\d{2,}$")
_BUNDLE_WORDS = re.compile(r"\b(each of|the following|list (the|all))\b", re.I)


class PackError(Exception):
    pass


def bank_path(cfg) -> Path:
    return cfg.dir("question_bank") / "question_bank.csv"


def load_bank(cfg) -> list[dict]:
    path = bank_path(cfg)
    if not path.is_file():
        raise PackError(f"{path.relative_to(cfg.root).as_posix()} not found: run `python -m kp init`")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            raise PackError(f"question_bank.csv columns must be exactly: {','.join(COLUMNS)}")
        rows = []
        for row in reader:
            if None in row:
                raise PackError(f"question_bank.csv line {reader.line_num}: too many columns; "
                                "put questions that contain commas in double quotes")
            rows.append({k: (v or "").strip() for k, v in row.items()})
        return rows


def _valid_date(text: str) -> bool:
    try:
        dt.date.fromisoformat(text)
        return True
    except ValueError:
        return False


def check_bank(cfg, rows) -> list[Issue]:
    issues: list[Issue] = []
    try:
        collections = {d["collection"] for d in load_manifest(cfg)["documents"] if d["status"] == "ok"}
    except IngestError:
        collections = None
    seen = set()
    for n, row in enumerate(rows, start=2):
        where = f"question_bank.csv line {n} ({row['id'] or 'no id'})"
        def err(msg):
            issues.append(Issue("error", where, msg))
        if not _ID.match(row["id"]):
            err("id must look like Q01")
        elif row["id"] in seen:
            err(f"duplicate id {row['id']}")
        seen.add(row["id"])
        if not row["question"]:
            err("question is empty")
        if row["priority"] not in PRIORITIES:
            err(f"priority must be one of {sorted(PRIORITIES)}")
        if row["status"] not in STATUSES:
            err(f"status must be one of {sorted(STATUSES)}")
        if row["still_holds"] not in ("yes", "no"):
            err("still_holds must be yes or no")
        if row["still_holds"] == "yes":
            floor = row["recency_floor"] or cfg.recency_floor
            if not floor or not _valid_date(floor):
                err("a 'still holds' question needs a recency floor date (recency_floor column "
                    "or kp.toml [evidence] recency_floor)")
        if not row["collection"]:
            err("collection is empty (use '*' to search all collections)")
        elif collections is not None and row["collection"] != "*" and row["collection"] not in collections:
            issues.append(Issue("warning", where,
                                f"no ingested documents in collection '{row['collection']}'"))
        if row["question"].count(",") >= 3 or _BUNDLE_WORDS.search(row["question"]):
            issues.append(Issue("warning", where, "may bundle several items: "
                                "split it into one question per item"))
    return issues


def _slug(text: str, limit: int = 40) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")[:limit].rstrip("-")


def evidence_filename(question_id: str, question: str, today: dt.date) -> str:
    return f"{today:%Y%m%d}_{question_id}_{_slug(question)}.md"


def build_pack(cfg, rows, n: int | None = None, today: dt.date | None = None) -> tuple[Path, Path]:
    today = today or dt.date.today()
    picked = sorted((r for r in rows if r["status"] in SELECTABLE),
                    key=lambda r: (PRIORITIES.get(r["priority"], 9), r["id"]))[: n or cfg.pack_size]
    if not picked:
        raise PackError("no Open or Needs follow-up questions in the Question Bank")
    items = [{"id": r["id"], "question": r["question"], "collection": r["collection"],
              "still_holds": r["still_holds"],
              "recency_floor": (r["recency_floor"] or cfg.recency_floor) if r["still_holds"] == "yes" else "",
              "evidence_file": evidence_filename(r["id"], r["question"], today)} for r in picked]
    out_dir = cfg.dir("query_packs")
    stem = f"{today:%Y%m%d}_pack"
    js = out_dir / f"{stem}.json"
    js.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [f"# Query pack {today:%Y-%m-%d}", "",
             f"Engine: **{cfg.engine}**. Prompt: `instructions/prompts/"
             + ("local_evidence.md" if cfg.engine == "local" else "notebooklm_courier.md") + "`.", ""]
    for it in items:
        lines += [f"## {it['id']}", "", it["question"], "",
                  f"- collection: {it['collection']}",
                  f"- save evidence to: `package/05_evidence/{it['evidence_file']}`"]
        if it["recency_floor"]:
            lines.append(f"- recency floor: {it['recency_floor']} (at least one source dated on or after)")
        lines.append("")
    md = out_dir / f"{stem}.md"
    md.write_text("\n".join(lines), encoding="utf-8")
    return md, js
