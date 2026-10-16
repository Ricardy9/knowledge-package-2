# 00 Overview: how the kit works

The kit turns a pile of documents into answers you can trust. Every finding points to a quote, a source and a page.

## The loop

| Step | Who | What happens | Command |
|---|---|---|---|
| 1. Set up | You + AI guide | You answer a few questions; the AI guide builds your project folder and research questions | `/setup` |
| 2. Add sources | You + AI guide | You put documents in the folders; the AI guide records each one | `/add-source` |
| 3. Plan notebooks | AI guide, then you | The AI guide says which documents go in which NotebookLM notebook; you create them | `/plan-notebooks` |
| 4. Ask | AI guide, you, NotebookLM | The AI guide prepares the questions and prompts; you paste them into NotebookLM | `/make-query-pack` |
| 5. Save | You + AI guide | You paste each answer back; the AI guide saves it word for word and logs the findings | `/save-answer` |
| Check progress | AI guide | A plain-language progress report | `/status` |
| Summarize (optional) | AI guide | A short summary built only from logged findings | `/draft` |

You repeat steps 4 and 5 until your questions are answered. You can add sources or questions at any time.

## Your project folder

Setup creates a folder for your project inside `projects/`:

| Folder | What it holds |
|---|---|
| `01_project-brief` | Your topic, period, audience and main questions |
| `02_sources` | Your documents (one subfolder per theme) and the list of sources |
| `03_questions` | Your research questions and their status |
| `04_notebooks` | Which documents go in which NotebookLM notebook |
| `05_query-packs` | Today's questions, with the exact prompts to paste |
| `06_answers` | NotebookLM's answers, saved word for word |
| `07_evidence-log` | Every finding, linked to its answer, source and page |
| `08_outputs` | Summaries |
| `09_archive` | Old versions (nothing is ever deleted) |

## Three rules
1. **Nothing is invented.** Every finding comes from your documents, with a quote and a page.
2. **Saved answers are never edited.** To correct one, ask again and save a new answer.
3. **"NOT FOUND IN SOURCES" is a result.** It tells you where evidence is missing, so you know what to look for next.

**Next:** `01_install-and-open.md`
