---
description: Step 5 — snapshot full + pinned stats into precision-history.db and improvement-log.md
argument-hint: "<label> [--note TEXT]"
---

# Step 5 — record the iteration

Invoke:

```bash
source .venv/bin/activate
eval-jss iterate record $ARGUMENTS
```

This computes the precision report twice (full corpus and
`--pinned-only`), inserts a row into `eval/precision-history.db`, and
appends a templated section to `eval/improvement-log.md`.

After the run:

1. Read the tail of `eval/improvement-log.md` to confirm the new section
   landed.
2. If this is a post-implementation snapshot (label starts with
   `post-`), eyeball the "Delta vs. previous iteration" block and call
   out which rules moved most.

Refuse to run if `$ARGUMENTS` is empty — a label is required.

End your reply with one of:

- `Next: /eval:suggest` — if this was a pre-change / baseline record.
- `Next: /eval:add-corpus` — if this was a `post-<label>` record and the
  loop has closed; the next iteration starts by growing the corpus.
