# Prompt 04: Coverage check

**When to use:** every few rounds, to find important topics your questions may be missing. Its results are ideas for new questions, never evidence. Do not cite them.

**How:**
1. Open a NotebookLM notebook.
2. In Claude Code, ask: "List my open and answered questions so I can paste them." Copy that list.
3. Paste the prompt below into NotebookLM, putting your question list where it says, and press Enter.
4. Show the suggestions to Claude Code and say which ones to add to the question bank. Saving a suggestion as a new question is fine. It must still be answered with prompt 01 before it counts as evidence.

**The prompt to paste:**

```text
Here are the questions we are researching:
[PASTE THE QUESTION LIST]

Based on the sources in this notebook, what important topics do these questions miss?
For each, give: MISSING TOPIC / WHY IT MATTERS (with a quote and source) / SUGGESTED NEW QUESTION.
These are suggestions only.
```
