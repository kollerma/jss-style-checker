# How this maps to Stanford STORM

This skill is a faithful re-implementation of the *method* in Stanford OVAL's
STORM, adapted to run inside Claude's agent loop instead of the original DSPy
pipeline. This file explains what the real system does and why each step here
mirrors it, so you can make good judgment calls when a situation isn't covered by
SKILL.md.

## What STORM actually is

STORM = **Synthesis of Topic Outlines through Retrieval and Multi-perspective
Question Asking** (Shao et al., NAACL 2024). It writes Wikipedia-style articles
with citations, from scratch, grounded in internet search. Its central claim is
that the bottleneck in automated research is *asking good questions*, and that
naively prompting a model to "ask questions about X" produces shallow ones.

It improves question quality two ways:

1. **Perspective-guided question asking.** Before researching, STORM surveys
   existing articles on related topics to discover the *perspectives* from which
   the topic tends to be covered, then uses those perspectives to drive question
   generation. → Stage 1 here: survey first, then derive perspectives from what
   coverage actually shows — not a fixed cast.

2. **Simulated conversation.** For each perspective, STORM simulates a multi-turn
   conversation between a "writer" (who asks) and a "topic expert" (who answers
   **grounded in retrieved sources**). The writer updates its understanding and
   asks follow-ups. → Stage 2 here: grounded interviews whose follow-ups react to
   what the last answer surfaced.

STORM then runs in **two stages**:
- **Pre-writing:** research (the conversations above) + outline generation.
- **Writing:** populate the outline into a full article with citations, then
  polish.

→ Stages 3–5 here: merge/contradictions → outline → grounded draft.

## What we add from Co-STORM and from a known weakness

- **Contradiction map (Stage 3).** Co-STORM (Jiang et al., EMNLP 2024) centers on
  surfacing where sources and agents *disagree* and what hasn't been covered
  ("unknown unknowns"). Mapping clashes, unanimous agreement, and untouched gaps
  is the highest-signal step — and the one casual research skips.

- **Peer review (Stage 6).** STORM's own authors note the system can suffer from
  source bias and fact-misassociation and does not self-critique. The explicit
  verification pass exists to catch exactly that. It is a check against the
  recorded sources, not a confidence-boosting recap.

## The grounding principle, restated

The original system's "topic expert" can only answer from retrieved passages.
That constraint is the whole point. In this re-implementation the equivalent
constraint is: interviewers and the drafter answer only from web_search /
web_fetch results, and every source is written down so citations are real and
checkable. If you ever catch yourself filling in a claim from background
knowledge, that's the signal to search instead.

## Things the real system does that we deliberately keep lightweight

- STORM dedupes and clusters retrieved information heavily; here we keep a simple
  deduped, numbered source list (`storm_run.py merge`) and rely on the drafter's
  judgment.
- STORM/Co-STORM maintain a structured "mind map" of concepts for long sessions.
  We use the outline + contradiction map for the same purpose at smaller scale.
- If you need the full validated pipeline, reproducible benchmarks, or the
  interactive Co-STORM roundtable, use the `knowledge-storm` Python package
  directly (`pip install knowledge-storm`). This skill trades that machinery for
  speed, zero setup, and Claude's own retrieval.

## Sources

- STORM paper — https://arxiv.org/abs/2402.14207
- Co-STORM paper — https://arxiv.org/abs/2408.15232
- Code — https://github.com/stanford-oval/storm
