"""The ``--version`` block (spec 027 contracts/version-output.md).

Four lines, byte-identical across engines except the engine line. The
formatter lives in core so the bindings reuse it rather than each
re-inventing the layout.
"""

from __future__ import annotations

from texlint.api import RuleSetInfo
from texlint.version import format_rule_set, format_version_block


def test_block_is_four_lines_and_newline_terminated() -> None:
    block = format_version_block(
        tool="1.2.0",
        engine="texlint/python",
        rule_set="2026-09-06 (jss.cls 3.3, vendored 2021-05-23)",
        journal="jss",
    )
    assert block == (
        "jss-lint 1.2.0\n"
        "engine: texlint/python 1.2.0\n"
        "rule set: 2026-09-06 (jss.cls 3.3, vendored 2021-05-23)\n"
        "journal: jss\n"
    )


def test_rule_set_line_from_metadata() -> None:
    info = RuleSetInfo(
        version="2026-09-06",
        fingerprint="sha256:" + "0" * 64,
        guide_edition="jss.cls 3.3",
        source_vendored_at="2021-05-23",
    )
    assert format_rule_set(info) == "2026-09-06 (jss.cls 3.3, vendored 2021-05-23)"
    assert info.guide_source == "jss.cls 3.3 (2021-05-23)"


def test_journal_without_rule_set_data_renders_n_a() -> None:
    assert format_rule_set(RuleSetInfo()) == "n/a"
    assert RuleSetInfo().guide_source is None
