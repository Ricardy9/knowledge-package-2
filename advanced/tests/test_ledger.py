import pytest

from kp.cli import main
from kp.ledger import (LedgerError, check_drafts, check_ledger, draft_definitions, list_drafts,
                       load_ledger)
from tests.test_evidence import RECORD

DRAFT = """# Displacement

Riverland recorded 1,642 displacement events in 2023.[^1] Flooding displaced 12,400 households.[^2]

[^1]: Riverland Annual Situation Report 2025, p. 11, para 57.
[^2]: Riverland Annual Situation Report 2025, p. 11, para 58.
"""
ROWS = [
    "C001,displacement_v1.md,1,Riverland recorded 1642 displacement events in 2023.,20261016_Q01_x.md,E1,1,high,single-source,",
    "C002,displacement_v1.md,2,Flooding displaced 12400 households.,20261016_Q01_x.md,E2,1,high,single-source,",
]


def setup(cfg, rows=ROWS, draft=DRAFT):
    (cfg.dir("evidence") / "20261016_Q01_x.md").write_text(RECORD, encoding="utf-8")
    (cfg.dir("working_drafts") / "displacement_v1.md").write_text(draft, encoding="utf-8")
    path = cfg.dir("working_drafts") / "evidence_ledger.csv"
    path.write_text(path.read_text(encoding="utf-8") + "\n".join(rows) + "\n", encoding="utf-8")


def errors(issues):
    return " | ".join(i.message for i in issues if i.level == "error")


def test_consistent_ledger_and_draft(corpus_project):
    setup(corpus_project)
    rows = load_ledger(corpus_project)
    assert errors(check_ledger(corpus_project, rows)) == ""
    assert errors(check_drafts(corpus_project, rows)) == ""


def test_ledger_field_rules(corpus_project):
    setup(corpus_project, rows=[
        "C001,displacement_v1.md,1,claim,missing.md,E1,1,high,single-source,",
        "C002,displacement_v1.md,2,claim,20261016_Q01_x.md,E9,4,certain,maybe,",
        "C002,displacement_v1.md,3,,20261016_Q01_x.md,E1,1,high,single-source,",
    ])
    e = errors(check_ledger(corpus_project, load_ledger(corpus_project)))
    for expected in ("missing.md", "E9", "source_tier", "confidence", "corroboration",
                     "duplicate claim_id C002", "claim is empty"):
        assert expected in e


def test_marker_without_ledger_row_or_definition(corpus_project):
    draft = DRAFT.replace("households.[^2]", "households.[^2] More.[^3]")
    setup(corpus_project, rows=ROWS[:1], draft=draft)
    e = errors(check_drafts(corpus_project, load_ledger(corpus_project)))
    assert "[^2] has no evidence ledger row" in e
    assert "[^3] has no note definition" in e


def test_ledger_row_for_missing_marker(corpus_project):
    setup(corpus_project, draft=DRAFT.replace(" Flooding displaced 12,400 households.[^2]", ""))
    e = errors(check_drafts(corpus_project, load_ledger(corpus_project)))
    assert "marker [^2] is not in displacement_v1.md" in e


def test_too_many_columns_is_a_clear_error(corpus_project):
    setup(corpus_project, rows=[ROWS[0][:-1] + "a note, with a comma,"])
    with pytest.raises(LedgerError, match="line 2: too many columns"):
        load_ledger(corpus_project)


def test_draft_definitions(corpus_project):
    setup(corpus_project)
    defs = draft_definitions(corpus_project)
    assert defs[("displacement_v1.md", "1")] == "Riverland Annual Situation Report 2025, p. 11, para 57."
    assert len(defs) == 2


def test_list_drafts_excludes_non_drafts(corpus_project):
    setup(corpus_project)
    wd = corpus_project.dir("working_drafts")
    for name in ("README.md", "issues_for_the_lead.md", "_scratch.md", "review_notes_1.md"):
        (wd / name).write_text("# x\n", encoding="utf-8")
    assert [p.name for p in list_drafts(corpus_project)] == ["displacement_v1.md"]


def test_load_ledger_errors(corpus_project):
    path = corpus_project.dir("working_drafts") / "evidence_ledger.csv"
    path.write_text("claim_id,draft\n", encoding="utf-8")
    with pytest.raises(LedgerError, match="columns must be exactly"):
        load_ledger(corpus_project)
    path.unlink()
    with pytest.raises(LedgerError, match="not found"):
        load_ledger(corpus_project)


def test_cli_ledger_check(corpus_project):
    setup(corpus_project)
    assert main(["ledger", "check", "--draft"]) == 0


def test_cli_ledger_check_fails_on_unledgered_marker(corpus_project):
    setup(corpus_project, rows=ROWS[:1])
    assert main(["ledger", "check", "--draft"]) == 1
