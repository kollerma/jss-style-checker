"""Command-line interface for texlint, exposed as ``jss-lint``.

See :doc:`specs/001-linter-foundation/contracts/cli.md` for the invocation
surface. The main pipeline is: parse click options → merge config →
parse each input file → load the selected journal → run the rule engine →
dispatch to a renderer → exit with the appropriate status.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click

from . import __version__
from .api import (
    InvalidJournalError,
    JournalNotFoundError,
    ParsedDocument,
    ToolConfig,
)
from .config import load as load_config
from .core.engine import UnsupportedSuffixError, load_journal, parse_document, run

_SUPPORTED_SUFFIXES = {".tex", ".ltx", ".bib", ".rnw", ".rmd"}
_PARSE_RULE_ID = "JSS-PARSE-000"

_JOURNAL_CHOICES: tuple[str, ...] | None = None  # resolved lazily; click accepts any string


def _eprint(message: str) -> None:
    click.echo(message, err=True)


def _expand_directory(path: Path) -> list[Path]:
    """All lintable files under *path*, recursively, in deterministic
    sorted order (report byte-stability)."""
    return sorted(
        p
        for p in path.rglob("*")
        if p.is_file() and p.suffix.lower() in _SUPPORTED_SUFFIXES
    )


def _parse_inputs(paths: tuple[str, ...]) -> tuple[ParsedDocument | None, int]:
    """Parse each input file. Return (document, exit_code_if_any).

    A directory argument expands recursively to every lintable file
    beneath it (``jss-lint .`` is the natural first invocation); an
    empty expansion is exit-2 with a clear message. Explicit file
    arguments keep strict suffix validation.

    The exit-code is 2 when any path is missing or has an unsupported
    suffix. Delegates to :func:`texlint.core.engine.parse_document` for
    actual parsing; extension dispatch supports ``.tex``, ``.ltx``,
    ``.bib``, ``.Rnw``, and ``.Rmd``.
    """
    path_objs: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            found = _expand_directory(path)
            if not found:
                _eprint(
                    f"jss-lint: no lintable files under {path} "
                    f"(looked for: {', '.join(sorted(_SUPPORTED_SUFFIXES))})"
                )
                return None, 2
            path_objs.extend(found)
            continue
        if path.suffix.lower() not in _SUPPORTED_SUFFIXES:
            _eprint(
                f"jss-lint: unsupported file extension '{path.suffix}' for {path} "
                f"(expected one of: {', '.join(sorted(_SUPPORTED_SUFFIXES))})"
            )
            return None, 2
        if not path.exists():
            _eprint(f"jss-lint: file not found: {path}")
            return None, 2
        path_objs.append(path)

    try:
        return parse_document(path_objs), 0
    except UnsupportedSuffixError as exc:
        _eprint(f"jss-lint: {exc}")
        return None, 2


def _dispatch_renderer(output: str, report: Any, cfg: ToolConfig) -> None:
    if output == "terminal":
        from .output.terminal import render as render_terminal

        render_terminal(report, cfg)
    elif output == "json":
        from .output.json_output import render as render_json

        render_json(report, cfg)
    elif output == "html":
        from .output.html_output import render as render_html

        render_html(report, cfg)
    elif output == "sarif":
        from .output.sarif import render as render_sarif

        render_sarif(report, cfg)
    else:  # pragma: no cover - click Choice prevents this
        _eprint(f"jss-lint: unknown output format {output!r}")
        sys.exit(2)


_SEVERITY_RANK: dict[str, int] = {"info": 0, "warning": 1, "error": 2}


def _determine_exit_code(report: Any, fail_on: str = "info") -> int:
    """Exit 2 if any *error-severity* parse failure is present; else 1
    if any violation at or above the ``fail_on`` severity; else 0.

    Error-severity parse failures dominate style violations because the
    report is incomplete when the parser could not process a file — see
    contracts/cli.md §Exit codes. Warning-severity ``JSS-PARSE-000``
    findings mark a *degraded* parse (the file was recovered and fully
    linted, e.g. via an encoding fallback or duplicate-bib-field
    recovery); those obey the normal ``fail_on`` threshold like any
    other finding.

    ``fail_on`` is the minimum severity that flips the exit code:
    ``"warning"`` (the default) lets info-severity advisories (e.g.
    the missing-DOI rule) pass CI; ``"info"`` (the pre-0.2 default)
    fails on any violation; ``"error"`` fails only on errors.
    Violations below the threshold are still rendered — the policy
    affects the exit code only.
    """
    if any(
        v.rule_id == _PARSE_RULE_ID and v.severity.value == "error"
        for v in report.violations
    ):
        return 2
    threshold = _SEVERITY_RANK.get(fail_on, 0)
    if any(
        _SEVERITY_RANK.get(v.severity.value, 0) >= threshold
        for v in report.violations
    ):
        return 1
    return 0


def _lint_paths(paths: tuple[str, ...]) -> tuple[Any, ToolConfig]:
    """Shared lint pipeline used by ``init`` and ``report`` subcommands.

    Mirrors the bare-PATHS branch in :func:`main`: load config, parse the
    inputs, load the journal module, and run the rule engine. On any
    failure it ``sys.exit``s with the appropriate code so callers do not
    need to re-implement error handling.
    """
    report, _doc, cfg = _lint_paths_with_doc(paths)
    return report, cfg


def _lint_paths_with_doc(
    paths: tuple[str, ...],
) -> tuple[Any, ParsedDocument, ToolConfig]:
    """Like :func:`_lint_paths` but also returns the parsed document so
    callers (spec-015 ``report`` subcommand) can introspect the
    preamble for title / author."""
    try:
        cfg = load_config({}, Path.cwd())
    except Exception as exc:  # pragma: no cover - defensive
        _eprint(f"jss-lint: failed to load .jss-lint.toml: {exc}")
        sys.exit(2)

    document, code = _parse_inputs(paths)
    if document is None:
        sys.exit(code)

    try:
        journal_module = load_journal(cfg.journal)
    except (JournalNotFoundError, InvalidJournalError) as exc:
        _eprint(f"jss-lint: {exc}")
        sys.exit(2)

    return run(cfg, document, journal_module), document, cfg


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    name="jss-lint",
    invoke_without_command=True,
)
@click.version_option(__version__, prog_name="jss-lint")
@click.option(
    "--journal",
    "journal",
    default=None,
    help="Journal identifier to apply (default: jss).",
)
@click.option(
    "--mode",
    "mode",
    type=click.Choice(["author", "reviewer"], case_sensitive=False),
    default=None,
    help="Output emphasis (default: author).",
)
@click.option(
    "--output",
    "output",
    type=click.Choice(["terminal", "json", "html", "sarif"], case_sensitive=False),
    default=None,
    help="Renderer for the compliance report (default: terminal).",
)
@click.option(
    "--source-root",
    "source_root",
    type=click.Path(file_okay=False, dir_okay=True, path_type=str),
    default=None,
    help="Base directory for SARIF artifact URIs (default: current working directory).",
)
@click.option(
    "--ignore-rules",
    "ignore_rules",
    default=None,
    help="Comma-separated rule ids to suppress.",
)
@click.option(
    "--min-confidence",
    "min_confidence",
    type=click.Choice(["low", "medium", "high"], case_sensitive=False),
    default=None,
    help=(
        "Skip rules whose measured-precision confidence tier is below "
        "this floor (default: low — run everything)."
    ),
)
@click.option(
    "--fail-on",
    "fail_on",
    type=click.Choice(["error", "warning", "info"], case_sensitive=False),
    default=None,
    help=(
        "Minimum violation severity that exits 1 (default: warning — "
        "info-severity advisories pass). Lower-severity findings are "
        "still reported."
    ),
)
@click.option(
    "-v",
    "--verbose",
    "verbose",
    is_flag=True,
    default=None,
    help="Enable diagnostic output on stderr.",
)
@click.option(
    "--fix",
    "fix",
    is_flag=True,
    default=False,
    help="Apply auto-fixes (spec 008). Atomic write per file.",
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="With --fix: print proposed fixes as a unified diff; do not write.",
)
@click.option(
    "--apply",
    "apply_interactive",
    is_flag=True,
    default=False,
    help="With --fix: prompt [y/n/a/q] per fix.",
)
@click.option(
    "--fix-rule",
    "fix_rules",
    multiple=True,
    help="Repeatable; limits --fix to the named rule ids.",
)
@click.option(
    "--no-resolve",
    "no_resolve",
    is_flag=True,
    default=False,
    help=(
        "Skip recursive \\input / \\include / \\subfile / "
        "\\bibliography resolution (currently a no-op until "
        "auto-resolve ships)."
    ),
)
@click.argument("paths", nargs=-1, type=click.Path(path_type=str))
@click.pass_context
def main(
    ctx: click.Context,
    journal: str | None,
    mode: str | None,
    output: str | None,
    source_root: str | None,
    ignore_rules: str | None,
    min_confidence: str | None,
    fail_on: str | None,
    verbose: bool | None,
    fix: bool,
    dry_run: bool,
    apply_interactive: bool,
    fix_rules: tuple[str, ...],
    no_resolve: bool,
    paths: tuple[str, ...],
) -> None:
    """Lint LaTeX/BibTeX manuscripts against journal style guides.

    With no subcommand, runs the read-only lint pass over the given
    paths (the historic ``jss-lint <PATHS>`` invocation). The command
    is also a Click group so that follow-ups such as ``explain``,
    ``init``, ``report``, ``diff``, and ``lsp`` can attach as
    subcommands without breaking the bare-PATHS surface — the seam is
    ``invoke_without_command=True``.
    """
    # When a subcommand is invoked, defer to its callback. The group
    # callback still runs first (Click always invokes the parent), so
    # we early-return before doing any lint work.
    if ctx.invoked_subcommand is not None:
        return

    # Manual subcommand dispatch: the group keeps a ``paths`` nargs=-1
    # argument so that the historic ``jss-lint <PATHS>`` invocation
    # works without a ``lint`` prefix. As a side-effect, Click parses
    # subcommand names into ``paths`` instead of dispatching. Detect
    # the case here and forward to the matching subcommand.
    if paths and paths[0] in main.commands:
        sub = main.commands[paths[0]]
        sub_ctx = sub.make_context(paths[0], list(paths[1:]), parent=ctx)
        with sub_ctx:
            sub.invoke(sub_ctx)
        return

    if not paths:
        _eprint("jss-lint: at least one FILE argument is required.")
        sys.exit(2)

    cli_overrides: dict[str, Any] = {}
    if journal is not None:
        cli_overrides["journal"] = journal
    if mode is not None:
        cli_overrides["mode"] = mode.lower()
    if output is not None:
        cli_overrides["output"] = output.lower()
    if source_root is not None:
        cli_overrides["source_root"] = Path(source_root)
    if ignore_rules is not None:
        cli_overrides["ignore_rules"] = ignore_rules
    if min_confidence is not None:
        cli_overrides["min_confidence"] = min_confidence.lower()
    if fail_on is not None:
        cli_overrides["fail_on"] = fail_on.lower()
    if verbose is not None:
        cli_overrides["verbose"] = verbose
    # Spec 013 follow-up: ``--no-resolve`` is a reserved flag. The
    # CLI does not currently auto-resolve, so the flag is wired
    # through ``cli_overrides`` but has no observable effect today.
    # Reserving it now lets users start scripting against the flag
    # before auto-resolve ships.
    if no_resolve:
        cli_overrides["no_resolve"] = True

    try:
        cfg = load_config(cli_overrides, Path.cwd())
    except Exception as exc:  # pragma: no cover - defensive; tomllib errors look like this
        _eprint(f"jss-lint: failed to load .jss-lint.toml: {exc}")
        sys.exit(2)

    document, code = _parse_inputs(paths)
    if document is None:
        sys.exit(code)

    try:
        journal_module = load_journal(cfg.journal)
    except JournalNotFoundError as exc:
        _eprint(f"jss-lint: {exc}")
        sys.exit(2)
    except InvalidJournalError as exc:
        _eprint(f"jss-lint: {exc}")
        sys.exit(2)

    report = run(cfg, document, journal_module)

    # Spec 008: --fix / --dry-run / --apply / --fix-rule.
    if dry_run and not fix:
        _eprint("jss-lint: --dry-run requires --fix")
        sys.exit(2)
    if apply_interactive and not fix:
        _eprint("jss-lint: --apply requires --fix")
        sys.exit(2)
    if dry_run and apply_interactive:
        _eprint("jss-lint: --dry-run and --apply are mutually exclusive")
        sys.exit(2)
    if fix:
        from .core.fixer import apply_fixes

        # Validate --fix-rule values against known rules from the
        # current report's catalogue.
        if fix_rules:
            known_ids = {v.rule_id for v in report.violations}
            # Also accept any catalogue rule the loaded journal exports.
            for r in journal_module.rules():
                known_ids.add(r.id)
            for rid in fix_rules:
                if rid not in known_ids:
                    _eprint(f"jss-lint: unknown --fix-rule {rid!r}")
                    sys.exit(2)
            scope: frozenset[str] | None = frozenset(fix_rules)
        else:
            scope = None
        if dry_run:
            fix_mode = "dry-run"
        elif apply_interactive:
            fix_mode = "interactive"
        else:
            fix_mode = "write"
        fix_report = apply_fixes(report, mode=fix_mode, rules=scope)
        if fix_report.rejected:
            sys.exit(2)

    _dispatch_renderer(cfg.output, report, cfg)
    sys.exit(_determine_exit_code(report, cfg.fail_on))


@main.command(name="explain")
@click.argument("rule_id", required=False, default=None)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["terminal", "markdown"], case_sensitive=False),
    default="terminal",
    help="Output format (default: terminal).",
)
@click.option(
    "--example",
    "example",
    is_flag=True,
    default=False,
    help="Reserved for fixture pull-through; currently no-op.",
)
def explain_cmd(rule_id: str | None, fmt: str, example: bool) -> None:
    """Render a rule explanation (or a per-category listing).

    Spec 009. ``--example`` is reserved for fixture pull-through and is a
    no-op in v1.
    """
    from . import explain as _explain

    fmt_norm = fmt.lower()
    try:
        out = _explain.render(rule_id, fmt=fmt_norm)
    except KeyError:
        unknown = (rule_id or "").strip().upper()
        _eprint(f"error: unknown rule id {unknown}")
        suggestions = _explain.did_you_mean(unknown)
        if suggestions:
            _eprint(f"did you mean: {', '.join(suggestions)}")
        sys.exit(2)
    click.echo(out, nl=False)


@main.command(name="init")
@click.argument(
    "path",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=str),
)
@click.option("--force", "force", is_flag=True, default=False)
@click.option("--dry-run", "dry_run", is_flag=True, default=False)
@click.option("--threshold", "threshold", type=float, default=0.90)
def init_cmd(path: str, force: bool, dry_run: bool, threshold: float) -> None:
    """Initialise a ``.jss-lint.toml`` for a manuscript directory.

    Spec 010. Lints PATH first, then writes (or previews) a starter
    config beside it.
    """
    from . import init as _init

    target = Path(path)
    if target.is_dir():
        target_dir = target
        # Lint every supported source file in the directory (single
        # level — matches the historic spec-010 lint surface).
        candidates = tuple(
            sorted(
                str(p)
                for p in target.iterdir()
                if p.is_file() and p.suffix.lower() in _SUPPORTED_SUFFIXES
            )
        )
    else:
        target_dir = target.parent
        candidates = (str(target),)

    if not candidates:
        _eprint(f"jss-lint: no lintable files under {target}")
        sys.exit(2)

    report, _cfg = _lint_paths(candidates)

    try:
        result = _init.run(
            target_dir,
            report=report,
            force=force,
            dry_run=dry_run,
            threshold=threshold,
        )
    except _init.InitRefusedError as exc:
        _eprint(f"jss-lint: {exc}")
        sys.exit(2)
    except ValueError as exc:
        _eprint(f"jss-lint: {exc}")
        sys.exit(2)

    if dry_run:
        click.echo("Proposed .jss-lint.toml (dry-run; nothing written):")
        click.echo(result.contents)
    else:
        click.echo(f"Wrote {result.config_path}")
        click.echo(
            f"({result.must_fix_count} distinct rules in {result.total_violations} violations"
            f"; {result.suppressed_count} rule"
            f"{'' if result.suppressed_count == 1 else 's'} auto-suppressed by precision DB)"
        )


@main.command(name="report")
@click.argument("path", type=click.Path(exists=True, path_type=str))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["md", "html", "pdf"], case_sensitive=False),
    default="md",
    help='Output format. PDF requires the [pdf] extra (`pip install "jss-lint[pdf]"`).',
)
@click.option(
    "--out",
    "out",
    type=click.Path(dir_okay=False, writable=True, path_type=str),
    default=None,
    help="Write report to FILE instead of stdout.",
)
@click.option(
    "--title",
    "title",
    default=None,
    help="Override the manuscript title (default: extracted from \\title{}).",
)
@click.option(
    "--author",
    "author",
    default=None,
    help="Override the manuscript author (default: extracted from \\author{} or \\Plainauthor{}).",
)
def report_cmd(
    path: str,
    fmt: str,
    out: str | None,
    title: str | None,
    author: str | None,
) -> None:
    """Render a one-page conformance report (spec 015)."""
    from . import report as _report

    target = Path(path)
    if target.is_dir():
        candidates = tuple(
            sorted(
                str(p)
                for p in target.iterdir()
                if p.is_file() and p.suffix.lower() in _SUPPORTED_SUFFIXES
            )
        )
    else:
        candidates = (str(target),)

    if not candidates:
        _eprint(f"jss-lint: no lintable files under {target}")
        sys.exit(2)

    report, document, _cfg = _lint_paths_with_doc(candidates)

    # Spec 015 follow-up: extract title / author from the parsed
    # preamble when the user didn't pass an override on the CLI.
    if title is None or author is None:
        extracted_title, extracted_author = _report.extract_metadata(document)
        if title is None:
            title = extracted_title or "Manuscript"
        if author is None:
            author = extracted_author or "(unknown)"

    fmt_norm = fmt.lower()
    try:
        rendered = _report.render_report(
            report,
            fmt=fmt_norm,
            title=title,
            author=author,
            file_count=len(candidates),
        )
    except _report.PdfNotAvailable as exc:
        _eprint(f"jss-lint: {exc}")
        sys.exit(2)

    if fmt_norm == "pdf":
        # bytes — must NOT echo to stdout as text; require --out.
        if out is None:
            _eprint("jss-lint: --format pdf requires --out FILE")
            sys.exit(2)
        Path(out).write_bytes(rendered)  # type: ignore[arg-type]
    else:
        if out is None:
            click.echo(rendered, nl=False)
        else:
            Path(out).write_text(rendered, encoding="utf-8")  # type: ignore[arg-type]


@main.command(name="diff")
@click.argument("old", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.argument("new", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option(
    "--ignore-line-drift",
    "ignore_line_drift",
    is_flag=True,
    default=False,
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["terminal", "markdown", "json"], case_sensitive=False),
    default="terminal",
    show_default=True,
    help="Output format (markdown is GitHub-flavoured CommonMark).",
)
def diff_cmd(
    old: str, new: str, ignore_line_drift: bool, fmt: str,
) -> None:
    """Diff two ``--output json`` reports (spec 016)."""
    import json

    from . import diff as _diff

    def _load(p: str) -> list[dict]:
        try:
            with open(p, encoding="utf-8") as f:
                payload = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            _eprint(f"jss-lint: failed to read {p}: {exc}")
            sys.exit(2)
        try:
            return _diff.validate_payload(payload, p)
        except _diff.SchemaMismatch as exc:
            _eprint(f"jss-lint: {exc}")
            sys.exit(2)

    old_violations = _load(old)
    new_violations = _load(new)

    diff = _diff.compare(
        old_violations, new_violations, ignore_line_drift=ignore_line_drift
    )
    fmt_norm = fmt.lower()
    if fmt_norm == "markdown":
        click.echo(_diff.render_markdown(diff), nl=False)
    elif fmt_norm == "json":
        click.echo(_diff.render_json(diff), nl=False)
    else:
        click.echo(_diff.render_terminal(diff), nl=False)
    sys.exit(1 if diff.introduced else 0)


@main.command(name="lsp")
@click.option(
    "--stdio",
    "stdio",
    is_flag=True,
    default=True,
    help=(
        "Communicate over stdio (default). Accepted for compatibility with "
        "LSP clients that append this flag — notably vscode-languageclient, "
        "which passes it whenever the server is configured with "
        "TransportKind.stdio. The server only speaks stdio, so this is a "
        "no-op."
    ),
)
def lsp_cmd(stdio: bool) -> None:  # noqa: ARG001 — stdio is accepted, not consumed
    """Start the spec-011 LSP server on stdio.

    Requires the ``[lsp]`` extra (``pip install "jss-lint[lsp]"``).
    Editors / clients spawn this command as a subprocess; the
    server speaks LSP 3.17 and shuts down when the client closes
    the connection.
    """
    try:
        from .lsp.server import main as _lsp_main
    except ImportError as exc:
        _eprint(
            "jss-lint: LSP support not installed; "
            'install with `pip install "jss-lint[lsp]"`'
        )
        _eprint(f"  ({exc})")
        sys.exit(2)
    _lsp_main()


if __name__ == "__main__":  # pragma: no cover
    main()
