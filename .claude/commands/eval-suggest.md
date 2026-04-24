---
description: Step 6 — analyse the latest iteration and write candidate improvements into the log
---

# Step 6 — suggest improvements

Analyse the most recent iteration's violations and propose concrete rule
improvements. Write findings into the current iteration's
"Findings / suggestions" block in `eval/improvement-log.md`.

Procedure:

1. Read the tail of `eval/improvement-log.md` — find the latest
   `## Iteration N …` section.
2. Query `eval/eval.db` for the top rules by violation count (full and
   pinned scopes). Spot-check samples with `sqlite3`-style queries via
   the Bash tool.
3. For each high-volume rule, decide whether hits look like:
   - **rule bug** (the rule fires on input that violates no actual JSS
     norm — e.g., content already wrapped in markup, inline code spans,
     case-sensitivity mismatches). These are the leverage.
   - **corpus mismatch** (input isn't JSS-styled; hits are technically
     TPs). Note briefly; do not prioritize.
4. Rank candidates by (volume × confidence × patch size). Lowest-risk,
   highest-volume wins first.
5. Write a ranked table into the Findings block, replacing the
   `_(fill in)_` placeholder. Include: change summary, estimated
   volume affected, surface (files touched), risk level.
6. Do NOT fill in the Plan block — that's `/eval-plan`'s job.

Avoid proposing spec-level corpus or harness changes here unless they
directly affect rule precision. Focus on rule modules.

End your reply with the literal line: `Next: /eval-plan`
