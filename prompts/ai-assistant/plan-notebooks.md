> **If your AI tool has no slash commands** (for example Codex or Copilot), paste the text below into it, then answer its questions. Where it says `$ARGUMENTS`, it means anything you typed after the request.

Plan which documents go into which NotebookLM notebook. Follow `CLAUDE.md` rules throughout.

1. Find out which project (use the only one if there is just one).
2. Read `02_sources/source_register.csv` and `03_questions/question_bank.csv`.
3. Group the sources into 1–4 focused notebooks.
   - Group by theme, or by the questions they answer.
   - Smaller, focused notebooks give better answers than one notebook with everything. NotebookLM also limits how many sources a notebook can hold.
   - Name each one `<project name> – <theme or question group>`.
4. Show the proposal as a table (notebook name, source ids, question ids) and let the user change it.
5. Once agreed:
   - write `04_notebooks/notebook_plan.md` using the table in that file;
   - fill the `notebook` column of `question_bank.csv` with each question's notebook name.
6. Give the user these exact steps for each notebook:
   1. Go to notebooklm.google.com and sign in with a Google account.
   2. Click **New notebook** (or **Create new**).
   3. Upload the files listed for that notebook from the `02_sources/` theme folders. For link-only sources, add the website link instead.
   4. Rename the notebook to the name in the plan.
   5. Paste prompt 05 (`prompts/notebooklm/05_source-overview.md`) and check that every document appears.

List every file you created or changed. End with a **Next step:** line. Usually this is: once your notebooks are ready, type `/make-query-pack`.
