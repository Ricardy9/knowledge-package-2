import csv
import json

import pytest

from kp.verify import VerifyError, build, collect, validate_verdict, verification_dir
from tests.test_ledger import setup


def verdict(item, tier, quote, **kw):
    v = {"item_id": item, "tier": tier, "supporting_quote": quote, "reasoning": "r",
         "confidence": 0.9, "named_specifics_checked": True}
    v.update(kw)
    return v


def test_schema_rules_ported_from_pilot():
    assert validate_verdict(verdict("a#1", "TIER_I", "text"))[0]
    assert not validate_verdict(verdict("a#1", "TIER_I", ""))[0]
    assert not validate_verdict(verdict("a#1", "TIER_II", "NOT_FOUND_IN_SOURCE"))[0]
    assert not validate_verdict(verdict("a#1", "TIER_I", "t", confidence=1.5))[0]
    assert validate_verdict(verdict("a#1", "TIER_III", "NOT_FOUND_IN_SOURCE"))[0]


def test_build_writes_self_contained_batches(corpus_project):
    setup(corpus_project)
    paths = build(corpus_project)
    assert len(paths) == 1
    text = paths[0].read_text(encoding="utf-8")
    assert "displacement_v1.md#1" in text and "12,400 households" in text
    assert "Do not open files" in text


def test_collect_maps_tiers_to_actions_and_rejects_unearned_quotes(corpus_project):
    setup(corpus_project)
    build(corpus_project)
    vdir = verification_dir(corpus_project)
    (vdir / "verdicts" / "batch_001.json").write_text(json.dumps([
        verdict("displacement_v1.md#1", "TIER_I", "Riverland recorded 1,642 displacement events in 2023."),
        verdict("displacement_v1.md#2", "TIER_I", "a quote that is not in the source"),
    ]), encoding="utf-8")
    summary = collect(corpus_project)
    assert summary["actions"] == {"OK": 1, "REGRADE": 1}
    assert summary["rejected"] == 1
    with (vdir / "worklist.csv").open(encoding="utf-8") as fh:
        rows = {r["item_id"]: r for r in csv.DictReader(fh)}
    assert rows["displacement_v1.md#2"]["issue"] == "no valid verdict"


def test_tier_three_triggers_whole_document_re_search(corpus_project):
    setup(corpus_project)
    build(corpus_project)
    vdir = verification_dir(corpus_project)
    (vdir / "verdicts" / "batch_001.json").write_text(json.dumps([
        verdict("displacement_v1.md#1", "TIER_III", "NOT_FOUND_IN_SOURCE"),
        verdict("displacement_v1.md#2", "TIER_II", "Flooding along the Blue Reed basin displaced 12,400 households."),
    ]), encoding="utf-8")
    collect(corpus_project)
    with (vdir / "worklist.csv").open(encoding="utf-8") as fh:
        rows = {r["item_id"]: r for r in csv.DictReader(fh)}
    assert rows["displacement_v1.md#1"]["action"] == "CHECK"
    assert rows["displacement_v1.md#1"]["location"].startswith("alpha__alpha-report, p. 11")
    assert rows["displacement_v1.md#2"]["action"] == "CHECK"


def test_human_status_survives_recollect_and_rebuild_needs_force(corpus_project):
    setup(corpus_project)
    build(corpus_project)
    vdir = verification_dir(corpus_project)
    (vdir / "verdicts" / "batch_001.json").write_text("[]", encoding="utf-8")
    collect(corpus_project)
    path = vdir / "worklist.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    rows[0]["status"], rows[0]["notes"] = "DONE", "checked by hand"
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    collect(corpus_project)
    again = list(csv.DictReader(path.open(encoding="utf-8")))
    assert again[0]["status"] == "DONE" and again[0]["notes"] == "checked by hand"
    with pytest.raises(VerifyError, match="--force"):
        build(corpus_project)
    build(corpus_project, force=True)
    assert any(p.name.startswith("verification_") for p in corpus_project.dir("archive").iterdir())
