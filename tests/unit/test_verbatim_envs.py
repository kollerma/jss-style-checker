"""Contract tests for the shared verbatim-environment sets.

The parser's special-char neutraliser and the rules' non-prose check
must agree on which environments hold literal (non-prose) content.
They used to hold two hand-maintained lists that drifted apart:
``lstlisting`` was neutralised by the parser but not recognised by
``_is_inside_verbatim``, so markup rules fired — and offered "safe"
auto-fixes — inside code listings.
"""

from __future__ import annotations

from pathlib import Path

from texlint.api import CODE_DISPLAY_ENVS, LISTING_ENVS, VERBATIM_ENVS
from texlint.core.parser import parse_tex_source
from texlint.journals.jss.rules import _helpers


def test_verbatim_envs_is_union_of_subsets():
    assert VERBATIM_ENVS == CODE_DISPLAY_ENVS | LISTING_ENVS
    assert CODE_DISPLAY_ENVS & LISTING_ENVS == frozenset()


def test_rule_helpers_consume_shared_set():
    assert _helpers._VERBATIM_ENVS == VERBATIM_ENVS


def test_parser_neutralises_every_shared_env():
    """A ``$`` inside each env body must be neutralised so strict
    parsing survives — for every env in the shared set, not just a
    parser-private subset."""
    for env in sorted(VERBATIM_ENVS):
        src = (
            f"prose before\n\\begin{{{env}}}\nx <- a $ b % c\n"
            f"\\end{{{env}}}\nprose after\n"
        )
        parsed = parse_tex_source(src, Path("doc.tex"))
        assert parsed.violations == (), f"parse error for env {env!r}"
        assert "$" not in parsed.source, f"unneutralised $ in {env!r}"
        assert "% c" not in parsed.source, f"unneutralised % in {env!r}"


def test_verbatim_star_not_shadowed_by_verbatim():
    """Longest-first alternation: ``\\begin{verbatim*}`` must match the
    starred name, not stop at the ``verbatim`` prefix."""
    src = "\\begin{verbatim*}\na $ b\n\\end{verbatim*}\n"
    parsed = parse_tex_source(src, Path("doc.tex"))
    assert parsed.violations == ()
    assert "$" not in parsed.source
