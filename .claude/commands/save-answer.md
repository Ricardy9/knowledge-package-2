Save a NotebookLM answer word for word, and record its findings in the evidence log. Follow `CLAUDE.md` rules throughout. This step must never change the answer's wording.

Question id given with the command (optional): $ARGUMENTS

1. Find out which project (use the only one if there is just one) and which question id (for example Q03). If no id was given, ask.
2. Ask the user to paste the **complete** NotebookLM answer, including every quote and source line. Wait for it.
3. Save it to `06_answers/`, using the file name given in the latest query pack for that question. If there is none, use `YYYY-MM-DD_Qnn_<three-to-five-word-slug>.md`. The file contains:

   ```
   # Qnn – <the question>
   - Notebook: <notebook name>
   - Saved on: <today's date>

   --- answer pasted below, unedited ---

   <the answer exactly as pasted>
   ```

   If a file with that name exists, never overwrite it. Add `-2`, `-3`… to the new file's name.
4. Read the saved answer. Add one row to `07_evidence-log/evidence_log.csv` for each evidence point that has a quote AND a source:
   - `finding_id`: the next free id (F001, F002…);
   - `question_id`: the question;
   - `finding`: a one-sentence statement of what the quote shows, staying close to its words;
   - `answer_file`: the file name you just saved;
   - `source_id`: the S-id from `02_sources/source_register.csv` whose title matches the cited source. If none matches, leave it blank and put `source not in register: <title as cited>` in `notes`;
   - `page`: the page exactly as the answer gives it, blank if none;
   - `confidence`:
     - `High` if the quote states the point directly;
     - `Medium` if it supports it less directly;
     - `Low` if it is unclear.

   Points without a quote and a source get no row. If a finding contains double quotes, double them inside the CSV value (`""`). Never add a finding that is not in the pasted answer.
5. Update the question's status in `question_bank.csv`:
   - set it to `Needs follow-up` if any of these applies:
     - the answer says NOT FOUND IN SOURCES;
     - some points have no quote, source or page (also suggest prompt 02, `prompts/notebooklm/02_citation-follow-up.md`);
     - the user says it is thin;
   - otherwise set it to `Answered`.
6. Report in plain words: the file saved, how many findings were added, and the new status.

List every file you created or changed. End with a **Next step:** line, usually the next question in the query pack.
