Prepare today's list of questions to ask NotebookLM, with the exact text to paste for each one. Follow `CLAUDE.md` rules throughout.

How many questions (optional): $ARGUMENTS

1. Find out which project (use the only one if there is just one).
2. From `03_questions/question_bank.csv`, pick the questions whose status is `Open` or `Needs follow-up`.
   - Take High priority first, then Medium, then Low.
   - Within the same priority, go in id order (Q01 before Q02).
   - Pick 5–10 questions, the number the user gave, or all that remain if fewer.
   - If none are left, say so and suggest `/status`.
3. Write `05_query-packs/YYYY-MM-DD_query-pack.md`, using today's date. Start it with this short "How to use this pack" box:
   1. Open NotebookLM.
   2. For each question below, open the notebook named, paste the prompt, and press Enter.
   3. Copy the whole answer.
   4. In Claude Code type `/save-answer Qnn` and paste it.

   Then, for each question:
   - a heading `## Qnn – <the question>`;
   - **Notebook:** the notebook name. If the `notebook` column is blank for any chosen question, stop and ask the user to run `/plan-notebooks` first;
   - **Prompt:** 01 (`prompts/notebooklm/01_answer-a-question.md`) normally, or 03 (`prompts/notebooklm/03_still-true-check.md`) if `still_true_check` is `yes`;
   - the prompt text from `prompts/notebooklm/01_answer-a-question.md` or `03_still-true-check.md`, inside a `text` code block, with every `[BRACKETED]` field filled in:
     - [QUESTION] is the question;
     - [EARLIER FINDING] is the text after `Earlier finding:` in `notes`;
     - [PERIOD START] is `period_start`;
   - **Save as:** `06_answers/YYYY-MM-DD_Qnn_<three-to-five-word-slug>.md`.
4. Set the status of the questions in the pack to `Asked` in `question_bank.csv`.
5. Tell the user, in plain words, to work through the pack from top to bottom.

List every file you created or changed. End with a **Next step:** line, for example: open the pack, ask Q01 in NotebookLM, then type `/save-answer Q01`.
