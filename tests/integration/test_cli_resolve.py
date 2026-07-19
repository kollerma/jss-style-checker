"""Spec 013 CLI wiring: auto-resolve on the bare ``jss-lint <PATHS>``
invocation, and ``--no-resolve`` genuinely disabling it.

Fixtures live under ``tests/fixtures/resolver_projects/``:
  * ``basic/`` — root.tex \\input's intro.tex (JSS-CODE-002) and
    \\bibliography{refs}'s refs.bib (JSS-REFS-003, no DOI).
  * ``cycle/`` — a.tex <-> b.tex mutual \\input (JSS-PROJECT-001).
  * ``missing/`` — root.tex \\input{ghost}, unresolvable (JSS-PROJECT-002).
  * ``latin1_root/`` — root.tex itself is Latin-1-encoded (a lone
    non-UTF-8 byte in a comment) and \\input's a normal UTF-8 intro.tex.
  * ``latin1_included/`` — root.tex is normal UTF-8 and \\input's a
    Latin-1-encoded intro.tex.
  * ``multi_bib/`` — root.tex \\cite's two entries and
    \\bibliography{refs1,refs2} (comma-separated, standard BibTeX);
    both resolve independently and both fire JSS-REFS-003 (no DOI).
  * ``rnw_root/`` — root.Rnw (not .tex) \\input's intro.tex.
  * ``rmd_root/`` — root.Rmd (not .tex) \\input's intro.tex from a raw
    LaTeX island in its prose.
  * ``texinputs/root/root.tex`` \\input's "extra", found only via
    TEXINPUTS=../extra (texinputs/extra/extra.tex).
  * ``bibinputs/root/root.tex`` \\bibliography{refs}, found only via
    BIBINPUTS=../extra (bibinputs/extra/refs.bib).
  * ``nonlintable_target/`` — root.tex \\input's a bundled .cls file
    directly (real-world precedent: pmclust's my_jss.cls); walked for
    the graph but silently excluded from linting.
  * ``subfile/`` — root.tex \\subfile's sub.tex (JSS-CODE-002).
  * ``multi_missing_multi_cycle/`` — root.tex \\input's two
    self-cycling files (a.tex, b.tex) and two missing refs (ghost1,
    ghost2): two distinct JSS-PROJECT-001s and two JSS-PROJECT-002s.
  * ``mixed_sort_order/`` — root.tex \\input{ghost} (JSS-PROJECT-002,
    line 1, column None) alongside ordinary preamble violations also
    at line 1 (column 1) on the same file, pinning the None-sorts-
    before-int column-bucket ordering between the two violation kinds.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "resolver_projects"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _violations(output: str) -> list[dict]:
    return json.loads(output)["violations"]


def test_single_root_file_auto_resolves(runner: CliRunner) -> None:
    result = runner.invoke(
        main, ["--output", "json", str(FIXTURES / "basic" / "root.tex")]
    )
    assert result.exit_code in (0, 1), result.output
    violations = _violations(result.output)
    rule_ids = {v["rule_id"] for v in violations}
    assert "JSS-CODE-002" in rule_ids
    assert "JSS-REFS-003" in rule_ids

    by_rule = {v["rule_id"]: v for v in violations}
    assert by_rule["JSS-CODE-002"]["file"] == str(FIXTURES / "basic" / "intro.tex")
    assert by_rule["JSS-REFS-003"]["file"] == str(FIXTURES / "basic" / "refs.bib")


def test_no_resolve_collapses_to_root_only(runner: CliRunner) -> None:
    result = runner.invoke(
        main,
        [
            "--no-resolve",
            "--output",
            "json",
            str(FIXTURES / "basic" / "root.tex"),
        ],
    )
    assert result.exit_code in (0, 1), result.output
    rule_ids = {v["rule_id"] for v in _violations(result.output)}
    assert "JSS-CODE-002" not in rule_ids
    assert "JSS-REFS-003" not in rule_ids


def test_directory_argument_does_not_auto_resolve(runner: CliRunner) -> None:
    """A directory expands to N independent files (spec 013: only a
    single root *file* argument triggers resolution)."""
    result = runner.invoke(
        main, ["--output", "json", str(FIXTURES / "basic")]
    )
    assert result.exit_code in (0, 1), result.output
    rule_ids = {v["rule_id"] for v in _violations(result.output)}
    # intro.tex and refs.bib are directly among the expanded files, so
    # their own violations still show up — but resolution itself never
    # ran (no JSS-PROJECT-* rule could have fired either way here).
    assert "JSS-CODE-002" in rule_ids
    assert "JSS-REFS-003" in rule_ids


def test_explicit_multi_file_does_not_resolve(runner: CliRunner) -> None:
    """Multiple explicit paths are an explicit member list (FR-003):
    the resolver never runs, so the a.tex/b.tex cycle isn't detected."""
    result = runner.invoke(
        main,
        [
            "--output",
            "json",
            str(FIXTURES / "cycle" / "a.tex"),
            str(FIXTURES / "cycle" / "b.tex"),
        ],
    )
    assert result.exit_code in (0, 1), result.output
    rule_ids = {v["rule_id"] for v in _violations(result.output)}
    assert "JSS-PROJECT-001" not in rule_ids


def test_cycle_is_detected_and_reported(runner: CliRunner) -> None:
    result = runner.invoke(
        main, ["--output", "json", str(FIXTURES / "cycle" / "a.tex")]
    )
    assert result.exit_code in (0, 1), result.output
    violations = _violations(result.output)
    cycle = [v for v in violations if v["rule_id"] == "JSS-PROJECT-001"]
    assert len(cycle) == 1
    assert cycle[0]["file"] == str(FIXTURES / "cycle" / "a.tex")
    assert "cycle detected" in cycle[0]["message"]


def test_missing_reference_is_reported(runner: CliRunner) -> None:
    result = runner.invoke(
        main, ["--output", "json", str(FIXTURES / "missing" / "root.tex")]
    )
    assert result.exit_code in (0, 1), result.output
    violations = _violations(result.output)
    missing = [v for v in violations if v["rule_id"] == "JSS-PROJECT-002"]
    assert len(missing) == 1
    assert missing[0]["file"] == str(FIXTURES / "missing" / "root.tex")
    assert missing[0]["message"] == "referenced file not found: ghost"


def test_no_resolve_suppresses_project_rules(runner: CliRunner) -> None:
    result = runner.invoke(
        main,
        [
            "--no-resolve",
            "--output",
            "json",
            str(FIXTURES / "missing" / "root.tex"),
        ],
    )
    assert result.exit_code in (0, 1), result.output
    rule_ids = {v["rule_id"] for v in _violations(result.output)}
    assert "JSS-PROJECT-002" not in rule_ids


def test_ignore_rules_suppresses_project_001(runner: CliRunner) -> None:
    """Per data-model.md / resolver.md C-13: JSS-PROJECT-* participate
    in --ignore-rules like any other rule (no sentinel exception)."""
    result = runner.invoke(
        main,
        [
            "--ignore-rules",
            "JSS-PROJECT-001",
            "--output",
            "json",
            str(FIXTURES / "cycle" / "a.tex"),
        ],
    )
    assert result.exit_code in (0, 1), result.output
    rule_ids = {v["rule_id"] for v in _violations(result.output)}
    assert "JSS-PROJECT-001" not in rule_ids


def test_latin1_root_degrades_gracefully(runner: CliRunner) -> None:
    """A non-UTF-8 root file decodes as Latin-1 with a warning-severity
    JSS-PARSE-000 instead of aborting the run; resolution still finds
    and lints the \\input'd intro.tex."""
    result = runner.invoke(
        main,
        ["--output", "json", str(FIXTURES / "latin1_root" / "root.tex")],
    )
    assert result.exit_code in (0, 1), result.output
    violations = _violations(result.output)
    rule_ids = {v["rule_id"] for v in violations}
    assert "JSS-PARSE-000" in rule_ids
    assert "JSS-CODE-002" in rule_ids  # from the resolved intro.tex

    parse_errors = [v for v in violations if v["rule_id"] == "JSS-PARSE-000"]
    assert len(parse_errors) == 1
    err = parse_errors[0]
    assert err["severity"] == "warning"
    assert err["file"] == str(FIXTURES / "latin1_root" / "root.tex")
    assert err["message"] == (
        "File is not valid UTF-8 (invalid continuation byte at byte 51); "
        "decoded as Latin-1 — check the result for mojibake and "
        "consider converting the file to UTF-8."
    )


def test_latin1_included_file_degrades_gracefully(runner: CliRunner) -> None:
    """A non-UTF-8 \\input'd file degrades the same way; the rest of the
    project (root.tex) still lints normally."""
    result = runner.invoke(
        main,
        ["--output", "json", str(FIXTURES / "latin1_included" / "root.tex")],
    )
    assert result.exit_code in (0, 1), result.output
    violations = _violations(result.output)
    parse_errors = [v for v in violations if v["rule_id"] == "JSS-PARSE-000"]
    assert len(parse_errors) == 1
    err = parse_errors[0]
    assert err["severity"] == "warning"
    assert err["file"] == str(FIXTURES / "latin1_included" / "intro.tex")
    assert "invalid continuation byte at byte 15" in err["message"]


def test_comma_separated_bibliography_resolves_each_file_independently(
    runner: CliRunner,
) -> None:
    """\\bibliography{refs1,refs2} is standard BibTeX (comma-separated
    list); each name resolves on its own — not one literal
    "refs1,refs2.bib" target, which would spuriously fire
    JSS-PROJECT-002."""
    result = runner.invoke(
        main,
        ["--output", "json", str(FIXTURES / "multi_bib" / "root.tex")],
    )
    assert result.exit_code in (0, 1), result.output
    violations = _violations(result.output)
    rule_ids = {v["rule_id"] for v in violations}
    assert "JSS-PROJECT-002" not in rule_ids

    refs003 = {
        v["file"] for v in violations if v["rule_id"] == "JSS-REFS-003"
    }
    assert refs003 == {
        str(FIXTURES / "multi_bib" / "refs1.bib"),
        str(FIXTURES / "multi_bib" / "refs2.bib"),
    }


def test_rnw_root_auto_resolves(runner: CliRunner) -> None:
    """A ``.Rnw`` (not ``.tex``) root file auto-resolves too."""
    result = runner.invoke(
        main, ["--output", "json", str(FIXTURES / "rnw_root" / "root.Rnw")]
    )
    assert result.exit_code in (0, 1), result.output
    by_rule = {v["rule_id"]: v for v in _violations(result.output)}
    assert by_rule["JSS-CODE-002"]["file"] == str(FIXTURES / "rnw_root" / "intro.tex")


def test_rmd_root_auto_resolves(runner: CliRunner) -> None:
    """A ``.Rmd`` (not ``.tex``) root file auto-resolves too — a
    ``\\input`` embedded in a raw-LaTeX prose island is still found."""
    result = runner.invoke(
        main, ["--output", "json", str(FIXTURES / "rmd_root" / "root.Rmd")]
    )
    assert result.exit_code in (0, 1), result.output
    by_rule = {v["rule_id"]: v for v in _violations(result.output)}
    assert by_rule["JSS-CODE-002"]["file"] == str(FIXTURES / "rmd_root" / "intro.tex")


def test_texinputs_search_path(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``\\input{extra}`` resolves via a TEXINPUTS directory that isn't
    the root's own directory."""
    monkeypatch.setenv("TEXINPUTS", str(FIXTURES / "texinputs" / "extra"))
    result = runner.invoke(
        main,
        ["--output", "json", str(FIXTURES / "texinputs" / "root" / "root.tex")],
    )
    assert result.exit_code in (0, 1), result.output
    by_rule = {v["rule_id"]: v for v in _violations(result.output)}
    assert by_rule["JSS-CODE-002"]["file"] == str(
        FIXTURES / "texinputs" / "extra" / "extra.tex"
    )


def test_bibinputs_search_path(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``\\bibliography{refs}`` resolves via a BIBINPUTS directory that
    isn't the root's own directory."""
    monkeypatch.setenv("BIBINPUTS", str(FIXTURES / "bibinputs" / "extra"))
    result = runner.invoke(
        main,
        ["--output", "json", str(FIXTURES / "bibinputs" / "root" / "root.tex")],
    )
    assert result.exit_code in (0, 1), result.output
    by_rule = {v["rule_id"]: v for v in _violations(result.output)}
    assert by_rule["JSS-REFS-003"]["file"] == str(
        FIXTURES / "bibinputs" / "extra" / "refs.bib"
    )


def test_nonlintable_target_walked_but_not_linted(runner: CliRunner) -> None:
    """A resolved \\input target with a non-lintable suffix (a bundled
    .cls file, e.g. pmclust's my_jss.cls) is silently excluded from
    linting — no crash, no spurious violation."""
    result = runner.invoke(
        main,
        [
            "--output",
            "json",
            str(FIXTURES / "nonlintable_target" / "root.tex"),
        ],
    )
    assert result.exit_code in (0, 1), result.output
    violations = _violations(result.output)
    files = {v["file"] for v in violations}
    assert not any(f.endswith(".cls") for f in files)


def test_subfile_resolves(runner: CliRunner) -> None:
    """``\\subfile{...}`` resolves like \\input."""
    result = runner.invoke(
        main, ["--output", "json", str(FIXTURES / "subfile" / "root.tex")]
    )
    assert result.exit_code in (0, 1), result.output
    by_rule = {v["rule_id"]: v for v in _violations(result.output)}
    assert by_rule["JSS-CODE-002"]["file"] == str(FIXTURES / "subfile" / "sub.tex")


def test_multiple_missing_and_multiple_cycles(runner: CliRunner) -> None:
    """Two distinct self-cycles and two distinct missing references
    each produce their own violation — the dedup/ordering logic isn't
    exercised by a single-violation project."""
    result = runner.invoke(
        main,
        [
            "--output",
            "json",
            str(FIXTURES / "multi_missing_multi_cycle" / "root.tex"),
        ],
    )
    assert result.exit_code in (0, 1), result.output
    violations = _violations(result.output)

    cycles = [v for v in violations if v["rule_id"] == "JSS-PROJECT-001"]
    assert len(cycles) == 2
    assert {v["file"] for v in cycles} == {
        str(FIXTURES / "multi_missing_multi_cycle" / "a.tex"),
        str(FIXTURES / "multi_missing_multi_cycle" / "b.tex"),
    }

    missing = [v for v in violations if v["rule_id"] == "JSS-PROJECT-002"]
    assert len(missing) == 2
    assert {v["message"] for v in missing} == {
        "referenced file not found: ghost1",
        "referenced file not found: ghost2",
    }


def test_project_violation_sorts_before_same_line_rule_violation(
    runner: CliRunner,
) -> None:
    """A JSS-PROJECT-* violation (column=None) and an ordinary rule
    violation (column=1) on the same file/line sort with the
    None-column entry first — pins Violation.sort_key's column-bucket
    ordering across the two violation kinds."""
    result = runner.invoke(
        main,
        [
            "--output",
            "json",
            str(FIXTURES / "mixed_sort_order" / "root.tex"),
        ],
    )
    assert result.exit_code in (0, 1), result.output
    violations = _violations(result.output)
    same_line = [
        v
        for v in violations
        if v["file"] == str(FIXTURES / "mixed_sort_order" / "root.tex")
        and v["line"] == 1
    ]
    assert len(same_line) >= 2
    assert same_line[0]["rule_id"] == "JSS-PROJECT-002"
    assert same_line[0]["column"] is None
    assert all(v["column"] == 1 for v in same_line[1:])
