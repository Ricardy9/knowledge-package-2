# Prompt 01: Answer a research question

**When to use:** for every research question in your query pack, unless the pack says to use prompt 03.

**How:**
1. Open the NotebookLM notebook named in the query pack.
2. Copy the prompt below. The query pack already has it filled in for each question, so copy it from there.
3. Paste it into the NotebookLM chat box and press Enter.
4. Check that every evidence point shows a quote and a source. If some don't, use prompt 02 in the same chat.
5. Copy the **whole** answer and type `/save-answer` in Claude Code.

**The prompt to paste:**

```text
Answer the research question below using ONLY the sources in this notebook.

QUESTION: [QUESTION]

Rules:
1. Use only these sources. Do not use outside knowledge.
2. For every point, quote the exact words from the source in quotation marks, then give the source title and page number.
3. If the sources do not answer the question, write exactly: NOT FOUND IN SOURCES.
4. If sources disagree, show each version and say which source says what.
5. For each source you use, state its publication date.
6. Do not round numbers, merge figures from different sources, or add context that is not in the sources.

Format:
ANSWER: a short answer in 2-4 sentences.
EVIDENCE: bullet points, each with "exact quote" — source title, page, date.
GAPS: what the sources do not cover.
```
