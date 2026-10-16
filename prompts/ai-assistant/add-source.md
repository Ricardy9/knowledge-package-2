> **If your AI tool has no slash commands** (for example Codex or Copilot), paste the text below into it, then answer its questions. Where it says `$ARGUMENTS`, it means anything you typed after the request. (This copy is generated from `.claude/commands/`; edit that file, not this one.)

Record one or more documents in the project's source register. Follow `CLAUDE.md` rules throughout.

Details given with the command: $ARGUMENTS

1. Find out which project. If only one folder exists in `projects/`, use it and say so; otherwise ask.
2. Find the new documents:
   - look in `projects/<name>/02_sources/` (all theme subfolders) for files that are not yet listed in `source_register.csv`;
   - also take any file names or links the user gives.
3. For each new document, gather the details, reading them from the file's first page where possible:
   - title, author or organisation, year;
   - type (report / article / dataset / web page / other);
   - theme (one of the subfolders);
   - the link where it can be found online.
   Show what you found and ask the user to confirm or correct it. Never invent a link; leave it blank if unknown.
4. Give each document the next id (S01, S02…) and add a row to `02_sources/source_register.csv`:
   - `file_name` is the file's name inside its theme folder, or blank for a link-only source;
   - put any note in `notes` (for example "scanned – may not read well").
5. If a document is not in a theme folder yet, tell the user which folder to move it into.
6. Remind the user once: PDFs must contain selectable text (try highlighting a word in the PDF; if you can't, it is a scanned image).

List every file you created or changed. End with a **Next step:** line. Usually this is: when all your documents are recorded, type `/plan-notebooks`.
