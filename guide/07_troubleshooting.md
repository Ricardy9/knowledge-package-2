# 07 Troubleshooting

| Problem | What to do |
|---|---|
| Typing `/setup` does nothing, or "command not found" | Claude Code is probably open on the wrong folder. Open the kit folder itself, the one that contains `START_HERE.md`. You can also just type "start the setup". |
| The AI guide doesn't offer setup | Type `/setup`, or say "please run the setup from CLAUDE.md". |
| NotebookLM won't accept a file | The file may be too large, password-protected or an unusual format. Try a PDF version, or split a very large file. |
| A document appears empty or garbled in NotebookLM | It is probably a scanned image. Look for a text version (try highlighting a word in the PDF). |
| The answer has no page numbers or sources | Paste prompt 02 (`prompts/notebooklm/02_citation-follow-up.md`) in the same NotebookLM chat, then save both answers. |
| "The AI guide changed my saved answer" | It must never do that. Ask it to put back the original from `09_archive/` if it is there, and tell it: "follow rule 2 in CLAUDE.md". |
| A CSV file looks jumbled in Excel | Open Excel first, then use **Data → From Text/CSV**, choose the file and pick UTF-8. |
| I want a second project | Type `/setup` again with a different project name. Each project has its own folder in `projects/`. |
| I want to restart a project | Ask the AI guide to move the project folder into an archive. Nothing is deleted. |
| Can I use an AI tool other than Claude Code? | Yes. Open the kit folder in that tool and ask it to follow `CLAUDE.md`, then say what you want to do (for example "run the setup"). |
