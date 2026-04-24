---
description: Step 7 — turn the latest iteration's findings into an ordered todo list
---

# Step 7 — plan

Convert the "Findings / suggestions" table in the latest iteration's
section of `eval/improvement-log.md` into a concrete, ordered Plan block.

Procedure:

1. Read the latest iteration's Findings block.
2. Pick an order that front-loads low-risk / high-volume changes. If
   two items overlap in surface, merge them.
3. Replace the `_(fill in)_` marker in the iteration's "Plan" block
   with:
   - A 1–2 sentence ordering rationale.
   - A Markdown todo checklist: `- [ ] <id>: <summary> — files touched`.
   - Include an explicit `- [ ] re-scan and `eval-jss iterate record
     post-<label>`` item as the final checkbox.
4. Use TaskCreate to mirror the checklist as in-session tasks so
   progress is tracked live.

Keep the plan under ~6 items. Anything bigger should be deferred to a
later iteration rather than attempted in one pass.

End your reply with the literal line: `Next: /eval-implement`
