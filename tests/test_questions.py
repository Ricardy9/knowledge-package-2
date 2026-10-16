import datetime as dt
import json

import pytest

from kp.questions import PackError, build_pack, check_bank, evidence_filename, load_bank

GOOD = [
    "Q01,What displacement did Riverland record in 2023?,Displacement,alpha,High,Open,no,,",
    "Q02,Does weak budget execution still hold since the 2021 assessment?,Governance,alpha,Medium,Open,yes,2024-01-01,",
    "Q03,How many disputes did women's peace committees mediate in 2024?,Resilience,beta,High,Closed,no,,",
]


def write_bank(cfg, lines):
    path = cfg.dir("question_bank") / "question_bank.csv"
    path.write_text(path.read_text(encoding="utf-8") + "\n".join(lines) + "\n", encoding="utf-8")


def messages(issues, level):
    return [i.message for i in issues if i.level == level]


def test_valid_bank_has_no_errors(corpus_project):
    write_bank(corpus_project, GOOD)
    assert messages(check_bank(corpus_project, load_bank(corpus_project)), "error") == []


def test_rules_are_enforced(corpus_project):
    write_bank(corpus_project, [
        "Q01,,Theme,alpha,High,Open,no,,",
        "Q01,Duplicate id?,Theme,alpha,Urgent,Open,no,,",
        "Q04,Does X still hold?,Theme,alpha,Low,Open,yes,,",
        'Q05,"Which drivers, factors, actors, and trends matter?",Theme,gamma,Low,Open,no,,',
    ])
    issues = check_bank(corpus_project, load_bank(corpus_project))
    errors = " | ".join(messages(issues, "error"))
    assert "question is empty" in errors
    assert "duplicate id Q01" in errors
    assert "priority" in errors
    assert "recency floor" in errors
    warnings = " | ".join(messages(issues, "warning"))
    assert "one question per item" in warnings
    assert "no ingested documents in collection 'gamma'" in warnings


def test_pack_selects_open_questions_by_priority(corpus_project):
    write_bank(corpus_project, GOOD)
    md, js = build_pack(corpus_project, load_bank(corpus_project), today=dt.date(2026, 10, 16))
    items = json.loads(js.read_text(encoding="utf-8"))
    assert [i["id"] for i in items] == ["Q01", "Q02"]          # Q03 is Closed
    assert items[0]["evidence_file"] == evidence_filename("Q01", items[0]["question"], dt.date(2026, 10, 16))
    assert items[0]["evidence_file"].startswith("20261016_Q01_what-displacement")
    text = md.read_text(encoding="utf-8")
    assert "Q02" in text and "recency floor: 2024-01-01" in text


def test_pack_with_nothing_open_fails(corpus_project):
    write_bank(corpus_project, [GOOD[2]])
    with pytest.raises(PackError, match="no Open"):
        build_pack(corpus_project, load_bank(corpus_project))


def test_unquoted_comma_row_is_a_clear_error(corpus_project):
    write_bank(corpus_project, ["Q01,What happened, when, and why?,Theme,alpha,High,Open,no,,"])
    with pytest.raises(PackError, match="too many columns"):
        load_bank(corpus_project)
