"""`eval-jss benchmark` — score one or more models against the gold set.

The "gold" set is every violation row whose `reviewer LIKE 'human:%'`
and whose verdict is `true_positive` or `false_positive`. For each
model, classify every gold row in memory (NO writes to the live DB),
compare against the human verdict, and report confusion-matrix metrics
per (model, rule) and per model.

Models are configured as `<name>:<base_url>` flags; multiple `--model`
options stack. The `<name>` is used both as the OpenAI `model` field
and as the row label in the report.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

from eval import api, db
from eval.human_review import source_snippet
from eval.review import LlamaServerClient, _format_marked_context


@dataclass(frozen=True)
class ModelSpec:
    name: str
    base_url: str

    @classmethod
    def parse(cls, raw: str) -> ModelSpec:
        """Accept `name:http://host:port` or `name=http://host:port`."""
        for sep in (":", "="):
            if sep in raw:
                idx = raw.index(sep)
                # `:` collides with URL `http://…`; split on the first
                # delimiter ONLY when the right side starts with `http`.
                tail = raw[idx + 1:]
                if sep == ":" and tail.startswith("//"):
                    continue
                if sep == ":" and not (
                    tail.startswith("http://")
                    or tail.startswith("https://")
                ):
                    continue
                return cls(name=raw[:idx], base_url=tail)
        raise ValueError(
            f"--model spec {raw!r} must be name:http://host:port"
        )


def _load_gold(db_path: Path) -> list[dict]:
    cx = db.connect(db_path)
    try:
        rows = cx.execute(
            "SELECT v.id, v.rule_id, v.category, v.line, v.column, v.message,"
            " v.severity, v.file, v.verdict, p.path AS paper_path"
            " FROM violations v JOIN papers p ON p.id = v.paper_id"
            " WHERE v.reviewer LIKE 'human:%'"
            " AND v.verdict IN ('true_positive','false_positive')"
            " ORDER BY v.rule_id, v.id"
        ).fetchall()
    finally:
        cx.close()
    return [dict(r) for r in rows]


def _classify_one(client: LlamaServerClient, row: dict) -> api.ClassifyResult:
    snippet = source_snippet(row["paper_path"], row["file"], row["line"])
    if snippet is None:
        paper_context = ""
    else:
        text, start = snippet
        paper_context = _format_marked_context(
            text, start, row["line"], row["column"]
        )
    return client.classify(row, paper_context)


def _score_model(
    spec: ModelSpec, gold: list[dict], console: Console
) -> dict[str, dict]:
    """Run classifier across `gold`, return raw per-row outcomes."""
    client = LlamaServerClient(model=spec.name, base_url=spec.base_url)
    outcomes: list[dict] = []
    n = len(gold)
    console.print(f"[bold]{spec.name}[/bold] · {spec.base_url} · {n} rows")
    for i, row in enumerate(gold, 1):
        result = _classify_one(client, row)
        outcomes.append({
            "rule_id": row["rule_id"],
            "human": row["verdict"],
            "model": result.verdict.value,
            "confidence": result.confidence,
            "reason": result.reason,
        })
        if i % 10 == 0 or i == n:
            console.print(f"  …{i}/{n}", end="\r")
    console.print()
    return {"name": spec.name, "outcomes": outcomes}


def _summarise(score: dict) -> dict:
    """Compute per-rule and overall agreement / precision / recall.

    Definitions, treating human verdict as ground truth:
    - tp_agree: human=TP and model=TP
    - fp_agree: human=FP and model=FP
    - flip_to_fp: human=TP, model=FP (model rejected a real violation)
    - flip_to_tp: human=FP, model=TP (model accepted a spurious finding)
    - uncertain: model returned uncertain
    - precision_on_tp_calls: tp_agree / (tp_agree + flip_to_tp)
      — i.e., when the model says TP, how often is it right?
    """
    by_rule: dict[str, Counter] = defaultdict(Counter)
    overall = Counter()
    for o in score["outcomes"]:
        rule = o["rule_id"]
        h, m = o["human"], o["model"]
        if m == "uncertain":
            bucket = "uncertain"
        elif h == "true_positive" and m == "true_positive":
            bucket = "tp_agree"
        elif h == "false_positive" and m == "false_positive":
            bucket = "fp_agree"
        elif h == "true_positive" and m == "false_positive":
            bucket = "flip_to_fp"
        elif h == "false_positive" and m == "true_positive":
            bucket = "flip_to_tp"
        else:
            bucket = "other"
        by_rule[rule][bucket] += 1
        overall[bucket] += 1
    return {"name": score["name"], "by_rule": by_rule, "overall": overall}


def _agreement(c: Counter) -> float | None:
    decided = c["tp_agree"] + c["fp_agree"] + c["flip_to_fp"] + c["flip_to_tp"]
    if decided == 0:
        return None
    return (c["tp_agree"] + c["fp_agree"]) / decided


def _render(summaries: list[dict], console: Console) -> None:
    if not summaries:
        return

    overall = Table(title="Overall agreement vs human gold")
    overall.add_column("Model")
    overall.add_column("N", justify="right")
    overall.add_column("TP-agree", justify="right")
    overall.add_column("FP-agree", justify="right")
    overall.add_column("→FP (model rejected real)", justify="right")
    overall.add_column("→TP (model accepted bogus)", justify="right")
    overall.add_column("Uncertain", justify="right")
    overall.add_column("Agreement", justify="right")
    for s in summaries:
        c = s["overall"]
        n = sum(c.values())
        agree = _agreement(c)
        agree_str = f"{agree:.1%}" if agree is not None else "—"
        overall.add_row(
            s["name"], str(n),
            str(c["tp_agree"]), str(c["fp_agree"]),
            str(c["flip_to_fp"]), str(c["flip_to_tp"]),
            str(c["uncertain"]), agree_str,
        )
    console.print(overall)

    rules = sorted({r for s in summaries for r in s["by_rule"]})
    if not rules:
        return
    per_rule = Table(title="Per-rule agreement (rules with ≥2 gold rows)")
    per_rule.add_column("Rule")
    for s in summaries:
        per_rule.add_column(s["name"], justify="right")
    for rule in rules:
        # Only show rules where any model has at least 2 gold rows.
        max_n = max(sum(s["by_rule"][rule].values()) for s in summaries)
        if max_n < 2:
            continue
        cells = [rule]
        for s in summaries:
            c = s["by_rule"][rule]
            n = sum(c.values())
            agree = _agreement(c)
            if n == 0:
                cells.append("—")
            else:
                pct = f"{agree:.0%}" if agree is not None else "—"
                cells.append(f"{c['tp_agree'] + c['fp_agree']}/{n} ({pct})")
        per_rule.add_row(*cells)
    console.print(per_rule)


def run(
    *, db_path: Path, models: list[ModelSpec], limit: int | None,
    write_json: Path | None,
) -> int:
    if not models:
        print("eval-jss benchmark: no --model supplied.")
        return 2
    gold = _load_gold(db_path)
    if limit is not None:
        gold = gold[:limit]
    if not gold:
        print(
            "eval-jss benchmark: no human-labelled gold rows. Run "
            "`eval-jss human-review` first."
        )
        return 2
    console = Console()
    console.print(f"[bold]Gold set:[/bold] {len(gold)} rows")
    summaries: list[dict] = []
    for spec in models:
        score = _score_model(spec, gold, console)
        summaries.append(_summarise(score))
        if write_json is not None:
            with write_json.open("a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "model": spec.name,
                    "outcomes": score["outcomes"],
                }) + "\n")
    _render(summaries, console)
    return 0
