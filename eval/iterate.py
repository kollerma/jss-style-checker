"""`eval-jss iterate record` — snapshot + log one iteration of the loop.

The loop is a 9-step cycle (see `eval/README.md`). This module implements
step 5: run the report twice (full and pinned) against `eval/eval.db`,
persist both snapshots into `eval/precision-history.db`, and append a
templated section to `eval/improvement-log.md`.

The "suggest improvements" / "plan" / "implement" steps are deliberately
not automated — those are where human / Claude judgement belongs.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from eval import db, history
from eval import report as report_mod
from eval.report import PrecisionTable, RuleRow


def _corpus_size(db_path: Path) -> int:
    cx = db.connect(db_path)
    try:
        row = cx.execute("SELECT COUNT(*) AS c FROM papers").fetchone()
    finally:
        cx.close()
    return int(row["c"]) if row else 0


def _tool_version(db_path: Path) -> str:
    cx = db.connect(db_path)
    try:
        row = cx.execute(
            "SELECT tool_version FROM runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        cx.close()
    return row["tool_version"] if row else "unknown"


def _format_rule_table(rows: Iterable[RuleRow]) -> str:
    """Render overall rows as a GitHub-flavored Markdown table."""
    lines = [
        "| category | rule | tp | fp | pending | precision | status |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for r in sorted(rows, key=lambda x: (x.category, x.rule_id)):
        if r.source != "overall":
            continue
        prec = f"{r.precision:.2%}" if r.precision is not None else "—"
        lines.append(
            f"| {r.category} | {r.rule_id} | {r.tp} | {r.fp} | "
            f"{r.pending} | {prec} | {r.status} |"
        )
    return "\n".join(lines)


def _format_delta(
    current: PrecisionTable,
    prev_map: dict[tuple[str, str], tuple[int, int, int]],
    scope: str,
) -> str:
    """Render a compact delta vs. the previous iteration, in Markdown."""
    if not prev_map:
        return "_(no prior iteration — baseline)_"
    entries: list[str] = []
    for r in sorted(current.rows, key=lambda x: (x.category, x.rule_id)):
        if r.source != "overall":
            continue
        key = (scope, r.rule_id)
        prev = prev_map.get(key)
        if prev is None:
            entries.append(
                f"- **new** `{r.rule_id}`: tp={r.tp} fp={r.fp} pending={r.pending}"
            )
            continue
        p_tp, p_fp, p_pending = prev
        d_tp, d_fp, d_pending = r.tp - p_tp, r.fp - p_fp, r.pending - p_pending
        if (d_tp, d_fp, d_pending) == (0, 0, 0):
            continue
        entries.append(
            f"- `{r.rule_id}`: "
            f"tp {p_tp:+d}→{r.tp} ({d_tp:+d}), "
            f"fp {p_fp:+d}→{r.fp} ({d_fp:+d}), "
            f"pending {p_pending}→{r.pending} ({d_pending:+d})"
        )
    if not entries:
        return "_(no rule-level changes)_"
    return "\n".join(entries)


def _markdown_section(
    *,
    iteration_id: int,
    ts: str,
    label: str,
    note: str | None,
    corpus_size: int,
    tool_version: str,
    full: PrecisionTable,
    pinned: PrecisionTable,
    prev_map: dict[tuple[str, str], tuple[int, int, int]],
) -> str:
    note_block = f"\n**Note:** {note}\n" if note else ""
    return f"""
## Iteration {iteration_id} — {ts} — {label}

- **Corpus size:** {corpus_size} papers
- **Tool version:** `{tool_version}`
- **Parse failures:** full={full.parse_failures}, pinned={pinned.parse_failures}
{note_block}
### Stats — full corpus

{_format_rule_table(full.rows)}

### Stats — pinned only

{_format_rule_table(pinned.rows)}

### Delta vs. previous iteration

**Full corpus**

{_format_delta(full, prev_map, "full")}

**Pinned only**

{_format_delta(pinned, prev_map, "pinned")}

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_
"""


_LOG_PREAMBLE = """# Eval-improve log

Each section below is one iteration of the eval-improve loop (see
`eval/README.md`). Stats are snapshots taken at record time; the
machine-readable copy lives in `eval/precision-history.db`.
"""


def _ensure_log_preamble(log_path: Path) -> None:
    if log_path.exists():
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(_LOG_PREAMBLE, encoding="utf-8")


def run_refresh(
    *,
    eval_db: Path,
    corpus_dir: Path,
    orphans_path: Path | None,
    no_save_orphans: bool = False,
) -> int:
    """Re-scan the corpus while preserving labelled verdicts.

    The wipe-and-rescan dance — DELETE FROM violations, run
    `eval-jss scan --force`, then UPDATE the labels back onto matching
    rows — has run by hand once per rule-fix iteration. This bakes it
    into one command and surfaces the orphaned-label count (rows whose
    matching violation no longer fires post-fix).

    Orphan dumping defaults to ON because rolling back a rule fix that
    suppressed N violations otherwise loses N labels permanently —
    they'd need human re-adjudication on the rebuilt rows. The default
    path is ``eval/orphans/<utc-timestamp>.json``; ``orphans_path``
    overrides; ``no_save_orphans=True`` disables.
    """
    import json

    from eval import scan as scan_mod

    if not no_save_orphans and orphans_path is None:
        ts = db.now_utc().replace(":", "").replace("-", "")
        orphans_path = Path("eval/orphans") / f"{ts}.json"

    cx = db.connect(eval_db)
    try:
        labels = cx.execute(
            "SELECT paper_id, rule_id, line, message, verdict, "
            "verdict_reason, reviewer, file FROM violations "
            "WHERE verdict IS NOT NULL"
        ).fetchall()
        before = len(labels)
        labels_dicts = [
            dict(zip(
                ["paper_id", "rule_id", "line", "message", "verdict",
                 "verdict_reason", "reviewer", "file"],
                tuple(r),
                strict=True,
            ))
            for r in labels
        ]
        cx.execute("DELETE FROM violations")
        print(f"eval-jss refresh: backed up {before} labelled rows; rescanning…")
    finally:
        cx.close()

    scan_code = scan_mod.run(
        db_path=eval_db, corpus_dir=corpus_dir,
        batch_size=None, force=True,
    )
    if scan_code == 2:
        print("eval-jss refresh: scan failed; labels are still in memory but DB is empty.")
        return 2

    cx = db.connect(eval_db)
    try:
        restored = 0
        orphans: list[dict] = []
        for row in labels_dicts:
            r = cx.execute(
                "UPDATE violations SET verdict=?, verdict_reason=?, reviewer=? "
                "WHERE paper_id=? AND rule_id=? AND line IS ? "
                "AND message=? AND (file IS ? OR file=?)",
                (
                    row["verdict"], row["verdict_reason"], row["reviewer"],
                    row["paper_id"], row["rule_id"], row["line"], row["message"],
                    row["file"], row["file"],
                ),
            )
            if r.rowcount:
                restored += 1
            else:
                orphans.append(row)
    finally:
        cx.close()

    print(f"eval-jss refresh: restored {restored}/{before} labels; "
          f"{len(orphans)} orphaned (violation no longer fires).")
    if orphans_path is not None and orphans:
        orphans_path.parent.mkdir(parents=True, exist_ok=True)
        with orphans_path.open("w", encoding="utf-8") as f:
            json.dump(orphans, f, indent=2)
        print(f"eval-jss refresh: orphan dump → {orphans_path}")
    return 0


def run_apply_orphans(*, eval_db: Path, orphans_path: Path) -> int:
    """Re-apply labels from an orphan dump onto current violations.

    Pair with ``run_refresh`` after rolling back a rule fix: the rule
    starts firing on rows again, the orphan dump still has their labels
    from before the (now-reverted) fix, and this command stitches them
    back together.
    """
    import json

    if not orphans_path.is_file():
        print(f"eval-jss apply-orphans: file not found at {orphans_path}")
        return 2
    with orphans_path.open("r", encoding="utf-8") as f:
        orphans = json.load(f)

    cx = db.connect(eval_db)
    try:
        applied = 0
        still_orphaned = 0
        for row in orphans:
            r = cx.execute(
                "UPDATE violations SET verdict=?, verdict_reason=?, reviewer=? "
                "WHERE paper_id=? AND rule_id=? AND line IS ? "
                "AND message=? AND (file IS ? OR file=?)",
                (
                    row["verdict"], row["verdict_reason"], row["reviewer"],
                    row["paper_id"], row["rule_id"], row["line"], row["message"],
                    row["file"], row["file"],
                ),
            )
            if r.rowcount:
                applied += 1
            else:
                still_orphaned += 1
    finally:
        cx.close()

    print(
        f"eval-jss apply-orphans: re-applied {applied} of {len(orphans)} "
        f"labels from {orphans_path}; {still_orphaned} still orphaned."
    )
    return 0


def run(
    *,
    eval_db: Path,
    history_db: Path,
    log_path: Path,
    manifest_path: Path,
    corpus_dir: Path,
    label: str,
    note: str | None,
) -> int:
    full = report_mod.compute_precision(eval_db)
    pinned_pairs = report_mod._pinned_pairs(manifest_path, corpus_dir)
    pinned = report_mod.compute_precision(eval_db, pinned=pinned_pairs)

    ts = db.now_utc()
    corpus_size = _corpus_size(eval_db)
    tool_version = _tool_version(eval_db)

    iteration_id = history.record(
        history_db,
        ts=ts, label=label, note=note,
        corpus_size=corpus_size, tool_version=tool_version,
        full=full, pinned=pinned,
    )
    prev_map = history.previous(history_db, iteration_id)

    section = _markdown_section(
        iteration_id=iteration_id,
        ts=ts, label=label, note=note,
        corpus_size=corpus_size, tool_version=tool_version,
        full=full, pinned=pinned, prev_map=prev_map,
    )
    _ensure_log_preamble(log_path)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(section)

    print(
        f"eval-jss: recorded iteration {iteration_id} "
        f"({label}) into {history_db} and appended to {log_path}"
    )
    return 0


def _load_policy(policy_path: Path) -> dict:
    """Read iteration-policy.toml; fall back to a baked-in default."""
    defaults = {
        "precision_threshold": 0.90,
        "min_tp_for_pass": 10,
        "precision_drop_tolerance_pp": 3.0,
    }
    if not policy_path.exists():
        return defaults
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]
    raw = tomllib.loads(policy_path.read_text(encoding="utf-8"))
    pass_cfg = raw.get("pass_criteria", {})
    fix_cfg = raw.get("fix_attempt", {})
    return {
        "precision_threshold": float(
            pass_cfg.get("precision_threshold", defaults["precision_threshold"])
        ),
        "min_tp_for_pass": int(
            pass_cfg.get("min_tp_for_pass", defaults["min_tp_for_pass"])
        ),
        "precision_drop_tolerance_pp": float(
            fix_cfg.get(
                "precision_drop_tolerance_pp",
                defaults["precision_drop_tolerance_pp"],
            )
        ),
    }


def run_guard(
    *,
    eval_db: Path,
    history_db: Path,
    manifest_path: Path,
    corpus_dir: Path,
    policy_path: Path,
) -> int:
    """Block recording when the current scan introduces a per-rule
    precision regression past the iteration-policy tolerance.

    Returns 0 when no regression is detected (recording is safe), 1
    when one or more passing rules dropped below the threshold or by
    more than ``precision_drop_tolerance_pp`` from their last
    recorded value, 2 on usage / file errors.
    """
    if not eval_db.exists():
        print(f"eval-jss guard: {eval_db} does not exist", flush=True)
        return 2

    policy = _load_policy(policy_path)
    pp_tolerance = policy["precision_drop_tolerance_pp"] / 100.0
    pass_threshold = policy["precision_threshold"]
    min_tp = policy["min_tp_for_pass"]

    prev_iter, prev_stats = history.latest_stats(history_db)
    if prev_iter is None:
        print("eval-jss guard: no prior iteration recorded — pass.")
        return 0

    full = report_mod.compute_precision(eval_db)
    pinned_pairs = report_mod._pinned_pairs(manifest_path, corpus_dir)
    pinned = report_mod.compute_precision(eval_db, pinned=pinned_pairs)

    regressions: list[str] = []
    for table, scope in ((full, "full"), (pinned, "pinned")):
        for r in table.rows:
            if r.source != "overall":
                continue
            prev = prev_stats.get((scope, r.rule_id))
            if prev is None:
                continue  # new rule, no baseline to compare to
            p_tp, p_fp, p_pending, p_prec, p_status = prev
            # Only guard rules that WERE passing — a fix on a FAIL rule
            # is allowed to keep failing without blocking recording.
            if p_status != "PASS":
                continue
            cur_prec = r.precision
            # If precision is None (no fires), the rule is vacuously
            # not regressing; skip.
            if cur_prec is None or p_prec is None:
                continue
            # Block if (a) precision dropped past tolerance, (b) the
            # rule fell below the global pass threshold from above, or
            # (c) TP count collapsed from at-or-above min_tp to below.
            # Pre-existing low-TP / low-precision rules don't count —
            # this iteration must have caused the regression.
            dropped_past_tolerance = (p_prec - cur_prec) > pp_tolerance
            below_threshold_now = (
                cur_prec < pass_threshold and p_prec >= pass_threshold
            )
            tp_collapsed = (
                p_tp >= min_tp and (r.tp + r.pending) < min_tp
            )
            if dropped_past_tolerance or below_threshold_now or tp_collapsed:
                if dropped_past_tolerance:
                    why = f"dropped {(p_prec - cur_prec) * 100:.2f}pp past tolerance"
                elif below_threshold_now:
                    why = f"crossed below pass threshold {pass_threshold:.0%}"
                else:
                    why = f"tp collapsed from {p_tp} to {r.tp} (min_tp={min_tp})"
                regressions.append(
                    f"  [{scope}] {r.rule_id}: "
                    f"{p_prec:.1%} → {cur_prec:.1%} "
                    f"(tp {p_tp}→{r.tp}, fp {p_fp}→{r.fp}); {why}"
                )

    if regressions:
        print(
            f"eval-jss guard: REGRESSION vs iteration {prev_iter} — "
            f"{len(regressions)} rule(s) dropped past policy:"
        )
        for line in regressions:
            print(line)
        print(
            "\nResolve before recording: revert the offending change "
            "(`git revert HEAD` after the fix commit) or relax the "
            "policy in eval/iteration-policy.toml if intentional."
        )
        return 1

    print(
        f"eval-jss guard: no regression vs iteration {prev_iter} — "
        f"recording is safe."
    )
    return 0
