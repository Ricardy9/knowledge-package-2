# NotebookLM plan

Create one NotebookLM notebook for each group of related sources. Focused notebooks give better answers than one notebook holding everything.

| Notebook name | Sources (ids from source_register.csv) | Questions it answers |
|---|---|---|
| Mexico displacement – Scale and causes | S01, S03, S04, S05 | Q01, Q02, Q03, Q04, Q05, Q06, Q10 |
| Mexico displacement – Groups, places and response | S02, S03, S05 | Q07, Q08, Q09 |

Sources S03 and S05 appear in both notebooks because they cover both topics.

**How to create them:**
1. Go to notebooklm.google.com and sign in.
2. Click **New notebook**.
3. Upload the listed PDFs from the `02_sources/` theme folders.
4. Rename the notebook to the name above.
5. Paste prompt 05 (`prompts/notebooklm/05_source-overview.md`) to check that every document was read.
