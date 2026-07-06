# Labeler benchmark — model-scope gold set

**Snapshot:** 2026-07-06 (pre-freeze refresh). Gold set = **1576 rows**
labelled by real humans (`reviewer LIKE 'human:%'`, excluding
`human:claude-proxy` and `human:auto-*`) **after excluding the 32
mechanically-decidable `deterministic_rule_ids`** — those are now
auto-labelled by the linter (reviewer `human:auto-deterministic`) and
never routed to a model, so they are out of scope for a *model*
benchmark (spec: catalogue `deterministic_rule_ids`; `eval/review.py`).
Raw per-row outcomes: `eval/benchmark-runs/20260706-bonsai-gold1576.jsonl`.

## Overall

| Model | N | TP-agree | FP-agree | →FP (rejected real) | →TP (accepted bogus) | Uncertain | Agreement |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bonsai-8B-mlx | 1576 | 693 | 9 | 97 | 115 | 662 | **76.8%** |

Down from the 2026-05-01 snapshot (85.7% on 934 rows). The drop is a
mix-shift, not a regression: (a) the gold set nearly doubled and now skews
toward the hard **semantic** rules (MARKUP-001/003, CITE-002, OPER-004,
NAME-002, REFS-006) since the easy deterministic rules — where Bonsai
scored ~100% — were removed as out-of-scope; (b) Bonsai remains a
*decisive-minority* labeller, punting (uncertain) on 662/1576.

## Per-rule agreement (rules with ≥2 gold rows)

`(X%)` on a small decided subset; `—` = model punted on every row.

| Rule | Bonsai (decided/total) |
|---|---:|
| JSS-CAP-002    | 149/159 (94%) |
| JSS-OPER-002   |  98/115 (86%) |
| JSS-MARKUP-003 | 137/254 (86%) |
| JSS-MARKUP-001 |  83/289 (57%) |
| JSS-NAME-002   |  78/110 (71%) |
| JSS-CODE-003   |   16/54 (84%) |
| JSS-XREF-005   |   13/54 (87%) |
| JSS-REFS-003   |   30/40 (75%) |
| JSS-CAP-003    |   11/29 (38%) |
| JSS-REFS-006   |    3/26 (14%) |
| JSS-MARKUP-004 |   4/19 (100%) |
| JSS-CITE-004   |  18/18 (100%) |
| JSS-HOUSE-001  |   14/17 (82%) |
| JSS-STRUCT-005 |      0/16 (—) |
| JSS-XREF-006   |      0/16 (—) |
| JSS-OPER-001   |    9/12 (90%) |
| JSS-MARKUP-002 |    3/12 (30%) |
| JSS-STRUCT-001 |     5/7 (71%) |
| JSS-CAP-004    |    7/7 (100%) |
| JSS-XREF-001   |     6/8 (75%) |
| JSS-REFS-004   |    4/8 (100%) |
| JSS-CAP-001    |    3/4 (100%) |
| JSS-ABBR-001   |     2/4 (67%) |
| JSS-REFS-005   |     2/4 (50%) |
| JSS-NAME-001   |    2/2 (100%) |
| JSS-CITE-002   |      0/72 (—) |
| JSS-OPER-004   |  5/219 (100%) |

## Scope + caveats

- **Deterministic rules are out of scope.** The 32 `deterministic_rule_ids`
  (BIBTEX-\*, PRE-\*, TYPO-\*, XREF-002/004, CITE-003, CODE-001/002,
  OPER-003, HOUSE-002/003, STRUCT presence, REFS-001/007, WIDTH-001) are
  auto-labelled by the linter and no longer benchmarked — the model never
  sees them. XREF-005 is deliberately kept in model scope (a parser edge
  gives it one genuine FP).
- **Qwen3-30B not refreshed this run.** At ~16 s/row (thinking-on, as
  routed) a full 1576-row Qwen3 pass is ≈7 h — impractical in this
  session. The 2026-05-01 Qwen3 numbers are on a *different* gold set
  (934 rows, deterministic rules included) and are **not** comparable to
  the table above; a fresh Qwen3 pass should be run before final routing
  decisions.
- **Gold-set composition.** 1410/1576 rows are original human labels
  (`human:unknown`); **166 (10.5%) are recent AI-assisted adjudications**
  (`human:readjudicate`/`opus`/`xref005`/`correction`/`strict`). These
  survive the `human:%` filter but are not independent human ground
  truth — see the freeze note in `improvement-log.md`.
