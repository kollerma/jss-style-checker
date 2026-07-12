---
name: storm
description: Run rigorous, citation-grounded research on a topic using the STORM method — survey the landscape, derive several genuine expert perspectives, interview each one grounded in live web search, map where they conflict, then write a sourced briefing and peer-review it. Use this whenever the user wants to "research", "do a deep dive on", "write a briefing / report / backgrounder on", "understand all sides of", "get up to speed on", or "prep for" something on a topic and expects sourced, multi-angle output rather than a quick answer — even if they never say the word "STORM". Do NOT use it for single-fact lookups or quick definitions; those don't need the pipeline.
---

# STORM — multi-perspective, retrieval-grounded research

This skill reproduces the method behind Stanford OVAL's STORM (Synthesis of Topic
Outlines through Retrieval and Multi-perspective Question Asking) inside Claude's
own agent loop. STORM's core insight is that the hard part of research is *asking
good questions*, and you get good questions by (1) attacking a topic from several
genuine, discovered perspectives and (2) grounding every answer in real sources.
`references/method.md` has the full mapping to the paper — read it if a situation
isn't covered here.

## The one rule that makes this STORM and not a vibe

**Every expert answer and every claim in the final report must be grounded in a
real source retrieved with web_search / web_fetch, and that source must be
recorded.** The moment an "expert" answers from memory, you've rebuilt exactly the
thing STORM was designed to beat: fluent, confident, unsourced text. If you can't
find a source for a claim, cut the claim or go find one.

## Inputs

- **topic** (required) — what to research.
- **role / audience** (optional) — who the briefing is for; sharpens the
  "actionable insight" at the end. Infer it if it's not given and obvious; only
  ask if it's quick and would change the output.
- **depth** (optional) — how many perspectives, default 5, sensible range 3–6.

## Workflow

All intermediate files live in `storm-runs/<slug>/`. Scaffold the run with the
bundled helper (path is relative to this skill's folder; use its full path if
your working directory is elsewhere):

```bash
python3 scripts/storm_run.py init "<topic>"
```

It prints the run paths (`run_dir`, `raw_dir`, …) as JSON. Use those paths for
everything below.

### 1 — Survey & discover perspectives
Run 2–3 broad searches to get the lay of the land (overviews, the major debates,
who the stakeholders are). From what the sources *actually* show, derive `depth`
**distinct** perspectives. Do not hardcode a stock cast — the paper's move is to
let real coverage reveal the angles. A perspective is a lens with a stake: e.g.
for "Ozempic for weight loss" you might land on a prescribing endocrinologist, a
health-insurance actuary, a fat-acceptance researcher, a supply-chain analyst,
and a long-term-safety pharmacologist — not a generic "practitioner / skeptic /
economist". Write them to `perspectives.md`: each with a one-line lens and why it
sees something the others miss.

### 2 — Grounded interviews (the core)
For each perspective, run a short simulated interview (3–5 turns): the perspective
asks a pointed question, and a researcher answers **only** from web_search /
web_fetch results, logging sources as it goes. Each follow-up question should
react to what the previous answer surfaced — that reactive threading is where
depth comes from.

Hand each interview to a subagent so they run in parallel (see **Fan-out** below).
Give each subagent the brief in `references/interviewer.md` with the topic, the
single perspective, and the run paths filled in. Each subagent writes:
- prose findings → `storm-runs/<slug>/raw/<perspective-slug>.notes.md`
- one source per line → `storm-runs/<slug>/raw/<perspective-slug>.sources.tsv`,
  formatted `URL<TAB>Title`

Separate files per perspective means no write contention during the fan-out.

### 3 — Merge sources, then map contradictions
Number every source once, deterministically:

```bash
python3 scripts/storm_run.py merge storm-runs/<slug>
```

This writes the deduped, numbered `sources.md` and prints a `url → [n]` map — use
those numbers as your citation keys from here on.

Then read all the `raw/*.notes.md` and write `contradictions.md`: where do two or
more perspectives directly clash (quote the clashing claims)? What does *every*
perspective agree on (likely true — even opponents confirm it)? What did *none* of
them address (the blind spot — often the most valuable finding)?

### 4 — Outline
From the notes plus the contradiction map, write a hierarchical `outline.md`.
Organize by theme, not by perspective — the perspectives are inputs, not sections.

### 5 — Draft, grounded
Write `report.md` section by section following the outline and the structure in
`references/report-template.md`. Every non-obvious claim carries an inline `[n]`
citation keyed to `sources.md`. A sentence with no `[n]` should be either
self-evidently general or cut. Only use citation numbers that actually exist in
`sources.md` — never invent one.

### 6 — Peer review (verification, not flattery)
Re-read `report.md` against `sources.md` and do an honest self-review: a
confidence score (1–10) for each key finding with a reason, the single weakest
claim and what would verify it, any perspective that ended up over-weighted, and
any 6th angle that would change the conclusions. Fix what you can immediately;
surface the rest in the **Reliability notes** block at the top of the report. The
template shows the exact format. This step exists because STORM's own authors
flag that the method can suffer source bias and fact-misassociation — the review
is a check against the recorded sources, not a confidence-boosting summary.

## Fan-out (parallel interviews)

If subagents are available (e.g. Claude Code's Task tool), launch one interview
subagent per perspective in a single batch, each with the
`references/interviewer.md` brief. That parallelism is what makes a 5-perspective
run fast.

If subagents are **not** available (e.g. a plain chat surface), run the interviews
yourself, one perspective at a time, in the same session — the file layout and the
rest of the pipeline are identical.

## Final output

Give the user `report.md` (with citations and the Reliability notes block) plus a
3–4 line plain-language summary of how solid the findings are and where the gaps
remain. Mention the intermediate files (`perspectives.md`, `contradictions.md`,
`sources.md`, `raw/`) are there if they want to audit the trail. Don't paste a
long report into chat — point them to the file and summarize.

## Reference files
- `references/method.md` — how each step maps to the STORM / Co-STORM papers and
  why the design choices matter.
- `references/interviewer.md` — the brief to hand each interview subagent.
- `references/report-template.md` — the exact report structure, citation style,
  and Reliability-notes format.
