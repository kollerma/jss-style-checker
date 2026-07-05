# Linter performance — full example corpus

**Papers:** 255   **Total wall (parse+lint):** 67.26 s   **Throughput:** 3.8 manuscripts/s

| Metric (per manuscript) | Seconds |
|---|---:|
| mean   | 0.2638 |
| median | 0.2307 |
| p95    | 0.6620 |
| min    | 0.0027 |
| max    | 1.5396 |

Slowest manuscripts:

| Manuscript | Seconds |
|---|---:|
| cran_mvtnorm | 1.5396 |
| cran_tram | 1.1560 |
| cran_surveillance | 0.9823 |
| cran_lme4 | 0.9533 |
| cran_trackeR | 0.8812 |

## Reproducibility

- Command: `python -m eval.benchmark_perf --corpus examples --repeats 3`
- Machine: Linux 6.12.76-linuxkit, aarch64, 10 logical CPUs
- Python: 3.11.2
- Measurement: in-process `parse_document` + rule-engine `run` per manuscript (the min over --repeats runs); excludes subprocess / interpreter-startup overhead.
