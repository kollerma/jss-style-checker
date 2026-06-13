# Labeler benchmark runs

Per-row classifier outcomes from `eval-jss benchmark --write-json`,
scored against the human-labelled gold set. One JSON line per gold
row. Used to calibrate the per-rule routing in `../review-routing.toml`.

## 2026-06-13 — Qwen3-30B re-benchmark + model-swap investigation

Gold set: 902 rows (down from the historical 934 after the
label-consistency pass, iteration 80).

| File | Model | Mode | Overall agreement |
|------|-------|------|-------------------|
| `20260613-qwen3-30b-thinkon-gold902.jsonl`   | Qwen3-30B-A3B   | thinking ON (default)  | **90.8%** |
| `20260613-qwen3-30b-thinkoff-gold902.jsonl`  | Qwen3-30B-A3B   | thinking OFF           | 77.8% |
| `20260613-bonsai-gold902.jsonl`              | Bonsai-8B-mlx   | (reasoning_content)    | 89.0% (decided) |
| `20260613-qwen3.5-35b-thinkoff-gold902.jsonl`| Qwen3.5-35B     | thinking OFF           | 82.0% |

Why four runs: port 8080 had briefly been swapped to Qwen3.5-35B,
whose heavier chain-of-thought overran the 1024-token budget with
thinking ON (every row UNCERTAIN), so it was benchmarked thinking-OFF.
Qwen3-30B was then restored and benchmarked both ways. The decisive
result: Qwen3-30B needs thinking **ON** — thinking-off collapses its
high-volume Markup rules (MARKUP-001 90%→69%, XREF-004 100%→73%),
while its reasoning fits the budget so thinking-on is both viable and
strong. The routing therefore pins Qwen3-30B as a bare URL (default
thinking-on); see `../review-routing.toml`.
