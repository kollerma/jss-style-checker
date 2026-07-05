"""Linter performance benchmark over the full example corpus.

Times the in-process parse + rule-engine cost per manuscript (the linter's
own work — excludes the ~fixed Python-interpreter startup of a subprocess
``jss-lint`` invocation) and reports total wall time plus the per-manuscript
median / p95 distribution. These numbers feed a performance table in the
JSS paper, so the summary records the exact command and the machine spec.

    python -m eval.benchmark_perf                 # print summary
    python -m eval.benchmark_perf --write         # also update benchmark-results.md
    python -m eval.benchmark_perf --corpus examples --repeats 1
"""

from __future__ import annotations

import argparse
import platform
import statistics
import sys
import time
from pathlib import Path

from eval.scan import _discover_papers, _source_files
from texlint.config import load as load_config
from texlint.core.engine import load_journal, parse_document
from texlint.core.engine import run as run_engine

REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "eval" / "benchmark-results.md"


def _machine_spec() -> dict[str, str]:
    import os

    return {
        "python": platform.python_version(),
        "platform": f"{platform.system()} {platform.release()}",
        "machine": platform.machine(),
        "cpus": str(os.cpu_count() or "?"),
    }


def _time_paper(files: list[Path], cfg, journal) -> float:
    """Seconds to parse + run the engine on one manuscript's files."""
    start = time.perf_counter()
    doc = parse_document(files)
    run_engine(cfg, doc, journal)
    return time.perf_counter() - start


def measure(corpus_dir: Path, repeats: int) -> list[tuple[str, float]]:
    cfg = load_config({}, Path.cwd())
    journal = load_journal(cfg.journal)
    papers = _discover_papers(corpus_dir)
    out: list[tuple[str, float]] = []
    for paper_dir in papers:
        files = _source_files(paper_dir)
        if not files:
            continue
        best = min(_time_paper(files, cfg, journal) for _ in range(repeats))
        out.append((paper_dir.name, best))
    return out


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    # nearest-rank
    k = max(0, min(len(s) - 1, round(pct / 100 * len(s) + 0.5) - 1))
    return s[k]


def _summary(timings: list[tuple[str, float]], spec: dict[str, str], cmd: str) -> str:
    secs = [t for _, t in timings]
    total = sum(secs)
    n = len(secs)
    slowest = sorted(timings, key=lambda x: x[1], reverse=True)[:5]
    lines = [
        "# Linter performance — full example corpus",
        "",
        f"**Papers:** {n}   **Total wall (parse+lint):** {total:.2f} s   "
        f"**Throughput:** {n / total:.1f} manuscripts/s"
        if total
        else f"**Papers:** {n}",
        "",
        "| Metric (per manuscript) | Seconds |",
        "|---|---:|",
        f"| mean   | {statistics.mean(secs):.4f} |",
        f"| median | {statistics.median(secs):.4f} |",
        f"| p95    | {_percentile(secs, 95):.4f} |",
        f"| min    | {min(secs):.4f} |",
        f"| max    | {max(secs):.4f} |",
        "",
        "Slowest manuscripts:",
        "",
        "| Manuscript | Seconds |",
        "|---|---:|",
        *[f"| {name} | {t:.4f} |" for name, t in slowest],
        "",
        "## Reproducibility",
        "",
        f"- Command: `{cmd}`",
        f"- Machine: {spec['platform']}, {spec['machine']}, "
        f"{spec['cpus']} logical CPUs",
        f"- Python: {spec['python']}",
        "- Measurement: in-process `parse_document` + rule-engine `run` per "
        "manuscript (the min over --repeats runs); excludes subprocess / "
        "interpreter-startup overhead.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="python -m eval.benchmark_perf")
    ap.add_argument("--corpus", default="examples")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cmd = f"python -m eval.benchmark_perf --corpus {args.corpus} --repeats {args.repeats}"
    timings = measure(Path(args.corpus), args.repeats)
    if not timings:
        print("eval-jss: no papers found to benchmark.")
        return 2
    text = _summary(timings, _machine_spec(), cmd)
    print(text)
    if args.write:
        RESULTS.write_text(text, encoding="utf-8")
        print(f"wrote {RESULTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
