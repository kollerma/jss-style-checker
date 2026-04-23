"""`eval-jss` — precision harness for the `jss-lint` linter.

See `specs/002-eval-jss-harness/` for the authoring plan and contracts.

This package is deliberately kept out of the published wheel
(`pyproject.toml`'s `tool.hatch.build.targets.wheel.packages` stays
`["src/texlint"]`). It ships in the sdist so developers who
`pip install -e '.[dev]'` get the harness; end users installing from
PyPI receive only the linter.
"""
