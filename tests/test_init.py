from kp.init import LEDGER_HEADER, QUESTION_BANK_HEADER, init_project


def test_init_creates_skeleton_and_seed_files(project):
    for key in ("rulebook", "question_bank", "evidence", "working_drafts", "archive"):
        assert project.dir(key).is_dir()
    assert project.corpus.is_dir() and project.handoffs.is_dir() and project.reports.is_dir()
    assert (project.dir("question_bank") / "question_bank.csv").read_text(encoding="utf-8") == QUESTION_BANK_HEADER
    assert (project.dir("working_drafts") / "evidence_ledger.csv").read_text(encoding="utf-8") == LEDGER_HEADER
    assert "TODO:" in project.direction_brief.read_text(encoding="utf-8")
    assert (project.dir("methodology_log") / "approvals.md").is_file()
    assert (project.dir("methodology_log") / "fold_back.md").is_file()


def test_init_never_overwrites(project):
    project.direction_brief.write_text("# Mine", encoding="utf-8")
    created = init_project(project.root)
    assert project.direction_brief.read_text(encoding="utf-8") == "# Mine"
    assert created == []
