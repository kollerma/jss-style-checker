# Labeler benchmark — model-scope gold set

**Snapshot:** 2026-07-06 (pre-freeze refresh, both models). Gold set =
**1435 rows**, real-human labels only (`reviewer LIKE 'human:%'`,
excluding `human:claude-proxy` and `human:auto-*`) **after excluding the
32 mechanically-decidable `deterministic_rule_ids`** — those are now
auto-labelled by the linter (reviewer `human:auto-deterministic`) and
never routed to a model, so they are out of scope for a *model*
benchmark (spec: catalogue `deterministic_rule_ids`; `eval/review.py`).

Both models were scored on the **same** clean 1435-row set so the
columns are directly comparable. Raw per-row outcomes:
`eval/benchmark-runs/20260706-bonsai-gold1435.jsonl` and
`…-qwen3-gold1435.jsonl`.

## Gold-set decontamination (this snapshot)

The previous snapshot's gold set was contaminated: 243 AI-generated
adjudications had been written under the bare `human:*` namespace
(`human:readjudicate` ×155, `human:opus-nonr` ×68,
`human:xref005-listing` ×20) and so leaked past the machine-label
filter. They were **re-namespaced to `human:auto-*`** on 2026-07-06 so
the existing filter excludes them; verdicts were untouched, so precision
is unaffected. The convention (automated labels MUST use `human:auto-*`,
never bare `human:*`) is now codified in `benchmark._load_gold`.

Residual: 25 rows (`human:correction` ×20, `human:strict-ruling` ×5) are
kept as human — they read like deliberate reviewer rulings, not batch AI
output — pending a provenance confirmation from the annotator. If they
are AI, the set drops to 1410.

## Overall

| Model | N | TP-agree | FP-agree | →FP (rejected real) | →TP (accepted bogus) | Uncertain | Agreement |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bonsai-8B-mlx | 1435 | 660 | 3 | 42 | 108 | 622 | **81.5%** |
| Qwen3-30B (think-on) | 1435 | 820 | 55 | 125 | 60 | 375 | **82.5%** |

Agreement is over *decided* rows (uncertain excluded). The two models
are near-tied on agreement but differ sharply in **decisiveness**:
Bonsai punts on 622/1435 (43%), Qwen3 on only 375/1435 (26%). Bonsai is
the more conservative labeller (rarely commits to "FP", so few false
accepts); Qwen3 commits far more often and picks up the long-tail rules
Bonsai abstains on — exactly the split the per-rule routing exploits.

## Per-rule agreement (correct / total, `(agreement% on decided)`)

`—` = model punted on every row (no decided rows).

| Rule | Bonsai-8B-mlx | Qwen3-30B | Routing pin |
|---|---:|---:|---|
| JSS-CAP-002    | 144/153 (94%) | 104/153 (91%) | bonsai |
| JSS-MARKUP-003 | 137/253 (86%) | 151/253 (88%) | qwen3 |
| JSS-MARKUP-001 |  72/251 (62%) | 163/251 (87%) | **qwen3** |
| JSS-OPER-004   |  5/219 (100%) | 169/219 (88%) | bonsai † |
| JSS-OPER-002   |  98/115 (86%) |  33/115 (38%) | **bonsai** |
| JSS-NAME-002   |  75/105 (71%) |  82/105 (95%) | **qwen3** |
| JSS-CITE-002   |     0/56 (—)  |   25/56 (74%) | qwen3 |
| JSS-CODE-003   |  12/45 (100%) |   16/45 (59%) | bonsai |
| JSS-REFS-003   |   30/35 (86%) |    8/35 (80%) | bonsai |
| JSS-XREF-005   |     0/31 (—)  |   23/31 (96%) | default → bonsai ‡ |
| JSS-CAP-003    |   11/29 (38%) |    4/29 (29%) | skip-list |
| JSS-MARKUP-004 |  4/18 (100%)  |   16/18 (89%) | qwen3 |
| JSS-CITE-004   |  18/18 (100%) |  18/18 (100%) | bonsai |
| JSS-STRUCT-005 |     0/16 (—)  |   11/16 (92%) | default → bonsai ‡ |
| JSS-HOUSE-001  |   14/15 (93%) |    8/15 (80%) | bonsai |
| JSS-XREF-006   |     0/15 (—)  |  12/15 (100%) | default → bonsai ‡ |
| JSS-OPER-001   |  9/11 (100%)  |  10/11 (100%) | bonsai |
| JSS-REFS-004   |    4/8 (100%) |    5/8 (83%)  | — |
| JSS-XREF-001   |    5/7 (71%)  |    4/7 (57%)  | — |
| JSS-CAP-004    |    7/7 (100%) |    4/7 (100%) | bonsai |
| JSS-REFS-006   |   3/6 (100%)  |    1/6 (33%)  | — |
| JSS-STRUCT-001 |   4/5 (80%)   |    1/5 (33%)  | bonsai |
| JSS-ABBR-001   |    2/4 (67%)  |    1/4 (33%)  | — |
| JSS-CAP-001    |   3/4 (100%)  |     0/4 (0%)  | bonsai |
| JSS-MARKUP-002 |    2/4 (67%)  |   3/4 (100%)  | — |
| JSS-NAME-001   |   2/2 (100%)  |     0/2 (—)   | — |
| JSS-REFS-005   |   2/2 (100%)  |   2/2 (100%)  | — |

The current routing pins (`eval/review-routing.toml`) hold up: Bonsai
keeps OPER-002 (Qwen3 inverts polarity, 38%), CAP-002, CODE-003,
REFS-003; Qwen3 keeps MARKUP-001 (87% vs 62%), NAME-002 (95% vs 71%),
CITE-002, MARKUP-003/004.

**Routing opportunities observed this run (not yet applied — flagged for
a post-freeze routing pass):**
- **‡ XREF-005, STRUCT-005, XREF-006** fall through to the Bonsai
  default, which punts on *all* of them (0 decided), while Qwen3 decides
  them at 96% / 92% / 100%. Candidates to pin to `qwen3-30b`.
- **† OPER-004** is pinned to Bonsai on the strength of a tiny earlier
  sample (Bonsai now decides only 5/219); Qwen3 decides 169/219 at 88%.
  Reconsider pinning OPER-004 → `qwen3-30b`.

Not changed here because routing re-tuning is out of scope for a
benchmark refresh and lands better as its own reviewed change.

## Scope + caveats

- **Deterministic rules are out of scope.** The 32 `deterministic_rule_ids`
  (BIBTEX-\*, PRE-\*, TYPO-\*, XREF-002/004, CITE-003, CODE-001/002,
  OPER-003, HOUSE-002/003, STRUCT presence, REFS-001/007, WIDTH-001) are
  auto-labelled by the linter and no longer benchmarked. XREF-005 is kept
  in model scope (a parser edge gives it one genuine FP).
- **Qwen3 is thinking-on**, matching the routing config (a bare URL,
  no `chat_template_kwargs`). Thinking-off collapses its strong rules
  (MARKUP-001, XREF-004) and must not be used. Full 1435-row pass ≈ 6 h
  at ~16 s/row.
- **Not comparable to the 2026-05-01 snapshot** (934 rows, deterministic
  rules included, gold set still contaminated). This is a clean restart
  of the benchmark baseline.
