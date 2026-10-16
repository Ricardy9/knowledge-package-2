"""Project configuration. Every path the runner touches is derived from here."""
from __future__ import annotations

import datetime as dt
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

ENGINES = {"local", "notebooklm"}

CATEGORY_DIRS = {
    "rulebook": "01_rulebook",
    "question_bank": "02_question_bank",
    "query_packs": "03_query_packs",
    "coverage_sweeps": "04_coverage_sweeps",
    "evidence": "05_evidence",
    "working_drafts": "06_working_drafts",
    "feedback_log": "08_feedback_log",
    "methodology_log": "09_methodology_log",
    "archive": "10_archive",
}


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    root: Path
    project_name: str
    lead: str
    engine: str = "local"
    pack_size: int = 10
    recency_floor: str = ""
    handoff_title: str = ""

    @property
    def inputs(self) -> Path:
        return self.root / "inputs"

    @property
    def corpus(self) -> Path:
        return self.inputs / "corpus"

    @property
    def background(self) -> Path:
        return self.inputs / "00_background"

    @property
    def direction_brief(self) -> Path:
        return self.inputs / "direction_brief.md"

    @property
    def package(self) -> Path:
        return self.root / "package"

    @property
    def index_dir(self) -> Path:
        return self.package / ".index"

    @property
    def outputs(self) -> Path:
        return self.root / "outputs"

    @property
    def handoffs(self) -> Path:
        return self.outputs / "07_handoffs"

    @property
    def reports(self) -> Path:
        return self.outputs / "reports"

    def dir(self, key: str) -> Path:
        return self.package / CATEGORY_DIRS[key]


def find_root(start: Path | None = None) -> Path:
    """The repository root: KP_ROOT if set, else the nearest folder holding kp.example.toml."""
    env = os.environ.get("KP_ROOT")
    if env:
        return Path(env).resolve()
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "kp.example.toml").is_file():
            return candidate
    raise ConfigError("cannot find the repository root (no kp.example.toml above "
                      f"{here}); run commands from inside the repository")


def _valid_date(text: str) -> bool:
    try:
        dt.date.fromisoformat(text)
        return True
    except ValueError:
        return False


def load_config(root: Path | None = None) -> Config:
    root = Path(root) if root else find_root()
    path = root / "kp.toml"
    if not path.is_file():
        raise ConfigError("kp.toml not found: run `python -m kp init` or copy "
                          "kp.example.toml to kp.toml and edit it")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"kp.toml is not valid TOML: {exc}") from exc
    project = data.get("project", {})
    evidence = data.get("evidence", {})
    name = str(project.get("name", "")).strip()
    lead = str(project.get("lead", "")).strip()
    if not name or not lead:
        raise ConfigError("kp.toml: [project] name and lead are required")
    engine = str(evidence.get("engine", "local")).strip()
    if engine not in ENGINES:
        raise ConfigError(f"kp.toml: [evidence] engine must be one of {sorted(ENGINES)}, got {engine!r}")
    floor = str(evidence.get("recency_floor", "")).strip()
    if floor and not _valid_date(floor):
        raise ConfigError(f"kp.toml: [evidence] recency_floor must be YYYY-MM-DD, got {floor!r}")
    size = data.get("pack", {}).get("size", 10)
    if not isinstance(size, int) or size < 1:
        raise ConfigError("kp.toml: [pack] size must be a positive integer")
    title = str(data.get("handoff", {}).get("title", "")).strip()
    return Config(root=root, project_name=name, lead=lead, engine=engine,
                  pack_size=size, recency_floor=floor, handoff_title=title)
