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
@click.pass_context
def human_review_cmd(
    ctx: click.Context, limit: int | None, rule_id: str | None, reviewer: str | None
) -> None:
    """Interactively label unlabelled and uncertain violations."""
    from eval import human_review as human_review_mod

    code = human_review_mod.run(
        db_path=ctx.obj["db"],
        limit=limit,
        rule_id=rule_id,
        reviewer=reviewer,
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
@click.pass_context
def review_cmd(
    ctx: click.Context,
    limit: int | None,
    confidence_threshold: float,
    model: str,
    base_url: str,
    skip_list: Path,
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
    )
    ctx.exit(code)


@cli.command("report")
@click.option("--by-source", is_flag=True, default=False)
@click.option(
    "--csv",
    "csv_path",
    type=str,
    default=None,
    help="Append precision history to this CSV (Phase B default: eval/report.csv; '-' disables).",
)
@click.pass_context
def report_cmd(ctx: click.Context, by_source: bool, csv_path: str | None) -> None:
    """Print the per-rule precision table."""
    from eval import report as report_mod

    code = report_mod.run(
        db_path=ctx.obj["db"],
        by_source=by_source,
        csv_path=csv_path,
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
