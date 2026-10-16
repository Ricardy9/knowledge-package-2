# 03 Add your sources

**Who:** you add the files, the AI guide records them. **Command:** `/add-source`.

1. **Collect your documents.** Reports, articles, official statistics, PDFs or Word files.
2. **Check that each PDF has real text.** Open it and try to highlight a word with your mouse. If you can, it is fine. If you can't, it is a scanned image: look for a text version, or expect NotebookLM to read it poorly.
3. **Put each file in its theme folder.** For example, put a report on violence in `projects/<your project>/02_sources/causes/`. Use your computer's normal file windows (File Explorer or Finder).
4. **Type `/add-source`.** The AI guide finds the new files, reads each one's title, author and year from its first page, and asks you to confirm. It gives each one an id (S01, S02…) and records it in `02_sources/source_register.csv`.

   You can also record a web page without a file: type `/add-source` followed by the link.

## The source register, column by column

| Column | Meaning |
|---|---|
| id | S01, S02… used everywhere else to point to this source |
| title, author_or_org, year | What the document is |
| type | report, article, dataset, web page or other |
| theme | Which theme folder it belongs to |
| link | Where it can be found online (left blank if unknown, never guessed) |
| file_name | The file's name in its theme folder (blank for web-only sources) |
| notes | Anything worth knowing, for example "scanned" |

**Tip:** CSV files open in Excel. If the columns look jumbled, open Excel first and use **Data → From Text/CSV**, choosing UTF-8.

**Next:** `04_set-up-notebooklm.md`
