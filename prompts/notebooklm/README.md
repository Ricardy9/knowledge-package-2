# NotebookLM prompts

These are ready-made texts you paste into NotebookLM (notebooklm.google.com) so that its answers stick to your sources and always show where each point comes from.

You rarely need to open these files yourself. When you type `/make-query-pack`, the AI guide copies the right prompt into the query pack with your question already filled in.

| Prompt | Use it when |
|---|---|
| [01 Answer a research question](01_answer-a-question.md) | For each question in your query pack (most of the time) |
| [02 Citation follow-up](02_citation-follow-up.md) | An answer has points without a quote, source or page |
| [03 "Is this still true?" check](03_still-true-check.md) | The question asks whether an earlier finding still holds |
| [04 Coverage check](04_coverage-check.md) | Every few rounds, to spot missing topics (ideas only, never evidence) |
| [05 Source overview](05_source-overview.md) | Once, right after creating a notebook |

**Three tips**
1. Copy the **whole** answer, including every quote and source line, before typing `/save-answer`.
2. If the sources show only as small clickable numbers, run prompt 02 so they appear as text.
3. "NOT FOUND IN SOURCES" is a useful result. It tells you where the evidence is missing. Never fill that gap from memory.
