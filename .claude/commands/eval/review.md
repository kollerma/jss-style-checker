---
description: Step 3 — run the AI classifier over unlabelled violations
argument-hint: "[--limit N] [--confidence-threshold 0.8]"
---

# Step 3 — AI classifier

Hand unlabelled rows to the local LLM for verdict labelling:

```bash
source .venv/bin/activate
eval-jss review $ARGUMENTS
```

Default confidence threshold is 0.8 (labels below that remain `uncertain`
for human review). Default model + base URL live in `eval/cli.py`.

After the run, report:

- rows labelled by the AI (TP / FP / uncertain counts)
- any rules excluded via `eval/review-skip-list.toml`
- remaining unlabelled count

If the LLM endpoint is unreachable, print the error and suggest the user
start their local model (or skip to `/eval:human-review`).

End your reply with one of:

- `Next: /eval:human-review` — if any `uncertain` or unlabelled rows remain.
- `Next: /eval:record <label>` — if the review is complete.
