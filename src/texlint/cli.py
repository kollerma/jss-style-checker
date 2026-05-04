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


def _parse_inputs(paths: tuple[str, ...]) -> tuple[ParsedDocument | None, int]:
    """Parse each input file. Return (document, exit_code_if_any).

    The exit-code is 2 when any path is missing or has an unsupported
    suffix. Delegates to :func:`texlint.core.engine.parse_document` for
    actual parsing; extension dispatch supports ``.tex``, ``.ltx``,
    ``.bib``, ``.Rnw``, and ``.Rmd``.
    """
    path_objs: list[Path] = []
    for raw in paths:
        path = Path(raw)
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


def _determine_exit_code(report: Any) -> int:
    """Exit 2 if any parse error present; else 1 if any violation; else 0.

    Parse failures dominate style violations because the report is incomplete
    when the parser could not process a file — see contracts/cli.md §Exit codes.
    """
    if any(v.rule_id == _PARSE_RULE_ID for v in report.violations):
        return 2
    if report.violations:
        return 1
    return 0


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    name="jss-lint",
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
    "-v",
    "--verbose",
    "verbose",
    is_flag=True,
    default=None,
    help="Enable diagnostic output on stderr.",
)
@click.argument("paths", nargs=-1, type=click.Path(path_type=str))
def main(
    journal: str | None,
    mode: str | None,
    output: str | None,
    source_root: str | None,
    ignore_rules: str | None,
    verbose: bool | None,
    paths: tuple[str, ...],
) -> None:
    """Lint LaTeX/BibTeX manuscripts against journal style guides."""
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
    if verbose is not None:
        cli_overrides["verbose"] = verbose

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
    _dispatch_renderer(cfg.output, report, cfg)
    sys.exit(_determine_exit_code(report))


if __name__ == "__main__":  # pragma: no cover
    main()
