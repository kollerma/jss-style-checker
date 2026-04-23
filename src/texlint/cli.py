"""Command-line interface for texlint, exposed as ``jss-lint``."""

from __future__ import annotations

import click

from . import __version__


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="jss-lint")
@click.argument("paths", nargs=-1, type=click.Path(exists=False))
def main(paths: tuple[str, ...]) -> None:
    """Lint LaTeX/BibTeX manuscripts against journal style guides.

    PATHS are files or directories to check. When omitted, no work is done.
    """
    if not paths:
        click.echo("jss-lint: no paths given (stub — rules not yet implemented).")
        return

    for path in paths:
        click.echo(f"jss-lint: would check {path} (stub — rules not yet implemented).")


if __name__ == "__main__":  # pragma: no cover
    main()
