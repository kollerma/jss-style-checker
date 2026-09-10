"""The ``--version`` block, shared by the CLI and the bindings.

Contract: ``specs/027-first-time-user-gaps/contracts/version-output.md``.
Four lines on stdout, exit 0::

    jss-lint 1.2.0
    engine: texlint/python 1.2.0
    rule set: 2026-09-06 (jss.cls 3.3, vendored 2021-05-23)
    journal: jss

The Rust engine prints ``engine: jsslint-core/rust <v>`` on line 2; that
one line is the documented §XIII divergence. Lines 1, 3, and 4 are
byte-identical across engines, which is what ``version_parity.rs``
compares — so the formatter lives here rather than in either CLI.
"""

from __future__ import annotations

from texlint.api import RuleSetInfo

_NO_RULE_SET = "n/a"


def format_rule_set(info: RuleSetInfo) -> str:
    """Line 3's payload. ``n/a`` for a journal without provenance."""
    if info.version is None:
        return _NO_RULE_SET
    if info.guide_edition is None:
        return info.version
    if info.source_vendored_at is None:
        return f"{info.version} ({info.guide_edition})"
    return f"{info.version} ({info.guide_edition}, vendored {info.source_vendored_at})"


def format_version_block(
    *, tool: str, engine: str, rule_set: str, journal: str
) -> str:
    """The four-line block, newline-terminated.

    *tool* is the single-sourced suite version (§XV), *engine* the engine
    label without its version, *rule_set* the output of
    :func:`format_rule_set`, and *journal* the effective journal id —
    suffixed ``(not registered)`` by the caller when it does not resolve.
    """
    return (
        f"jss-lint {tool}\n"
        f"engine: {engine} {tool}\n"
        f"rule set: {rule_set}\n"
        f"journal: {journal}\n"
    )
