> **If your AI tool has no slash commands** (for example Codex or Copilot), paste the text below into it, then answer its questions. Where it says `$ARGUMENTS`, it means anything you typed after the request.

Run the guided setup for a new research project. Follow `CLAUDE.md` rules throughout.

Ask the questions below one at a time and wait for each answer. For each one:
- say in one sentence why it matters;
- offer the matching line from `example-mexico-displacement/01_project-brief/project_profile.md` as an example.

1. Ask for a short project name: lowercase words joined by hyphens, for example `mexico-displacement`. If `projects/<name>/` already exists, ask for another name.
2. Ask what the project is about, in one or two sentences.
3. Ask what period it should cover (start year and end year).
4. Ask who will read the results, and what decision the results will help them make.
5. Ask for 3–5 main research questions.
6. Propose 3–5 themes to group the sources by, based on the topic, and let the user edit them.
7. Ask whether they already have documents, or want help finding a starter list.
   - If they want help, suggest only well-known kinds of sources to look for: UN agencies, research institutes, national statistics offices, human-rights organisations.
   - Say what kind of document to look for (annual report, country profile, official statistics).
   - Never give a link you have not opened and checked.

Then build the workspace:
- Copy everything in `project-template/` to `projects/<name>/` (all folders, READMEs and CSV files).
- Fill `projects/<name>/01_project-brief/project_profile.md` with the answers and today's date.
- Create one subfolder per theme inside `projects/<name>/02_sources/`, named in lowercase with hyphens.
- Break each main question into 2–4 specific questions. Each must ask about exactly ONE thing that a source could confirm or deny.
- For any question that asks whether something from earlier work "is still true":
  - set `still_true_check` to `yes` and `period_start` to the start of the period;
  - write the earlier finding in `notes` as `Earlier finding: "..."`, in the user's own words;
  - never write a finding you made up.
- Show the list of specific questions. Let the user add, remove or reword them.
- Save the agreed list to `03_questions/question_bank.csv`, with ids Q01, Q02…, status `Open`, and a priority (High / Medium / Low) the user agrees.

Finish with a short checklist:
- **Ready now:** the project folder, the profile, the theme folders, the question bank.
- **Your next job:** put your documents (PDFs with selectable text) into the theme folders inside `projects/<name>/02_sources/`.
- **Then type:** `/add-source` to record them.
- **Guide to read:** `guide/03_add-your-sources.md`.

List every file you created. End with a **Next step:** line.
