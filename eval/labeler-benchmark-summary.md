# Labeler benchmark — full 934-row gold set

**Snapshot:** 2026-05-01, after iter-71-baseline. Gold set = 934 rows
labelled by real humans (`reviewer LIKE 'human:%'`, excluding
`human:claude-proxy` and `human:auto-*`). Per-row outcomes persisted
to `eval/labeler-benchmark.json`.

## Overall

| Model | N | TP-agree | FP-agree | →FP (rejected real) | →TP (accepted bogus) | Uncertain | Agreement |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bonsai-8B-mlx | 934 | 435 | 1 | 17 | 56 | 425 | **85.7%** |
| Qwen3-30B-A3B | 934 | 538 | 29 | 53 | 15 | 299 | **89.3%** |

Both clear the policy floor of `min_overall_agreement = 0.85`. Qwen3
wins by 3.6pp overall, but the per-rule picture is **strongly
complementary** — pick the right model per rule rather than one
universal labeller.

## Per-rule agreement (rules with ≥5 gold rows)

| Rule | N | Bonsai | Qwen3-30B | Notes |
|---|---:|---:|---:|---|
| JSS-CAP-002 | 192 | **94%** | 88% | Both strong; prefer Bonsai |
| JSS-MARKUP-001 | 188 | 78% | **92%** | Bonsai uncertain on 161/188; Qwen3 decisive |
| JSS-MARKUP-003 | 105 | — | **100%** | Bonsai 100% uncertain — useless here |
| JSS-CAP-003 | 47 | 40% | 63% | Both poor; rule on AI skip-list |
| JSS-XREF-004 | 45 | (100%) | **97%** | Bonsai decides only 2/45; Qwen3 decisive |
| JSS-CITE-002 | 43 | — | **94%** | Bonsai 100% uncertain |
| JSS-NAME-002 | 38 | 63% | **100%** | Bonsai flips 13 publisher TPs; on skip-list |
| JSS-REFS-003 | 38 | **84%** | 50% | Bonsai much better; only decides 6/38 for Qwen |
| JSS-BIBTEX-004 | 30 | (100%) | (0%) | Both ≥97% uncertain — needs human |
| JSS-OPER-002 | 25 | **96%** | 48% | Bonsai dominant; on skip-list |
| JSS-CITE-004 | 18 | **100%** | **100%** | Trivial for both |
| JSS-MARKUP-004 | 17 | (100%) | **87%** | Qwen3 decisive on more |
| JSS-CAP-001 | 15 | **100%** | (0%) | — |
| JSS-HOUSE-001 | 15 | **93%** | 70% | Bonsai better |
| JSS-OPER-004 | 15 | (100%) | **100%** | Qwen3 decides 13/15 |
| JSS-CODE-003 | 11 | **100%** | 67% | Bonsai dominant |
| JSS-OPER-001 | 11 | **100%** | **100%** | Both perfect |
| JSS-CITE-003 | 10 | **100%** | **100%** | Both perfect |
| JSS-XREF-002 | 10 | **100%** | **100%** | Both perfect |
| JSS-PARSE-000 | 8 | 62% | 67% | Both poor; deterministic check anyway |
| JSS-CAP-004 | 7 | **100%** | **100%** | — |
| JSS-TYPO-001 | 7 | **100%** | **100%** | — |
| JSS-PRE-001 | 6 | **100%** | **100%** | — |
| JSS-STRUCT-001 | 5 | 80% | 50% | Bonsai better |

Parens `(X%)` indicate the model decided very few rows — the agreement
percentage applies to the small decided subset; the rest were "uncertain".

## Strategic implications

**Routing per rule** (better than one-model-fits-all):

- **Bonsai-only routes** (Bonsai ≥ 90%, Qwen3 lower): JSS-CAP-002,
  JSS-REFS-003, JSS-OPER-002, JSS-HOUSE-001, JSS-CODE-003.
- **Qwen3-only routes** (Qwen3 ≥ 90%, Bonsai uncertain or wrong):
  JSS-MARKUP-001, JSS-MARKUP-003, JSS-CITE-002, JSS-XREF-004,
  JSS-NAME-002.
- **Either** (both ≥ 90%): JSS-CITE-003, JSS-CITE-004, JSS-XREF-002,
  JSS-OPER-001, JSS-CAP-004, JSS-TYPO-001, JSS-PRE-001, JSS-CAP-001
  (Bonsai), JSS-CAP-003 already on skip-list.
- **Human review only** (no model reliable): JSS-BIBTEX-004 (both
  ~100% uncertain), JSS-CAP-003 (both 40-63%), JSS-PARSE-000 (62-67%).

The current `eval/review-skip-list.toml` covers JSS-CAP-001/002/003/004,
JSS-CITE-004, JSS-OPER-002, JSS-REFS-002, JSS-NAME-002. With these
benchmark numbers the skip-list should be revised:

- **REMOVE** from skip-list (model handles them): JSS-CAP-001
  (Bonsai 100%), JSS-CAP-002 (Bonsai 94%, large sample), JSS-CAP-004
  (both 100%), JSS-OPER-002 (Bonsai 96%), JSS-NAME-002 (Qwen3 100%).
- **KEEP** in skip-list: JSS-CAP-003 (both ≤63%), JSS-CITE-004
  (perfect agreement makes review redundant — controversial).

## Bonsai vs Qwen3: model-temperament summary

- Bonsai is a **decisive minority labeller**: when it commits to an
  answer it's usually right (435 TP-agree, 1 FP-agree, only 17 →FP
  vs human truth), but it punts (uncertain) on 425 of 934 rows.
- Qwen3 is a **commit-prone majority labeller**: decides 635 of 934
  but with more wrong calls (29 FP-agree + 53 →FP + 15 →TP =
  97 outright disagreements, vs Bonsai's 74).
- Net: Qwen3's higher agreement comes from confidently labelling
  rows Bonsai punted on. Both are useful; an ensemble that prefers
  the model with higher per-rule agreement (and falls back to
  human-review when both disagree) would beat either alone.

## Followups

- Rebenchmark cadence: re-run after every 5 iterations per
  `iteration-policy.toml::labeler_health.rebenchmark_every_n_iterations`.
- Wire per-rule routing into `eval-jss review` (today it always uses
  one model).
- Raise/lower `min_rule_agreement = 0.75` based on this evidence
  (current threshold catches CAP-003, NAME-002, PARSE-000, MARKUP-001
  for Bonsai; CAP-003, REFS-003, OPER-002, STRUCT-001, BIBTEX-004,
  CAP-001, BIBTEX-002 for Qwen3).
