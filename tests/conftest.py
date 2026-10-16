import shutil
from pathlib import Path

import pytest

from kp.config import load_config
from kp.ingest import ingest
from kp.init import init_project
from tests.fixtures.make_corpus import make_corpus

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture
def project(tmp_path, monkeypatch):
    """An initialised, empty project in a temporary repository root."""
    shutil.copy(REPO / "kp.example.toml", tmp_path / "kp.example.toml")
    shutil.copytree(REPO / "instructions" / "templates", tmp_path / "instructions" / "templates")
    init_project(tmp_path)
    toml = (tmp_path / "kp.toml").read_text(encoding="utf-8")
    toml = toml.replace('name = "My knowledge product"', 'name = "Riverland test product"')
    toml = toml.replace('lead = "Name of the Lead"', 'lead = "Test Lead"')
    (tmp_path / "kp.toml").write_text(toml, encoding="utf-8")
    monkeypatch.setenv("KP_ROOT", str(tmp_path))
    return load_config(tmp_path)


@pytest.fixture
def corpus_project(project):
    make_corpus(project.corpus)
    ingest(project)
    return project
