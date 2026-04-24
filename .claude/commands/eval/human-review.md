---
description: Step 4 — interactively label uncertain / skip-listed violations
argument-hint: "[--rule JSS-XXX-NNN] [--limit N]"
---

# Step 4 — human review

`eval-jss human-review` is an interactive TUI — it has to be run by the
user directly in the terminal, not through me. Surface the invocation
and a short pre-flight report:

1. Count of rows with `verdict IS NULL` (unlabelled).
2. Count of rows with `verdict = 'uncertain'`.
3. Top 3 rules contributing to those pools.

Then print the command for the user to run:

```
eval-jss human-review $ARGUMENTS
```

(suggest `! eval-jss human-review` if they want it run inside this
session's shell).

Once they've finished labelling, the next step is record.

End your reply with the literal line: `Next: /eval:record <label>`
