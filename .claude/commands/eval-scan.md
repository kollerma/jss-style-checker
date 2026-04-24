---
description: Step 2 — scan the corpus with jss-lint and persist violations
---

# Step 2 — scan

Run the linter over the corpus and repopulate `eval/eval.db`:

```bash
source .venv/bin/activate
eval-jss scan --corpus examples/ --force
```

Then summarize:

- total violations persisted
- top 8 rules by count (full corpus)
- top 3 papers by violation count
- parse failures (JSS-PARSE-000), grouped by `.Rnw` / `.Rmd` / `.bib`

If any papers are marked `scan_failed`, list them with the parse error
message.

End your reply with the literal line: `Next: /eval-review`
