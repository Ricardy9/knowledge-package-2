# Prompt 05: Source overview

**When to use:** once, right after you create a notebook and upload its documents. It shows what each document covers and confirms that NotebookLM can read them all. A document that comes back empty or garbled is usually a scanned image.

**How:**
1. Open the new notebook in NotebookLM.
2. Paste the prompt below and press Enter.
3. Check that every document you uploaded appears in the list. If one is missing or looks wrong, re-upload it or find a text version.
4. Optional: paste the result into Claude Code and ask it to save it in `04_notebooks/`.

**The prompt to paste:**

```text
For each source in this notebook, list: title, author or organization, publication date, the period it covers, and the 3-5 main topics it covers (one line each). Do not summarize findings.
```
