# Worked example: forced displacement in Mexico

This folder shows a project set up exactly as `/setup` and the other commands would build it. Use it as a model for your own project, or try the whole workflow on it.

## What is filled in

| Step | File | Status |
|---|---|---|
| Project brief | `01_project-brief/project_profile.md` | Done |
| Sources | `02_sources/source_register.csv` | 5 real English documents, every link checked on 2026-10-16 |
| Questions | `03_questions/question_bank.csv` | 10 questions, each about one checkable thing |
| Notebooks | `04_notebooks/notebook_plan.md` | 2 notebooks planned |
| Query pack | `05_query-packs/2026-10-16_query-pack.md` | 3 questions with ready-to-paste prompts |
| Answers and evidence | `06_answers/`, `07_evidence-log/` | **Empty on purpose.** No answers are made up; you produce them by running the query pack |

## Try it yourself (about 30 minutes)
1. **Download the five sources.** Open `02_sources/source_register.csv` (in Excel, or ask the AI guide to show it), open each link, and save each PDF into the theme folder named in its `notes`.
2. **Create the two notebooks** in NotebookLM, as described in `04_notebooks/notebook_plan.md`.
3. **Run the query pack.** Open `05_query-packs/2026-10-16_query-pack.md` and paste each prompt into the named notebook.
4. **Save each answer.** In Claude Code, type `/save-answer Q01` and paste NotebookLM's answer, then do the same for the other questions. Before saving, ask the AI guide to work on a copy: "copy the Mexico example into projects/ as mexico-practice". That keeps this example clean.
5. **Type `/status`** to see progress.

## About the sources
- S02 and S05 are copies hosted on ecoi.net, a well-known archive of country information, because the original pages could not be reached directly.
- S01 is a global report: Mexico is one country among many in it.
- S03 was originally written in Spanish; the link is the official English version.
