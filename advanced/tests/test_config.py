import pytest

from kp.config import CATEGORY_DIRS, ConfigError, load_config
from kp.issues import Issue, has_errors, render


def write_toml(root, body):
    (root / "kp.toml").write_text(body, encoding="utf-8")


def test_load_config_reads_fields_and_resolves_paths(tmp_path):
    write_toml(tmp_path, '[project]\nname = "Demo"\nlead = "A. Lead"\n'
                         '[evidence]\nengine = "notebooklm"\nrecency_floor = "2023-01-01"\n'
                         '[pack]\nsize = 5\n')
    cfg = load_config(tmp_path)
    assert cfg.project_name == "Demo"
    assert cfg.lead == "A. Lead"
    assert cfg.engine == "notebooklm"
    assert cfg.pack_size == 5
    assert cfg.recency_floor == "2023-01-01"
    assert cfg.corpus == tmp_path / "inputs" / "corpus"
    assert cfg.dir("evidence") == tmp_path / "package" / "05_evidence"
    assert cfg.handoffs == tmp_path / "outputs" / "07_handoffs"
    assert set(CATEGORY_DIRS) >= {"rulebook", "question_bank", "evidence", "working_drafts"}


def test_missing_toml_explains_fix(tmp_path):
    with pytest.raises(ConfigError, match="kp.example.toml"):
        load_config(tmp_path)


def test_invalid_engine_rejected(tmp_path):
    write_toml(tmp_path, '[project]\nname = "D"\nlead = "L"\n[evidence]\nengine = "web"\n')
    with pytest.raises(ConfigError, match="engine"):
        load_config(tmp_path)


def test_bad_recency_floor_rejected(tmp_path):
    write_toml(tmp_path, '[project]\nname = "D"\nlead = "L"\n[evidence]\nrecency_floor = "2023"\n')
    with pytest.raises(ConfigError, match="recency_floor"):
        load_config(tmp_path)


def test_issues_render_and_errors():
    issues = [Issue("warning", "a.md", "check this"), Issue("error", "b.md", "broken")]
    assert has_errors(issues)
    text = render(issues)
    assert "ERROR" in text and "b.md: broken" in text
    assert render([]) == "OK: no issues found"
