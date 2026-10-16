# Prompt 03: "Is this still true?" check

**When to use:** when a question asks whether an earlier finding still holds. These questions are marked `still_true_check = yes` in the question bank, and the query pack tells you when to use this prompt. It stops an answer from relying only on old sources.

**How:**
1. Open the NotebookLM notebook named in the query pack.
2. Copy the prompt from the query pack. The earlier finding and the start date are already filled in.
3. Paste it into NotebookLM and press Enter.
4. Copy the whole answer and type `/save-answer` in Claude Code.

**The prompt to paste:**

```text
An earlier finding said: "[EARLIER FINDING]"

Using ONLY sources in this notebook dated [PERIOD START] or later, does this still hold?
Answer one of: STILL HOLDS / HAS CHANGED / NOT ENOUGH RECENT EVIDENCE.
Then give the evidence: "exact quote" — source title, page, date.
Do not use any source dated before [PERIOD START] to support the answer.
```
