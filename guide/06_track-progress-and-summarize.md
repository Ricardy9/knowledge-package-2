# 06 Track progress and write a summary

**Who:** the AI guide, checked by you. **Commands:** `/status`, `/draft`.

## See where you are
**Type `/status`.** In plain words, you see:
- how many questions are open, waiting, answered or need follow-up;
- why each follow-up is needed;
- how many findings are logged, and which sources haven't been used yet;
- the single most useful next step.

`/status` never changes your files. Use it whenever you come back to the project.

## Write a working summary (optional)
**Type `/draft`** when most questions are answered. The AI guide writes `08_outputs/<date>_summary.md`:
- a short answer to each main question, where every sentence ends with the finding ids it rests on, for example (F003, F007);
- a **Gaps** section listing what the evidence does not cover;
- the sources used.

It uses **only** the findings in your evidence log, never outside knowledge.

## Before you share anything
Check each finding id the summary cites:
1. find the row in `07_evidence-log/evidence_log.csv`;
2. open its answer file in `06_answers/`;
3. if needed, open the source at the page given.

The kit makes checking easy; checking is still your job.

**Next:** if something goes wrong, see `07_troubleshooting.md`.
