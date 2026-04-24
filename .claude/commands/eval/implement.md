---
description: Step 8 — implement the planned improvements for the current iteration
---

# Step 8 — implement

Work through the Plan checklist in the latest iteration's section of
`eval/improvement-log.md`. For each item:

1. Read the referenced file(s); confirm the change locus.
2. Apply the smallest diff that achieves the fix.
3. Run the affected tests; if a rule module changed, run
   `pytest tests/texlint -q` for smoke coverage and
   `pytest tests -q` for the full suite before checking the box.
4. Mark the corresponding item complete via TaskUpdate and update the
   `- [x]` marker in the log.

Constraints:

- Do not touch `src/texlint/core/` or `src/texlint/api.py` unless the
  Plan explicitly authorizes it (Constitution §IV).
- Keep catalogue metadata (`specs/003-jss-rule-catalogue/catalogue.yaml`)
  in sync with any message/severity changes.
- Do not commit; the user will review and commit deliberately.

When the checklist is done, move on to rescanning.

End your reply with the literal line: `Next: /eval:rescan <label>` (using
the same label as the pre-change record).
