---
description: Step 9 — re-scan, re-record the iteration, and summarize the delta
argument-hint: "<same label as the pre-change record; 'post-' prefix is added automatically>"
---

# Step 9 — re-scan and close the iteration

Pre-change label: `$ARGUMENTS` (required). If empty, abort and ask.

Run:

```bash
source .venv/bin/activate
eval-jss scan --corpus examples/ --force
eval-jss iterate record post-$ARGUMENTS --note "Post-implementation snapshot for iteration labelled $ARGUMENTS"
```

After the record:

1. Read the tail of `eval/improvement-log.md` to pull the new section's
   "Delta vs. previous iteration" block.
2. Summarize: which rules saw the biggest reductions, whether any rule
   regressed, and the net change in pending / TP / FP totals.
3. Append a concise "Results" note to the PRE-change iteration's
   "Results (post-implementation)" block, pointing at the post- section
   and naming the two or three most notable deltas.

If a rule regressed (pending count went up without a corresponding rise
in TPs), flag it explicitly — this usually signals a new false-positive
pattern that needs attention next iteration.

The loop is closed.

End your reply with the literal line: `Next: /eval:add-corpus` (to start
iteration N+1).
