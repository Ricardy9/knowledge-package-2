# Knowledge Package 2.0

**A reproducible, source-grounded knowledge production workflow, operated through Claude Code.**

Knowledge Package 2.0 turns a defined collection of source documents into a structured, traceable knowledge product: direction → research questions → verbatim evidence → evidence ledger → cited draft → independent verification → handoff → feedback fold-back. Every claim in a draft must trace back, through the ledger, to a verbatim quote on a specific page of a source document.

It generalizes a workflow proven in live production in 2026. The specification for the knowledge product is the *Suite of Deliverables v2.0*.

> **Status: in development (private).** The runner core is built and tested (49 automated tests passing). Onboarding docs (`CLAUDE.md`, `START.md`), the generalized instruction package and the remaining runner commands are in progress — see *Status* below.

## How it works

| Stage | Who | Mechanism |
|---|---|---|
| Direction | Lead | `inputs/direction_brief.md` → Rulebook (Lead approves) |
| Source corpus | Runner | `python -m kp ingest` — page-level text with printed page numbers; duplicates and unreadable files reported |
| Questions | Claude Code + runner | `package/02_question_bank/question_bank.csv`; `python -m kp questions check` enforces one checkable item per question and a recency floor on "still holds?" questions |
| Query pack | Runner | `python -m kp pack` |
| Evidence | Claude Code + runner | `python -m kp search` finds passages with document, page and paragraph; Evidence Records store verbatim quotes; `python -m kp evidence check` verifies every quote word-for-word on the cited page and makes records write-once |
| Evidence ledger | Claude Code + runner | `python -m kp ledger check --draft` — every citation marker in a draft maps to a ledger row and an evidence passage |
| Independent verification | Runner + blind subagents | `python -m kp verify build` / `collect` — self-contained grading batches, strict verdict schema (no unearned quotes), whole-document re-search, human-signed worklist |
| Handoff, status | Runner | *in progress* |

## Repository map

```
inputs/     YOU populate: 00_background/, corpus/<collection>/, direction_brief.md   (git-ignored)
package/    RUNNER-managed working materials, categories 01–10                    (git-ignored)
outputs/    THE KNOWLEDGE PRODUCT: 07_handoffs/, reports/                         (git-ignored)
kp/         the Python runner (python -m kp)
tests/      automated tests + synthetic fixture corpus (fictional "Riverland")
docs/       documentation (in progress)
```

Only folder `README.md` files are tracked under `inputs/`, `package/` and `outputs/`, so confidential source documents and drafts cannot be committed by accident.

## Try it

Requires Python 3.11+.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt     # POSIX: .venv/bin/python
.venv/Scripts/python -m pytest -q                           # 49 passed
.venv/Scripts/python -m kp init                             # folder skeleton + kp.toml
.venv/Scripts/python tests/fixtures/make_corpus.py inputs/corpus   # synthetic demo corpus
.venv/Scripts/python -m kp ingest
.venv/Scripts/python -m kp search "grain prices 38 percent"         # → alpha__alpha-report, p. 12, para 60
```

## Status

| Built and tested | In progress |
|---|---|
| Config, `init`, folder skeleton | `kp handoff` (Word draft + Issues for the Lead) |
| `ingest` (PDF/DOCX/TXT/MD, printed folios, duplicates, failures) | `kp approve rulebook`, `kp check` pre-flight and package hygiene |
| `search` with page/paragraph locators | `kp status` completion report on the 10 deliverables |
| Question Bank rules and query packs | Generalized instruction package and prompts |
| Evidence Records: verbatim quote checks, write-once | `README` / `CLAUDE.md` / `START.md` onboarding for Claude Code |
| Evidence Ledger and draft-marker checks | End-to-end trial runs |
| Independent verification (`verify build` / `collect`) | |

## Principles

- Never invent a citation, figure, quote or date; `NOT FOUND IN SOURCES` is a valid result.
- Evidence is write-once; every draft claim needs a ledger row.
- The AI does the heavy reading; people keep the judgment — every verification row is signed off by a person.
