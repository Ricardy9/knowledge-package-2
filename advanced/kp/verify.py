"""Independent verification: blind grading batches, a strict verdict schema, whole-document
re-search, and a worklist a person signs off.

The schema and rubric are ported from the pilot's citation audit (`stage2_schema.py`,
`stage2_prompt.py`). A TIER_I/II verdict without a verbatim quote from the supplied text
is unearned and rejected.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import shutil
from collections import Counter
from pathlib import Path

from kp.evidence import parse_record
from kp.ingest import load_pages, pages_for
from kp.ledger import draft_definitions, load_ledger
from kp.search import locator, search_pages
from kp.textutil import normalize_for_match

NOT_FOUND = "NOT_FOUND_IN_SOURCE"
TIERS = {"TIER_I", "TIER_II", "TIER_III"}
REQUIRED = ("item_id", "tier", "supporting_quote", "reasoning", "confidence", "named_specifics_checked")
WORKLIST_COLUMNS = ["item_id", "tier", "action", "issue", "supporting_quote", "location", "status", "notes"]

RUBRIC = """You are checking citations in a working draft of a knowledge product. For each item
you are given a CLAIM from the draft, the CITATION attached to it, and the SOURCE TEXT the
citation points to. Decide how well the supplied source text supports that specific claim.

TIER_I   The source directly and unambiguously supports the claim. You can point to the
         sentence or table in the source text that states it.
TIER_II  The claim is matchable to the source but strays from it: paraphrase drift, a causal
         verb stronger than the source supports, a rounded or restated figure, or a date,
         place or person stated more precisely than in the source.
TIER_III You cannot match the claim to the source text at all.

Rules:
- Judge only the claim shown, not the surrounding argument.
- Judge only from the source text supplied in the item. Do not open files, do not browse,
  and do not use prior knowledge. If the supplied text does not settle the claim, that is
  TIER_III.
- If the claim names a specific person, place, figure or dated event, the supplied text
  must state that specific detail; otherwise the verdict is TIER_II at best.
- Copy supporting_quote verbatim from the supplied text. Never paraphrase into that field.
- If the supplied text does not address the claim, return TIER_III with supporting_quote
  exactly "NOT_FOUND_IN_SOURCE". TIER_I and TIER_II require a real quote.
- Do not be generous.

Return only a JSON array, one object per item, nothing else:
[{"item_id": "<as given>", "tier": "TIER_I|TIER_II|TIER_III", "supporting_quote": "<verbatim or NOT_FOUND_IN_SOURCE>", "reasoning": "<one or two sentences>", "confidence": <0.0-1.0>, "named_specifics_checked": <true|false>}]
"""


class VerifyError(Exception):
    pass


def validate_verdict(obj) -> tuple[bool, str]:
    if not isinstance(obj, dict):
        return False, "verdict is not an object"
    for f in REQUIRED:
        if f not in obj:
            return False, f"missing field: {f}"
    if not isinstance(obj["item_id"], str) or not obj["item_id"].strip():
        return False, "item_id must be a non-empty string"
    if obj["tier"] not in TIERS:
        return False, f"unknown tier: {obj['tier']!r}"
    c = obj["confidence"]
    if isinstance(c, bool) or not isinstance(c, (int, float)) or not 0.0 <= c <= 1.0:
        return False, f"confidence out of range: {c!r}"
    quote = str(obj["supporting_quote"]).strip()
    if obj["tier"] in ("TIER_I", "TIER_II"):
        if not quote:
            return False, "TIER_I and TIER_II require a supporting quote from the source"
        if NOT_FOUND in quote:
            return False, f"tier {obj['tier']} with {NOT_FOUND}: the tier is unearned"
    if not str(obj["reasoning"]).strip():
        return False, "reasoning is empty"
    if not isinstance(obj["named_specifics_checked"], bool):
        return False, "named_specifics_checked must be a boolean"
    return True, "ok"


def verification_dir(cfg) -> Path:
    return cfg.dir("working_drafts") / "verification"


def _items(cfg) -> list[dict]:
    defs = draft_definitions(cfg)
    items = []
    for row in load_ledger(cfg):
        rec = parse_record(cfg.dir("evidence") / row["evidence_file"])
        sources, doc_ids = [], []
        if rec.meta.get("engine") == "local":
            wanted = {p.strip() for p in row["passages"].split(";") if p.strip()}
            for p in rec.passages:
                if f"E{p.eid}" not in wanted:
                    continue
                pages = load_pages(cfg, p.doc_id)
                idx = pages_for(pages, p.page)
                text = " ".join(pages[idx[0]]["text"].split()) if idx else p.quote
                sources.append({"source": f"{p.doc_id}, p. {p.page}", "text": text})
                doc_ids.append(p.doc_id)
        else:
            sources.append({"source": f"evidence record {row['evidence_file']}", "text": rec.answer})
        items.append({"item_id": f"{row['draft']}#{row['marker']}", "claim": row["claim"],
                      "citation": defs.get((row["draft"], row["marker"]), ""),
                      "source_text": sources, "_doc_ids": doc_ids})
    return items


def build(cfg, batch_size: int = 10, force: bool = False) -> list[Path]:
    vdir = verification_dir(cfg)
    verdict_dir = vdir / "verdicts"
    if verdict_dir.is_dir() and any(verdict_dir.glob("*.json")):
        if not force:
            raise VerifyError("verdicts already exist: use --force to archive this round and rebuild")
        shutil.move(str(vdir), str(cfg.dir("archive") / f"verification_{dt.datetime.now():%Y%m%d_%H%M%S}"))
    items = _items(cfg)
    if not items:
        raise VerifyError("the evidence ledger has no rows to verify")
    batch_dir = vdir / "batches"
    if batch_dir.is_dir():
        shutil.rmtree(batch_dir)
    batch_dir.mkdir(parents=True)
    (vdir / "verdicts").mkdir(exist_ok=True)
    public = [{k: v for k, v in it.items() if not k.startswith("_")} for it in items]
    paths = []
    for n, start in enumerate(range(0, len(public), batch_size), start=1):
        path = batch_dir / f"batch_{n:03d}.md"
        path.write_text(RUBRIC + "\nITEMS:\n" + json.dumps(public[start:start + batch_size], indent=2,
                                                           ensure_ascii=False), encoding="utf-8")
        paths.append(path)
    (vdir / "items.json").write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    return paths


def _previous(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        return {r["item_id"]: (r.get("status", ""), r.get("notes", "")) for r in csv.DictReader(fh)}


def collect(cfg) -> dict:
    vdir = verification_dir(cfg)
    items_path = vdir / "items.json"
    if not items_path.is_file():
        raise VerifyError("no verification round found: run `python -m kp verify build` first")
    items = json.loads(items_path.read_text(encoding="utf-8"))
    by_id = {it["item_id"]: it for it in items}
    accepted, rejected = {}, []
    for batch in sorted((vdir / "batches").glob("batch_*.md")):
        vf = vdir / "verdicts" / f"{batch.stem}.json"
        if not vf.is_file():
            continue
        try:
            data = json.loads(vf.read_text(encoding="utf-8"))
        except ValueError as exc:
            rejected.append({"batch": batch.stem, "reason": f"not valid JSON: {exc}"})
            continue
        if not isinstance(data, list):
            rejected.append({"batch": batch.stem, "reason": "top level must be a JSON array"})
            continue
        for v in data:
            ok, msg = validate_verdict(v)
            if ok and v["item_id"] not in by_id:
                ok, msg = False, "unknown item_id"
            if ok and v["tier"] != "TIER_III":
                supplied = " ".join(s["text"] for s in by_id[v["item_id"]]["source_text"])
                if normalize_for_match(v["supporting_quote"]) not in normalize_for_match(supplied):
                    ok, msg = False, "supporting_quote is not verbatim in the supplied source text"
            if ok:
                accepted[v["item_id"]] = v
            else:
                rejected.append({"item_id": v.get("item_id") if isinstance(v, dict) else None, "reason": msg})
    previous = _previous(vdir / "worklist.csv")
    rows = []
    for it in items:
        v = accepted.get(it["item_id"])
        tier, location, quote = "", "", ""
        if v is None:
            action, issue = "REGRADE", "no valid verdict"
        else:
            tier, quote = v["tier"], v["supporting_quote"]
            if tier == "TIER_I":
                action, issue = "OK", ""
            elif tier == "TIER_II":
                action, issue = "CHECK", v["reasoning"]
            else:
                hits = []
                for doc_id in dict.fromkeys(it["_doc_ids"]):
                    for h in search_pages(it["claim"], load_pages(cfg, doc_id), k=1):
                        h["doc_id"] = doc_id
                        hits.append(h)
                if hits:
                    best = max(hits, key=lambda h: h["score"])
                    action, location = "CHECK", locator(best)
                    issue = "not supported by the cited passage; a candidate passage exists elsewhere in the cited document"
                else:
                    action, issue = "FIX", "not supported by the cited source: find support or revise the claim"
        status, notes = previous.get(it["item_id"], ("", ""))
        rows.append({"item_id": it["item_id"], "tier": tier, "action": action, "issue": issue,
                     "supporting_quote": quote, "location": location, "status": status, "notes": notes})
    with (vdir / "worklist.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=WORKLIST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    (vdir / "rejected.json").write_text(json.dumps(rejected, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"items": len(items), "actions": dict(Counter(r["action"] for r in rows)), "rejected": len(rejected)}
