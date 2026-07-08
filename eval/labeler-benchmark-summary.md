# Labeler benchmark — model-scope gold set

**Snapshot:** 2026-07-07 (pre-freeze refresh, both models, decontaminated
gold). Gold set = **1410 rows**, **exclusively independent human labels**
(`reviewer = 'human:unknown'`) after excluding the 32 mechanically-decidable
`deterministic_rule_ids` — those are now auto-labelled by the linter
(reviewer `human:auto-deterministic`) and never routed to a model, so
they are out of scope for a *model* benchmark (spec: catalogue
`deterministic_rule_ids`; `eval/review.py`).

Both models were scored on the **same** clean 1410-row set so the columns
are directly comparable. Raw per-row outcomes:
`eval/benchmark-runs/20260707-bonsai-gold1410.jsonl` and
`…-qwen3-gold1410.jsonl`.

## Gold-set decontamination (this snapshot)

The gold set had accumulated **268 AI-generated adjudications** written
under the bare `human:*` namespace, which leaked past the machine-label
filter and were being counted as human ground truth:

| Tag (before) | Rows | Provenance |
|---|--:|---|
| `human:readjudicate`    | 155 | eval-sweep workflow adjudications |
| `human:opus-nonr`       |  68 | Opus subagent adjudications |
| `human:correction`      |  25 | AI corrections of earlier AI mislabels ("… (AI mislabel)") |
| `human:xref005-listing` |  20 | XREF-005 verify workflow |
| `human:strict-ruling`   |   5 | AI strict-ruling that *overrode prior human TPs* on retired CAP-003 |

All were **re-namespaced to `human:auto-*`** so the existing
`NOT LIKE 'human:auto-%'` filter excludes them; verdicts were untouched,
so linter precision is unaffected (97.23%). The convention (automated
labels MUST use `human:auto-*`, never bare `human:*`) is now codified in
`benchmark._load_gold`. The resulting gold set is 1410 rows, all
`human:unknown` — no AI-adjudication residue.

## Overall

| Model | N | TP-agree | FP-agree | →FP (rejected real) | →TP (accepted bogus) | Uncertain | Agreement |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bonsai-8B-mlx | 1410 | 651 | 3 | 32 | 103 | 621 | **82.9%** |
| Qwen3-30B (think-on) | 1410 | 811 | 56 | 121 | 60 | 362 | **82.7%** |

A dead heat on agreement (over *decided* rows; uncertain excluded), but
the models differ sharply in **decisiveness**: Bonsai punts on 621/1410
(44%), Qwen3 on only 362/1410 (26%). Bonsai is the conservative labeller
(rarely commits to "FP", so almost no FP-agreement); Qwen3 commits far
more and picks up the long-tail rules Bonsai abstains on — exactly the
split the per-rule routing exploits.

## Per-rule agreement (correct / total, `(agreement% on decided)`)

`—` = model punted on every row (no decided rows).

| Rule | Bonsai-8B-mlx | Qwen3-30B | Routing pin |
|---|---:|---:|---|
| JSS-MARKUP-003 | 137/253 (86%) | 151/253 (82%) | qwen3 |
| JSS-MARKUP-001 |  72/251 (62%) | 161/251 (85%) | **qwen3** |
| JSS-OPER-004   |  5/219 (100%) | 169/219 (88%) | bonsai † |
| JSS-CAP-002    | 144/153 (94%) | 106/153 (95%) | bonsai |
| JSS-OPER-002   |  98/115 (86%) |  33/115 (40%) | **bonsai** |
| JSS-NAME-002   |   74/96 (77%) |   68/96 (99%) | **qwen3** |
| JSS-CITE-002   |     0/56 (—)  |   27/56 (75%) | qwen3 |
| JSS-CODE-003   |  12/45 (100%) |   18/45 (58%) | bonsai |
| JSS-REFS-003   |   30/35 (86%) |    4/35 (50%) | bonsai |
| JSS-XREF-005   |     0/31 (—)  |   24/31 (96%) | default → bonsai ‡ |
| JSS-CAP-003    |   11/24 (46%) |    5/24 (62%) | skip-list |
| JSS-CITE-004   |  18/18 (100%) |  18/18 (100%) | bonsai |
| JSS-STRUCT-005 |     0/16 (—)  |   14/16 (93%) | default → bonsai ‡ |
| JSS-XREF-006   |     0/15 (—)  |  13/15 (100%) | default → bonsai ‡ |
| JSS-MARKUP-004 |  1/14 (100%)  |   13/14 (93%) | qwen3 |
| JSS-HOUSE-001  |  11/11 (100%) |    9/11 (100%) | bonsai |
| JSS-OPER-001   |  9/11 (100%)  |  10/11 (100%) | bonsai |
| JSS-CAP-004    |    7/7 (100%) |    1/7 (100%) | bonsai |
| JSS-REFS-004   |    3/7 (100%) |    5/7 (83%)  | — |
| JSS-XREF-001   |    5/7 (71%)  |    5/7 (71%)  | — |
| JSS-REFS-006   |   3/6 (100%)  |    2/6 (67%)  | — |
| JSS-ABBR-001   |    2/4 (67%)  |    1/4 (50%)  | — |
| JSS-CAP-001    |   3/4 (100%)  |    1/4 (33%)  | bonsai |
| JSS-MARKUP-002 |    2/4 (67%)  |   4/4 (100%)  | — |
| JSS-STRUCT-001 |   4/4 (100%)  |    1/4 (50%)  | bonsai |
| JSS-REFS-005   |   2/2 (100%)  |   2/2 (100%)  | — |

The current routing pins (`eval/review-routing.toml`) hold up: Bonsai
keeps OPER-002 (Qwen3 inverts polarity, 40%), CAP-002, CODE-003,
REFS-003; Qwen3 keeps MARKUP-001 (85% vs 62%), NAME-002 (99% vs 77%),
CITE-002, MARKUP-003/004.

**Routing opportunities observed this run (not yet applied — flagged for
a post-freeze routing pass):**
- **‡ XREF-005, STRUCT-005, XREF-006** fall through to the Bonsai
  default, which punts on *all* of them (0 decided), while Qwen3 decides
  them at 96% / 93% / 100%. Candidates to pin to `qwen3-30b`.
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
  (MARKUP-001, XREF-004) and must not be used. Full 1410-row pass ≈ 6 h
  at ~16 s/row.
- **Not comparable to the 2026-05-01 snapshot** (934 rows, deterministic
  rules included, gold set still contaminated). This is a clean restart
  of the benchmark baseline on independent-human ground truth.
