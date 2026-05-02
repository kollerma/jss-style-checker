"""`eval-jss` CLI entry point.

Console script: registered in `pyproject.toml` as `eval-jss = eval.cli:main`.
Contract: `specs/002-eval-jss-harness/contracts/cli.md`.

Subcommands (stubbed or wired):
- `init`          — Phase A (wired in T009)
- `scan`          — Phase A (wired in T016)
- `human-review`  — Phase A (wired in T018)
- `review`        — Phase B (wired in T023)
- `report`        — Phase A (wired in T020, extended in Phase B)
- `corpus fetch`  — Phase B (wired in T028)
- `corpus status` — Phase B (wired in T028)
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from eval import db

DEFAULT_DB = Path("eval/eval.db")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--db",
    "db_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_DB),
    show_default=True,
    help="Path to the eval-jss SQLite database.",
)
@click.pass_context
def cli(ctx: click.Context, db_path: Path) -> None:
    """Precision harness for the jss-lint linter."""
    ctx.ensure_object(dict)
    ctx.obj["db"] = Path(db_path)


@cli.command("init")
@click.pass_context
def init_cmd(ctx: click.Context) -> None:
    """Create (or reconcile) the eval-jss SQLite schema."""
    db_path: Path = ctx.obj["db"]
    try:
        db.init(db_path)
    except OSError as err:
        click.echo(f"eval-jss: init failed: {err}", err=True)
        ctx.exit(2)
    click.echo(f"eval-jss: database ready at {db_path}")


@cli.command("scan")
@click.option(
    "--corpus",
    "corpus_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("examples"),
    show_default=True,
)
@click.option("--batch-size", type=int, default=None)
@click.option("--force", is_flag=True, default=False)
@click.pass_context
def scan_cmd(
    ctx: click.Context, corpus_dir: Path, batch_size: int | None, force: bool
) -> None:
    """Run jss-lint on each paper in the corpus and persist violations."""
    from eval import scan as scan_mod

    code = scan_mod.run(
        db_path=ctx.obj["db"],
        corpus_dir=corpus_dir,
        batch_size=batch_size,
        force=force,
    )
    ctx.exit(code)


@cli.command("human-review")
@click.option("--limit", type=int, default=None)
@click.option("--rule", "rule_id", type=str, default=None)
@click.option("--reviewer", type=str, default=None)
@click.option(
    "--skip-listed",
    is_flag=True,
    default=False,
    help="Review only rules on the AI skip list (rules whose violations bypass the classifier).",
)
@click.option(
    "--skip-list",
    "skip_list_path",
    type=click.Path(path_type=Path),
    default=Path("eval/review-skip-list.toml"),
    show_default=True,
    help="Skip-list TOML consulted when --skip-listed is set.",
)
@click.option(
    "--reverify-ai",
    is_flag=True,
    default=False,
    help=(
        "Widen the review queue to AI-labelled rows so the human can "
        "spot-check or override AI verdicts. Use for rules whose "
        "precision currently depends entirely on AI labels."
    ),
)
@click.pass_context
def human_review_cmd(
    ctx: click.Context,
    limit: int | None,
    rule_id: str | None,
    reviewer: str | None,
    skip_listed: bool,
    skip_list_path: Path,
    reverify_ai: bool,
) -> None:
    """Interactively label unlabelled and uncertain violations."""
    from eval import human_review as human_review_mod

    code = human_review_mod.run(
        db_path=ctx.obj["db"],
        limit=limit,
        rule_id=rule_id,
        reviewer=reviewer,
        skip_listed=skip_listed,
        skip_list_path=skip_list_path,
        reverify_ai=reverify_ai,
    )
    ctx.exit(code)


@cli.command("review")
@click.option("--limit", type=int, default=None)
@click.option("--confidence-threshold", type=float, default=0.8, show_default=True)
@click.option("--model", type=str, default="qwen3-30b-a3b", show_default=True)
@click.option("--base-url", type=str, default="http://localhost:8080", show_default=True)
@click.option(
    "--skip-list",
    type=click.Path(path_type=Path),
    default=Path("eval/review-skip-list.toml"),
    show_default=True,
)
@click.option(
    "--routing",
    "routing_path",
    type=click.Path(path_type=Path),
    default=None,
    help=(
        "Per-rule model routing TOML (eval/review-routing.toml). "
        "When set, supersedes --model/--base-url and routes each rule "
        "to its best-performing model per the gold benchmark."
    ),
)
@click.pass_context
def review_cmd(
    ctx: click.Context,
    limit: int | None,
    confidence_threshold: float,
    model: str,
    base_url: str,
    skip_list: Path,
    routing_path: Path | None,
) -> None:
    """Delegate labelling of unlabelled violations to a local LLM."""
    from eval import review as review_mod

    code = review_mod.run(
        db_path=ctx.obj["db"],
        limit=limit,
        confidence_threshold=confidence_threshold,
        model=model,
        base_url=base_url,
        skip_list_path=Path(skip_list),
        routing_path=routing_path,
    )
    ctx.exit(code)


@cli.command("report")
@click.option("--by-source", is_flag=True, default=False)
@click.option(
    "--by-format",
    is_flag=True,
    default=False,
    help="Partition precision by violation file suffix (tex | bib | rnw | rmd).",
)
@click.option(
    "--diff",
    is_flag=True,
    default=False,
    help=(
        "Render per-rule TP/FP/precision deltas between the two latest "
        "iterations in precision-history.db."
    ),
)
@click.option(
    "--against",
    type=int,
    default=None,
    help="With --diff: compare against this iteration id (default: previous).",
)
@click.option(
    "--history-db",
    "history_db",
    type=click.Path(path_type=Path),
    default=Path("eval/precision-history.db"),
    show_default=True,
    help="Precision-history DB consulted for --diff.",
)
@click.option(
    "--pinned-only",
    is_flag=True,
    default=False,
    help="Restrict to violations from the manifest's pinned vignette_file per paper.",
)
@click.option(
    "--manifest",
    "manifest_path",
    type=click.Path(path_type=Path),
    default=Path("eval/corpus-manifest.csv"),
    show_default=True,
    help="Manifest consulted when --pinned-only is set.",
)
@click.option(
    "--corpus",
    "corpus_dir",
    type=click.Path(path_type=Path, file_okay=False),
    default=Path("examples"),
    show_default=True,
    help="Corpus root consulted when --pinned-only is set (must match the scan invocation).",
)
@click.option(
    "--csv",
    "csv_path",
    type=str,
    default=None,
    help="Append precision history to this CSV (Phase B default: eval/report.csv; '-' disables).",
)
@click.pass_context
def report_cmd(
    ctx: click.Context,
    by_source: bool,
    by_format: bool,
    diff: bool,
    against: int | None,
    history_db: Path,
    pinned_only: bool,
    manifest_path: Path,
    corpus_dir: Path,
    csv_path: str | None,
) -> None:
    """Print the per-rule precision table."""
    if by_source and by_format:
        click.echo("eval-jss: --by-source and --by-format are mutually exclusive", err=True)
        ctx.exit(2)

    from eval import report as report_mod
    from eval.corpus import ManifestError

    try:
        code = report_mod.run(
            db_path=ctx.obj["db"],
            by_source=by_source,
            by_format=by_format,
            csv_path=csv_path,
            pinned_only=pinned_only,
            manifest_path=manifest_path if pinned_only else None,
            corpus_dir=corpus_dir if pinned_only else None,
            diff=diff,
            history_db=history_db,
            against=against,
        )
    except (FileNotFoundError, ManifestError) as err:
        click.echo(f"eval-jss: {err}", err=True)
        ctx.exit(2)
    ctx.exit(code)


@cli.command("benchmark")
@click.option(
    "--model",
    "models",
    multiple=True,
    help="Model spec as `name:http://host:port`. Repeat for multiple models.",
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Cap the gold set size (for quick smoke runs).",
)
@click.option(
    "--write-json",
    "write_json",
    type=click.Path(path_type=Path),
    default=None,
    help="Append per-row outcomes (one JSON line per model) to this file.",
)
@click.pass_context
def benchmark_cmd(
    ctx: click.Context,
    models: tuple[str, ...],
    limit: int | None,
    write_json: Path | None,
) -> None:
    """Score AI models against the human-labelled gold set."""
    from eval import benchmark as bench_mod

    try:
        specs = [bench_mod.ModelSpec.parse(m) for m in models]
    except ValueError as err:
        click.echo(f"eval-jss: {err}", err=True)
        ctx.exit(2)
    code = bench_mod.run(
        db_path=ctx.obj["db"],
        models=specs,
        limit=limit,
        write_json=write_json,
    )
    ctx.exit(code)


@cli.group("jss-archive")
def jss_archive_group() -> None:
    """Scrape and consult the JSS archive (OAI-PMH)."""


@jss_archive_group.command("sync")
@click.option(
    "--cache",
    "cache_path",
    type=click.Path(path_type=Path),
    default=Path("eval/jss-archive.json"),
    show_default=True,
)
@click.option(
    "--since",
    type=str,
    default=None,
    help="ISO-8601 date (YYYY-MM-DD); incremental refresh from this date.",
)
@click.pass_context
def jss_archive_sync_cmd(
    ctx: click.Context, cache_path: Path, since: str | None,
) -> None:
    """Fetch every JSS paper's metadata via OAI-PMH and cache it."""
    from eval import jss_archive

    code = jss_archive.run_sync(cache_path=cache_path, since=since)
    ctx.exit(code)


@jss_archive_group.command("packages")
@click.option(
    "--cache",
    "cache_path",
    type=click.Path(path_type=Path),
    default=Path("eval/jss-archive.json"),
    show_default=True,
)
@click.option(
    "--cran-matched/--all-candidates",
    default=True,
    help=(
        "Filter to candidates that actually exist on CRAN's PACKAGES "
        "index (default), or print every candidate the heuristic "
        "extracted (includes false positives like 'A-optimality')."
    ),
)
@click.pass_context
def jss_archive_packages_cmd(
    ctx: click.Context, cache_path: Path, cran_matched: bool,
) -> None:
    """List CRAN package candidates extracted from the JSS archive."""
    from eval import jss_archive

    code = jss_archive.run_packages(
        cache_path=cache_path, cran_matched=cran_matched,
    )
    ctx.exit(code)


@cli.group("cran-github")
def cran_github_group() -> None:
    """Scrape and consult the GitHub mirror of CRAN (`github.com/cran`)."""


@cran_github_group.command("sync")
@click.option(
    "--cache",
    "cache_path",
    type=click.Path(path_type=Path),
    default=Path("eval/cran-github.json"),
    show_default=True,
)
@click.pass_context
def cran_github_sync_cmd(ctx: click.Context, cache_path: Path) -> None:
    """Fetch JSS-counterpart vignettes via GitHub Code Search and cache them."""
    from eval import cran_github

    code = cran_github.run_sync(cache_path=cache_path)
    ctx.exit(code)


@cran_github_group.command("packages")
@click.option(
    "--cache",
    "cache_path",
    type=click.Path(path_type=Path),
    default=Path("eval/cran-github.json"),
    show_default=True,
)
@click.pass_context
def cran_github_packages_cmd(ctx: click.Context, cache_path: Path) -> None:
    """List distinct package names from the cran-github cache."""
    from eval import cran_github

    code = cran_github.run_packages(cache_path=cache_path)
    ctx.exit(code)


@cli.group("iterate")
def iterate_group() -> None:
    """Eval-improve loop bookkeeping."""


@iterate_group.command("record")
@click.argument("label", type=str)
@click.option("--note", type=str, default=None, help="Freeform annotation for this snapshot.")
@click.option(
    "--history-db",
    "history_db",
    type=click.Path(path_type=Path),
    default=Path("eval/precision-history.db"),
    show_default=True,
)
@click.option(
    "--log",
    "log_path",
    type=click.Path(path_type=Path),
    default=Path("eval/improvement-log.md"),
    show_default=True,
)
@click.option(
    "--manifest",
    "manifest_path",
    type=click.Path(path_type=Path),
    default=Path("eval/corpus-manifest.csv"),
    show_default=True,
)
@click.option(
    "--corpus",
    "corpus_dir",
    type=click.Path(path_type=Path, file_okay=False),
    default=Path("examples"),
    show_default=True,
)
@click.pass_context
def iterate_record_cmd(
    ctx: click.Context,
    label: str,
    note: str | None,
    history_db: Path,
    log_path: Path,
    manifest_path: Path,
    corpus_dir: Path,
) -> None:
    """Snapshot full + pinned stats into precision-history.db and the log."""
    from eval import iterate as iterate_mod
    from eval.corpus import ManifestError

    try:
        code = iterate_mod.run(
            eval_db=ctx.obj["db"],
            history_db=history_db,
            log_path=log_path,
            manifest_path=manifest_path,
            corpus_dir=corpus_dir,
            label=label,
            note=note,
        )
    except (FileNotFoundError, ManifestError) as err:
        click.echo(f"eval-jss: {err}", err=True)
        ctx.exit(2)
    ctx.exit(code)


@iterate_group.command("plan")
@click.option(
    "--history-db",
    "history_db",
    type=click.Path(path_type=Path),
    default=Path("eval/precision-history.db"),
    show_default=True,
)
@click.option(
    "--manifest",
    "manifest_path",
    type=click.Path(path_type=Path),
    default=Path("eval/corpus-manifest.csv"),
    show_default=True,
)
@click.option(
    "--corpus",
    "corpus_dir",
    type=click.Path(path_type=Path, file_okay=False),
    default=Path("examples"),
    show_default=True,
)
@click.option(
    "--policy",
    "policy_path",
    type=click.Path(path_type=Path),
    default=Path("eval/iteration-policy.toml"),
    show_default=True,
)
@click.pass_context
def iterate_plan_cmd(
    ctx: click.Context,
    history_db: Path,
    manifest_path: Path,
    corpus_dir: Path,
    policy_path: Path,
) -> None:
    """Compute the next loop action and emit it as JSON.

    Pure decision function — reads policy + history + current report,
    emits ``{"action": "fix_rule"|"grow_corpus"|"rebenchmark"|"stop",
    "target": ..., "reason": ...}`` to stdout. The orchestrator (a
    subagent or shell loop) executes the action and re-runs ``plan``
    on the next iteration.
    """
    from eval import iterate as iterate_mod
    from eval.corpus import ManifestError

    try:
        code = iterate_mod.run_plan(
            eval_db=ctx.obj["db"],
            history_db=history_db,
            manifest_path=manifest_path,
            corpus_dir=corpus_dir,
            policy_path=policy_path,
        )
    except (FileNotFoundError, ManifestError) as err:
        click.echo(f"eval-jss: {err}", err=True)
        ctx.exit(2)
    ctx.exit(code)


@iterate_group.command("guard")
@click.option(
    "--history-db",
    "history_db",
    type=click.Path(path_type=Path),
    default=Path("eval/precision-history.db"),
    show_default=True,
)
@click.option(
    "--manifest",
    "manifest_path",
    type=click.Path(path_type=Path),
    default=Path("eval/corpus-manifest.csv"),
    show_default=True,
)
@click.option(
    "--corpus",
    "corpus_dir",
    type=click.Path(path_type=Path, file_okay=False),
    default=Path("examples"),
    show_default=True,
)
@click.option(
    "--policy",
    "policy_path",
    type=click.Path(path_type=Path),
    default=Path("eval/iteration-policy.toml"),
    show_default=True,
)
@click.pass_context
def iterate_guard_cmd(
    ctx: click.Context,
    history_db: Path,
    manifest_path: Path,
    corpus_dir: Path,
    policy_path: Path,
) -> None:
    """Block on per-rule precision regressions vs. the last iteration.

    Computes the current precision table, compares against the most
    recently recorded iteration, and exits non-zero when one or more
    previously-passing rules dropped past the
    ``precision_drop_tolerance_pp`` threshold from
    ``eval/iteration-policy.toml``. Wire into autonomous loops or
    pre-commit hooks to refuse recording / committing a regression.
    """
    from eval import iterate as iterate_mod
    from eval.corpus import ManifestError

    try:
        code = iterate_mod.run_guard(
            eval_db=ctx.obj["db"],
            history_db=history_db,
            manifest_path=manifest_path,
            corpus_dir=corpus_dir,
            policy_path=policy_path,
        )
    except (FileNotFoundError, ManifestError) as err:
        click.echo(f"eval-jss: {err}", err=True)
        ctx.exit(2)
    ctx.exit(code)


@iterate_group.command("refresh")
@click.option(
    "--corpus",
    "corpus_dir",
    type=click.Path(path_type=Path, file_okay=False),
    default=Path("examples"),
    show_default=True,
)
@click.option(
    "--save-orphans",
    "orphans_path",
    type=click.Path(path_type=Path),
    default=None,
    help=(
        "JSON dump path for labels whose matching violation no longer fires. "
        "Default: `eval/orphans/<utc-timestamp>.json` (set automatically). "
        "Use --no-save-orphans to disable."
    ),
)
@click.option(
    "--no-save-orphans",
    is_flag=True,
    default=False,
    help="Disable the default orphan dump.",
)
@click.pass_context
def iterate_refresh_cmd(
    ctx: click.Context,
    corpus_dir: Path,
    orphans_path: Path | None,
    no_save_orphans: bool,
) -> None:
    """Wipe + rescan the corpus and restore labelled verdicts.

    Use after a rule-logic change so the precision report reflects
    the new behaviour without losing existing TP/FP labels. Labels
    whose violation no longer fires are reported and dumped to
    `eval/orphans/<utc-timestamp>.json` by default — that file is
    the only way to recover labels if the rule change is later rolled
    back.
    """
    from eval import iterate as iterate_mod

    code = iterate_mod.run_refresh(
        eval_db=ctx.obj["db"],
        corpus_dir=corpus_dir,
        orphans_path=orphans_path,
        no_save_orphans=no_save_orphans,
    )
    ctx.exit(code)


@iterate_group.command("apply-orphans")
@click.argument(
    "orphans_path",
    type=click.Path(path_type=Path, dir_okay=False),
)
@click.pass_context
def iterate_apply_orphans_cmd(
    ctx: click.Context, orphans_path: Path,
) -> None:
    """Re-apply labels from an orphan dump onto current violations.

    Use after rolling back a rule fix so labels whose violations
    re-appear in the current scan get their verdicts restored.
    """
    from eval import iterate as iterate_mod

    code = iterate_mod.run_apply_orphans(
        eval_db=ctx.obj["db"], orphans_path=orphans_path,
    )
    ctx.exit(code)


@cli.group("corpus")
def corpus_group() -> None:
    """Reproduce the corpus from the pinned manifest (Phase B)."""


@corpus_group.command("fetch")
@click.option(
    "--manifest",
    "manifest_path",
    type=click.Path(path_type=Path),
    default=Path("eval/corpus-manifest.csv"),
    show_default=True,
)
@click.option(
    "--target",
    "target_dir",
    type=click.Path(path_type=Path, file_okay=False),
    default=Path("examples"),
    show_default=True,
)
@click.option(
    "--gaps",
    "gaps_path",
    type=click.Path(path_type=Path),
    default=Path("eval/corpus-manifest-gaps.csv"),
    show_default=True,
)
@click.pass_context
def corpus_fetch_cmd(
    ctx: click.Context,
    manifest_path: Path,
    target_dir: Path,
    gaps_path: Path,
) -> None:
    """Materialise every manifest row from an immutable distribution URL."""
    from eval import corpus as corpus_mod

    code = corpus_mod.run_fetch(
        manifest_path=manifest_path,
        target_dir=target_dir,
        gaps_path=gaps_path,
    )
    ctx.exit(code)


@corpus_group.command("suggest")
@click.option(
    "--manifest",
    "manifest_path",
    type=click.Path(path_type=Path),
    default=Path("eval/corpus-manifest.csv"),
    show_default=True,
)
@click.option("--limit", type=int, default=50, show_default=True)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Deterministic RNG seed for reproducible picks. Default: nondeterministic.",
)
@click.option(
    "--verify/--no-verify",
    default=True,
    show_default=True,
    help="Probe each candidate's CRAN landing page to confirm it ships a vignette.",
)
@click.option(
    "--from-jss-archive/--no-from-jss-archive",
    default=True,
    show_default=True,
    help=(
        "Restrict the candidate pool to JSS-archive-matched packages "
        "(eval/jss-archive.json). Run `eval-jss jss-archive sync` "
        "first to populate the cache. With --no-from-jss-archive, "
        "fall back to a random sample over CRAN's PACKAGES index."
    ),
)
@click.option(
    "--jss-archive-cache",
    "jss_archive_cache",
    type=click.Path(path_type=Path),
    default=Path("eval/jss-archive.json"),
    show_default=True,
    help="JSS-archive cache file (used when --from-jss-archive is on).",
)
@click.option(
    "--from-cran-github/--no-from-cran-github",
    default=True,
    show_default=True,
    help=(
        "Also consider candidates discovered via GitHub Code Search of "
        "the cran org (eval/cran-github.json). Run `eval-jss cran-github "
        "sync` first to populate the cache. Unioned with the jss-archive "
        "pool when both flags are on."
    ),
)
@click.option(
    "--cran-github-cache",
    "cran_github_cache",
    type=click.Path(path_type=Path),
    default=Path("eval/cran-github.json"),
    show_default=True,
    help="cran-github cache file (used when --from-cran-github is on).",
)
@click.option(
    "--jss-only/--no-jss-only",
    default=True,
    show_default=True,
    help=(
        "Only suggest packages whose source tarball ships a vignette that "
        "loads the `jss` LaTeX class AND cites Journal of Statistical "
        "Software (in the vignette or a sibling .bib). Future corpus rows "
        "must satisfy this — see memory/feedback_corpus_jss_only.md."
    ),
)
@click.pass_context
def corpus_suggest_cmd(
    ctx: click.Context,
    manifest_path: Path,
    limit: int,
    seed: int | None,
    verify: bool,
    jss_only: bool,
    from_jss_archive: bool,
    jss_archive_cache: Path,
    from_cran_github: bool,
    cran_github_cache: Path,
) -> None:
    """Print CRAN packages with vignettes that are not yet in the manifest."""
    from eval import corpus as corpus_mod

    code = corpus_mod.run_suggest(
        manifest_path=manifest_path,
        limit=limit,
        seed=seed,
        from_jss_archive=from_jss_archive,
        jss_archive_cache=jss_archive_cache,
        from_cran_github=from_cran_github,
        cran_github_cache=cran_github_cache,
        verify=verify,
        jss_only=jss_only,
    )
    ctx.exit(code)


@corpus_group.command("status")
@click.option(
    "--manifest",
    "manifest_path",
    type=click.Path(path_type=Path),
    default=Path("eval/corpus-manifest.csv"),
    show_default=True,
)
@click.option(
    "--target",
    "target_dir",
    type=click.Path(path_type=Path, file_okay=False),
    default=Path("examples"),
    show_default=True,
)
@click.pass_context
def corpus_status_cmd(
    ctx: click.Context, manifest_path: Path, target_dir: Path
) -> None:
    """Show which manifest rows are materialised, pending, or mismatched."""
    from eval import corpus as corpus_mod

    code = corpus_mod.run_status(manifest_path=manifest_path, target_dir=target_dir)
    ctx.exit(code)


def main(argv: list[str] | None = None) -> int:
    """Console-script entry point.

    With `standalone_mode=False`, click catches `ctx.exit(N)` internally
    and returns `N` as this function's return value, which we forward to
    the OS. If the command returns nothing, default to 0.
    """
    try:
        result = cli.main(args=argv, standalone_mode=False)
    except click.ClickException as err:
        err.show()
        return err.exit_code
    return int(result) if isinstance(result, int) else 0


if __name__ == "__main__":
    sys.exit(main())
