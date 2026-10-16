> **If your AI tool has no slash commands** (for example Codex or Copilot), paste the text below into it, then answer its questions. Where it says `$ARGUMENTS`, it means anything you typed after the request.

Show the project's progress in plain language. This step changes no files.

1. Find out which project (use the only one if there is just one).
2. Read `03_questions/question_bank.csv`, `07_evidence-log/evidence_log.csv`, `02_sources/source_register.csv` and the folder `05_query-packs/`.
3. Report briefly:
   - **Questions:** how many there are in total, and how many are Open, Asked, Answered, Needs follow-up and Closed.
   - **Waiting for NotebookLM:** the questions with status Asked, and the query pack they are in.
   - **Needs follow-up:** each question with one line on why. Read its answer file to tell whether it was NOT FOUND or missing citations.
   - **Evidence:** the number of findings, and the sources with no findings yet.
   - **The single most useful next step:**
     - `/save-answer` if questions are Asked;
     - `/make-query-pack` if questions are Open;
     - prompt 02 or a new source if questions need follow-up;
     - `/draft` if most questions are Answered.

End with a **Next step:** line.
