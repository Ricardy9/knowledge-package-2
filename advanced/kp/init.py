"""Create the folder skeleton and seed files. Never overwrites anything."""
from __future__ import annotations

import shutil
from pathlib import Path

from kp.config import CATEGORY_DIRS

QUESTION_BANK_HEADER = "id,question,theme,collection,priority,status,still_holds,recency_floor,notes\n"
LEDGER_HEADER = ("claim_id,draft,marker,claim,evidence_file,passages,source_tier,"
                 "confidence,corroboration,notes\n")
APPROVALS_SEED = "# Approvals\n\nHuman checkpoints, one line each. Written by `python -m kp approve`.\n\n"
FOLD_BACK_SEED = ("# Fold-back log\n\nOne line per durable lesson: `- YYYY-MM-DD: <lesson> -> <rule file>`,"
                  " or `- YYYY-MM-DD: no durable lesson from <feedback file>`.\n\n")


def _dirs(root: Path) -> list[Path]:
    package = root / "package"
    return ([root / "inputs" / "00_background", root / "inputs" / "corpus",
             package / ".index", root / "outputs" / "07_handoffs", root / "outputs" / "reports"]
            + [package / d for d in CATEGORY_DIRS.values()])


def init_project(root: Path) -> list[str]:
    root = Path(root)
    created: list[str] = []
    for d in _dirs(root):
        if not d.is_dir():
            d.mkdir(parents=True)
            created.append(d.relative_to(root).as_posix() + "/")

    def seed(rel: str, content: str | None = None, copy_from: Path | None = None) -> None:
        target = root / rel
        if target.exists():
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        if copy_from is not None:
            shutil.copy(copy_from, target)
        else:
            target.write_text(content or "", encoding="utf-8")
        created.append(rel)

    seed("kp.toml", copy_from=root / "kp.example.toml")
    seed("inputs/direction_brief.md", copy_from=root / "instructions" / "templates" / "direction_brief.md")
    seed("package/02_question_bank/question_bank.csv", QUESTION_BANK_HEADER)
    seed("package/06_working_drafts/evidence_ledger.csv", LEDGER_HEADER)
    seed("package/09_methodology_log/approvals.md", APPROVALS_SEED)
    seed("package/09_methodology_log/fold_back.md", FOLD_BACK_SEED)
    return created
