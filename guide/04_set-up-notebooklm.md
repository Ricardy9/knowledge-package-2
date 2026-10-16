# 04 Set up NotebookLM

**Who:** the AI guide plans, you create the notebooks. **Command:** `/plan-notebooks`.

NotebookLM is a free Google tool that answers questions using only the documents you upload, and shows where each answer comes from.

1. **Type `/plan-notebooks`.** The AI guide proposes 1–4 notebooks, each holding a focused group of documents, and says which questions each notebook will answer. Agree or ask for changes. It saves the plan in `04_notebooks/notebook_plan.md`.

   Why several notebooks? A notebook with fewer, related documents gives more precise answers than one with everything.
2. **Create each notebook.** Do this for every notebook in the plan:
   1. Go to notebooklm.google.com and sign in with your Google account.
   2. Click **New notebook** (or **Create new**).
   3. Upload the files listed in the plan from your `02_sources/` theme folders. For web-only sources, add the link.
   4. Rename the notebook to the name in the plan, so you can find it later.
3. **Check each notebook.** Paste the prompt from `prompts/notebooklm/05_source-overview.md` into the notebook. Every document you uploaded should appear in the reply. If one is missing or garbled, re-upload it or find a text version.

**Next:** `05_ask-and-save-answers.md`
