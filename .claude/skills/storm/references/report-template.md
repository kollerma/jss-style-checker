# Report template

Write `report.md` in this exact shape. Keep prose tight; every non-obvious claim
gets an inline `[n]` citation keyed to `sources.md`.

```
# {{Topic}} — research briefing

## Reliability notes
- Overall confidence: {{low / medium / high}} — one line on why.
- Weakest claim: {{the single least-supported claim}} → would be confirmed by
  {{what evidence}}.
- Possible bias: {{any perspective that ended up over-weighted, or "none
  significant"}}.
- Open gap: {{what none of the perspectives covered}}.

## Bottom line  (~150 words)
A briefing for someone with 60 seconds who needs the nuance, not just the
headline: what's true, what's contested, what it means.

## Key findings
A ranked list, most to least reliable. For each: the finding in one or two
sentences with citations [n], plus a tag for which perspectives support it and
which push back. The ranking is the point — don't bury a shaky finding next to a
solid one without flagging it.

## Where the experts disagree
The live contradictions from contradictions.md, with the clashing claims and
which side currently has the stronger evidence, and why.

## What everyone agrees on
The points every perspective confirmed — the load-bearing, likely-true core.

## The non-obvious connection
One link between findings that only shows up when all perspectives are on the
table at once.

## So what — for {{role / audience, or "a smart generalist"}}
The specific thing this person should do or watch differently given the evidence.
Concrete, not "consider exploring".

## The frontier question
The single open question that, if answered, would most change how we understand
this topic.
```

## Citation rules

- Use only `[n]` numbers that exist in `sources.md`. Never invent one.
- Put the citation immediately after the claim it supports.
- If two sources back a claim, `[n][m]` is fine.
- A paragraph with zero citations should be either obviously general knowledge or
  removed.
