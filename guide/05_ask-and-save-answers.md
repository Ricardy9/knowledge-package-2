# 05 Ask NotebookLM and save the answers

**Who:** all three. **Commands:** `/make-query-pack`, then `/save-answer`. This is the step you repeat most.

## A. Get today's questions
**Type `/make-query-pack`.** The AI guide picks the next 5–10 questions (most important first) and writes a query pack in `05_query-packs/`. For each question, the pack gives:
- the notebook to open;
- the exact prompt to paste, with your question already filled in;
- the file name the answer will be saved under.

## B. Ask NotebookLM
For each question in the pack, from top to bottom:
1. Open the notebook named in the pack.
2. Copy the prompt from the pack, paste it into the NotebookLM chat box, and press Enter.
3. **Check the answer.** Each evidence point should show "a quote in quotation marks", the source title and a page. If some points don't, paste prompt 02 (`prompts/notebooklm/02_citation-follow-up.md`) in the same chat.
4. **Copy the whole answer**, including all quotes and source lines (and the follow-up, if you used one).

## C. Save it
1. In Claude Code, type `/save-answer Q01` (with that question's number) and paste the answer.
2. The AI guide does three things:
   - saves the answer **word for word** in `06_answers/`;
   - adds each quoted finding to `07_evidence-log/evidence_log.csv`, with its source and page;
   - marks the question **Answered**, or **Needs follow-up** if the answer said NOT FOUND, had points without citations, or you tell it the answer was thin.
3. Move on to the next question in the pack.

## When the answer says NOT FOUND IN SOURCES
This is a real result: your documents do not cover that point. Options:
- add a document that does cover it (`/add-source`), upload it to the notebook, and ask again;
- reword the question if it was unclear;
- or accept the gap. It will be listed in your summary.

Never fill the gap from memory, or from an AI answer that has no source.

**Next:** `06_track-progress-and-summarize.md`
