"""The colour decision (spec 027 item F, `contracts/color.md` C-3).

One pure function of `(flag, toml, env, isatty)`, implemented identically
in both CLIs and tested here as a matrix. The precedence follows the
convention anstream, ripgrep, and cargo share, so a user's `NO_COLOR`
habit works here too:

    --color always|never  >  NO_COLOR  >  CLICOLOR_FORCE  >  TOML  >  TTY
"""

from __future__ import annotations

import re

import pytest

from texlint.api import ToolConfig
from texlint.color import should_colorize

_SGR_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_sgr(text: str) -> str:
    return _SGR_RE.sub("", text)


def decide(flag=None, toml="auto", env=None, isatty=True) -> bool:
    return should_colorize(flag=flag, toml_value=toml, env=env or {}, isatty=isatty)


class TestFlagWins:
    def test_always_beats_a_pipe(self) -> None:
        assert decide(flag="always", isatty=False) is True

    def test_never_beats_a_tty(self) -> None:
        assert decide(flag="never", isatty=True) is False

    def test_always_beats_no_color(self) -> None:
        # The explicit flag is the user asking for it right now.
        assert decide(flag="always", env={"NO_COLOR": "1"}) is True

    def test_never_beats_clicolor_force(self) -> None:
        assert decide(flag="never", env={"CLICOLOR_FORCE": "1"}) is False


class TestEnvironment:
    def test_no_color_disables(self) -> None:
        assert decide(env={"NO_COLOR": "1"}) is False

    def test_empty_no_color_is_ignored(self) -> None:
        # The convention is "set and non-empty"; an empty value is how
        # scripts unset it without unsetting it.
        assert decide(env={"NO_COLOR": ""}) is True

    def test_no_color_beats_clicolor_force(self) -> None:
        assert decide(env={"NO_COLOR": "1", "CLICOLOR_FORCE": "1"}) is False

    def test_clicolor_force_enables_off_a_tty(self) -> None:
        assert decide(env={"CLICOLOR_FORCE": "1"}, isatty=False) is True

    def test_clicolor_force_zero_is_ignored(self) -> None:
        assert decide(env={"CLICOLOR_FORCE": "0"}, isatty=False) is False

    def test_empty_clicolor_force_is_ignored(self) -> None:
        assert decide(env={"CLICOLOR_FORCE": ""}, isatty=False) is False


class TestTomlAndAuto:
    def test_toml_always_enables_off_a_tty(self) -> None:
        assert decide(toml="always", isatty=False) is True

    def test_toml_never_disables_on_a_tty(self) -> None:
        assert decide(toml="never", isatty=True) is False

    def test_toml_loses_to_the_environment(self) -> None:
        assert decide(toml="always", env={"NO_COLOR": "1"}) is False

    def test_auto_follows_the_tty(self) -> None:
        assert decide(isatty=True) is True
        assert decide(isatty=False) is False

    def test_dumb_terminal_is_not_coloured(self) -> None:
        assert decide(env={"TERM": "dumb"}, isatty=True) is False

    def test_dumb_terminal_still_yields_to_an_explicit_flag(self) -> None:
        assert decide(flag="always", env={"TERM": "dumb"}, isatty=True) is True

    def test_an_unknown_toml_value_falls_through_to_auto(self) -> None:
        # `color = "sometimes"` is a typo, not a request for colour.
        assert decide(toml="sometimes", isatty=False) is False


class TestStripInvariant:
    """`color.md` C-1: colour must never change layout.

    Stripping every SGR sequence from coloured output has to give the
    plain stream back byte for byte — that is what lets the parity
    suites, the snapshot tests, and the eval harness keep comparing the
    plain stream while colour ships.
    """

    def _render(self, report, cfg, color: bool) -> str:
        import io
        from contextlib import redirect_stdout

        from texlint.output.terminal import render

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            render(report, cfg, color)
        return buffer.getvalue()

    def _report(self, path: str):
        from pathlib import Path

        from texlint.core.engine import load_journal, parse_document, run

        return run(
            ToolConfig(), parse_document([Path(path)]), load_journal("jss")
        )

    @pytest.mark.parametrize(
        "fixture",
        [
            "tests/fixtures/compliant/minimal.tex",
            "tests/fixtures/violations/citations/JSS-CITE-002-bad.tex",
        ],
    )
    @pytest.mark.parametrize("mode", ["author", "reviewer"])
    def test_stripping_yields_the_plain_stream(self, fixture: str, mode: str) -> None:
        from dataclasses import replace

        report = self._report(fixture)
        cfg = replace(ToolConfig(), mode=mode)
        plain = self._render(report, cfg, False)
        coloured = self._render(report, cfg, True)
        assert _strip_sgr(coloured) == plain

    def test_a_report_with_findings_is_actually_coloured(self) -> None:
        # Guards the invariant above against passing vacuously. A clean
        # author run legitimately has nothing to colour: its only output
        # is the footer, and `color.md` C-2 leaves footer sentences,
        # the baseline line, and the coverage body uncoloured.
        report = self._report(
            "tests/fixtures/violations/citations/JSS-CITE-002-bad.tex"
        )
        assert "\x1b[" in self._render(report, ToolConfig(), True)

    def test_skipped_rules_block_too(self) -> None:
        from dataclasses import replace

        report = self._report("tests/fixtures/compliant/minimal.tex")
        cfg = replace(ToolConfig(), verbose=True)
        plain = self._render(report, cfg, False)
        assert _strip_sgr(self._render(report, cfg, True)) == plain

    def test_only_the_sixteen_colour_palette_is_used(self) -> None:
        # No 256-colour (`38;5;N`) or truecolor (`38;2;R;G;B`) sequences:
        # they are unreadable on some backgrounds and unsupported on
        # others (`color.md` C-2).
        report = self._report("tests/fixtures/violations/citations/JSS-CITE-002-bad.tex")
        coloured = self._render(report, ToolConfig(), True)
        for code in re.findall(r"\x1b\[([0-9;]*)m", coloured):
            for part in code.split(";"):
                assert part == "" or int(part) < 38 or 90 <= int(part) <= 97, (
                    f"SGR parameter {part!r} is outside the 16-colour set"
                )
