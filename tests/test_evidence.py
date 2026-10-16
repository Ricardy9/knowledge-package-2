from kp.evidence import check_evidence, parse_record

RECORD = """---
question_id: Q01
question: What displacement did Riverland record in 2023?
date: 2026-10-16
engine: local
collection: alpha
---
## Answer
Riverland recorded 1,642 displacement events in 2023 [E1], and flooding displaced 12,400 households [E2].

## Passages
[E1] "Riverland recorded 1,642 displacement events in 2023." — alpha__alpha-report, p. 11, para 57
[E2] "Flooding along the Blue Reed basin displaced 12,400 households." — alpha__alpha-report, p. 11, para 58
"""


def save(cfg, name, text):
    path = cfg.dir("evidence") / name
    path.write_text(text, encoding="utf-8")
    return path


def errors(issues):
    return [i.message for i in issues if i.level == "error"]


def test_parse_record(corpus_project):
    rec = parse_record(save(corpus_project, "20261016_Q01_x.md", RECORD))
    assert rec.meta["question_id"] == "Q01"
    assert [p.eid for p in rec.passages] == [1, 2]
    assert rec.passages[0].doc_id == "alpha__alpha-report"
    assert rec.passages[0].page == "11" and rec.passages[0].para == 57
    assert rec.parse_errors == []


def test_valid_record_passes_and_is_registered(corpus_project):
    save(corpus_project, "20261016_Q01_x.md", RECORD)
    assert errors(check_evidence(corpus_project)) == []
    assert (corpus_project.dir("evidence") / ".hashes.json").is_file()


def test_altered_quote_is_rejected(corpus_project):
    save(corpus_project, "20261016_Q01_x.md", RECORD.replace("12,400 households", "14,000 households"))
    assert any("not found on" in m for m in errors(check_evidence(corpus_project)))


def test_wrong_page_is_rejected(corpus_project):
    save(corpus_project, "20261016_Q01_x.md", RECORD.replace("p. 11, para 58", "p. 13, para 58"))
    assert any("not found on" in m for m in errors(check_evidence(corpus_project)))


def test_unknown_reference_and_missing_answer(corpus_project):
    bad = RECORD.replace("[E2].", "[E3].")
    save(corpus_project, "20261016_Q01_x.md", bad)
    assert any("[E3]" in m for m in errors(check_evidence(corpus_project)))


def test_not_found_answer_is_valid(corpus_project):
    text = RECORD.split("## Answer")[0] + "## Answer\nNOT FOUND IN SOURCES\n\n## Passages\n"
    save(corpus_project, "20261016_Q09_x.md", text)
    assert errors(check_evidence(corpus_project)) == []


def test_edit_after_check_is_detected(corpus_project):
    path = save(corpus_project, "20261016_Q01_x.md", RECORD)
    check_evidence(corpus_project)
    path.write_text(RECORD.replace("and flooding", "while flooding"), encoding="utf-8")
    assert any("changed after" in m for m in errors(check_evidence(corpus_project)))


def test_notebooklm_record_reports_quote_check_not_applicable(corpus_project):
    text = RECORD.replace("engine: local", "engine: notebooklm").split("## Passages")[0]
    save(corpus_project, "20261016_Q01_x.md", text)
    issues = check_evidence(corpus_project)
    assert errors(issues) == []
    assert any(i.level == "info" and "not applicable" in i.message for i in issues)


def test_quote_from_next_page_cited_on_wrong_page_is_rejected(corpus_project):
    text = RECORD.replace(
        "Flooding along the Blue Reed basin displaced 12,400 households.",
        "Grain prices rose 38 percent between March and June 2024.")
    save(corpus_project, "20261016_Q01_x.md", text)
    assert any("not found on" in m for m in errors(check_evidence(corpus_project)))


def test_mixed_not_found_answer_is_not_valid(corpus_project):
    text = (RECORD.split("## Answer")[0]
            + "## Answer\nDisplacement was 9,999 [E1]. NOT FOUND IN SOURCES for 2022.\n\n## Passages\n")
    save(corpus_project, "20261016_Q09_x.md", text)
    assert any("[E1]" in m for m in errors(check_evidence(corpus_project)))
