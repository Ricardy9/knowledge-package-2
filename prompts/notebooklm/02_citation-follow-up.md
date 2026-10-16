# Prompt 02: Citation follow-up

**When to use:** when an answer from prompt 01 or 03 has points with no quote, no source title or no page number. NotebookLM sometimes shows sources only as small clickable numbers, and those numbers disappear when you copy the text.

**How:**
1. Stay in the same NotebookLM chat, straight after the answer.
2. Paste the prompt below and press Enter.
3. Copy **both** answers (the first one and this follow-up) and type `/save-answer` in Claude Code.

**The prompt to paste:**

```text
Some points in your previous answer do not show a source and page. For each of those points, give the exact quote and the source title, page and date it comes from. If a point cannot be traced to a source, say so and remove it.
```
