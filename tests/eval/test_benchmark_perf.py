"""Tests for the pure helpers in eval.benchmark_perf."""

from __future__ import annotations

from eval import benchmark_perf as bp


def test_percentile_nearest_rank() -> None:
    vals = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    assert bp._percentile(vals, 95) == 10.0
    assert bp._percentile(vals, 50) in (5.0, 6.0)
    assert bp._percentile([], 95) == 0.0
    assert bp._percentile([42.0], 95) == 42.0


def test_summary_contains_metrics_and_reproducibility() -> None:
    timings = [("paperA", 0.10), ("paperB", 0.30), ("paperC", 0.20)]
    spec = {"python": "3.11.2", "platform": "Linux x", "machine": "aarch64", "cpus": "10"}
    text = bp._summary(timings, spec, "python -m eval.benchmark_perf")
    assert "median" in text and "p95" in text
    assert "3 " in text or "Papers:** 3" in text
    assert "python -m eval.benchmark_perf" in text  # exact command recorded
    assert "aarch64" in text  # machine spec recorded
    assert "paperB" in text  # slowest listed


def test_machine_spec_keys() -> None:
    spec = bp._machine_spec()
    assert {"python", "platform", "machine", "cpus"} <= set(spec)
