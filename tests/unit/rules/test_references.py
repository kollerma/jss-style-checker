"""Tests for JSS references rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, Severity, ToolConfig
from texlint.journals.jss.rules.references import (
    check_jss_refs_001,
    jss_refs_001,
    jss_refs_002,
    jss_refs_003,
    jss_refs_004,
    jss_refs_005,
    jss_refs_006,
    jss_refs_007,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "references"


def _bib_from_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_seven_rules():
    assert len(rules) == 7


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {
        f"JSS-REFS-00{i}" for i in range(1, 8)
    }


def test_all_rule_formats_are_none():
    for r in rules:
        assert r.formats is None


# ---------------------------------------------------------------------------
# JSS-REFS-001 — year required
# ---------------------------------------------------------------------------


class TestRefs001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_refs_001, _bib_from_fixture("JSS-REFS-001-bad.bib"), kind="bib")
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-REFS-001"
        assert v.severity == Severity.WARNING
        assert v.fix is None

    def test_good_fixture_no_violation(self, run_rule):
        assert run_rule(jss_refs_001, _bib_from_fixture("JSS-REFS-001-good.bib"), kind="bib") == []

    def test_multiple_entries_multiple_violations(self, run_rule):
        src = (
            "@article{a, author={x}}\n"
            "@book{b, author={y}, title={T}, publisher={P}}\n"
        )
        violations = run_rule(jss_refs_001, src, kind="bib")
        assert len(violations) == 2

    def test_empty_library_is_silent(self, run_rule):
        assert run_rule(jss_refs_001, "", kind="bib") == []

    def test_no_bib_files_is_silent(self, tmp_path: Path):
        doc = ParsedDocument()
        assert list(check_jss_refs_001(doc, ToolConfig())) == []

    def test_missing_key_is_unknown(self, run_rule):
        # Empty key: suggestion uses <unknown>.
        src = "@article{, author={x}}\n"
        violations = run_rule(jss_refs_001, src, kind="bib")
        assert len(violations) == 1
        assert "<unknown>" in violations[0].suggestion


# ---------------------------------------------------------------------------
# JSS-REFS-002 — tight title-case (all-lowercase)
# ---------------------------------------------------------------------------


class TestRefs002:
    def test_positive(self, run_rule):
        violations = run_rule(jss_refs_002, _bib_from_fixture("JSS-REFS-002-bad.bib"), kind="bib")
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-REFS-002"

    def test_good_fixture_no_violation(self, run_rule):
        assert run_rule(jss_refs_002, _bib_from_fixture("JSS-REFS-002-good.bib"), kind="bib") == []

    def test_title_missing_is_silent(self, run_rule):
        src = "@article{a, author={x}, year={2020}}\n"
        assert run_rule(jss_refs_002, src, kind="bib") == []

    def test_title_with_non_letter_words_only(self, run_rule):
        # "1984" — no letter words → silent (len(words)==0 branch).
        src = "@article{a, title={1984}, year={1984}}\n"
        assert run_rule(jss_refs_002, src, kind="bib") == []

    def test_mixed_case_is_ok(self, run_rule):
        src = "@article{a, title={Some Title}, year={2020}}\n"
        assert run_rule(jss_refs_002, src, kind="bib") == []

    def test_macro_wrapped_is_ok(self, run_rule):
        # After \pkg-stripping: 'mass: a guide' → still all-lowercase → fires.
        src = "@article{a, title={\\pkg{MASS}: a guide}, year={2020}}\n"
        violations = run_rule(jss_refs_002, src, kind="bib")
        # Stripped LaTeX leaves 'MASS: a guide' — MASS upper → not all lowercase → silent.
        # Actually we strip the \pkg macro name but keep the braced content.
        # Expected: 'MASS: a guide' → 'MASS' has upper → silent.
        assert violations == []


# ---------------------------------------------------------------------------
# JSS-REFS-003 — DOI advisory (info)
# ---------------------------------------------------------------------------


class TestRefs003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_refs_003, _bib_from_fixture("JSS-REFS-003-bad.bib"), kind="bib")
        assert len(violations) == 1
        assert violations[0].severity == Severity.INFO

    def test_good_fixture_no_violation(self, run_rule):
        assert run_rule(jss_refs_003, _bib_from_fixture("JSS-REFS-003-good.bib"), kind="bib") == []

    def test_unknown_entry_type_silent(self, run_rule):
        src = "@misc{a, author={x}, year={2020}}\n"
        assert run_rule(jss_refs_003, src, kind="bib") == []

    def test_entry_without_key_uses_unknown(self, run_rule):
        src = "@article{, author={x}, title={T}, journal={J}, year={2020}}\n"
        violations = run_rule(jss_refs_003, src, kind="bib")
        assert len(violations) == 1
        assert "<unknown>" in violations[0].suggestion

    def test_pre_doi_era_silent(self, run_rule):
        # CrossRef and DOI registration began ~2000; pre-2000 entries
        # mostly never received a retroactive DOI. The advisory should
        # not fire on them.
        src = "@article{a, author={x}, title={T}, journal={J}, year={1986}}\n"
        assert run_rule(jss_refs_003, src, kind="bib") == []

    def test_pre_doi_era_book_silent(self, run_rule):
        src = "@book{a, author={x}, title={T}, publisher={Cambridge}, year={1998}}\n"
        assert run_rule(jss_refs_003, src, kind="bib") == []

    def test_pre_doi_era_with_year_in_other_field_format(self, run_rule):
        # 'Sept 1995' style year strings — the 4-digit year is still
        # extracted by the year regex.
        src = "@article{a, author={x}, title={T}, journal={J}, year={Sept 1995}}\n"
        assert run_rule(jss_refs_003, src, kind="bib") == []


# ---------------------------------------------------------------------------
# JSS-REFS-004 — markup for package / language names
# ---------------------------------------------------------------------------


class TestRefs004:
    def test_positive_language_in_title(self, run_rule):
        # MASS fixture mentions 'S' (a programming language per LANGUAGES) unwrapped.
        violations = run_rule(jss_refs_004, _bib_from_fixture("JSS-REFS-004-bad.bib"), kind="bib")
        assert len(violations) >= 1
        assert violations[0].rule_id == "JSS-REFS-004"

    def test_good_fixture_wrapped(self, run_rule):
        assert run_rule(jss_refs_004, _bib_from_fixture("JSS-REFS-004-good.bib"), kind="bib") == []

    def test_title_missing_silent(self, run_rule):
        src = "@article{a, author={x}, year={2020}}\n"
        assert run_rule(jss_refs_004, src, kind="bib") == []

    def test_pkg_mention_only(self, run_rule):
        # Bare 'MASS' (an R_PACKAGE) without \pkg{} wrapping.
        src = "@article{a, title={MASS is useful}, year={2020}}\n"
        violations = run_rule(jss_refs_004, src, kind="bib")
        assert len(violations) == 1
        assert "\\pkg" in violations[0].suggestion

    def test_clean_title_silent(self, run_rule):
        src = "@article{a, title={A General Approach}, year={2020}}\n"
        assert run_rule(jss_refs_004, src, kind="bib") == []

    def test_language_mention_fires_proglang(self, run_rule):
        # 'Python' is in LANGUAGES; title mentions it unwrapped.
        src = "@article{a, title={Statistical Methods in Python}, year={2020}}\n"
        violations = run_rule(jss_refs_004, src, kind="bib")
        assert len(violations) == 1
        assert "\\proglang" in violations[0].suggestion


def test_iter_entries_skips_library_none(tmp_path: Path):
    # Covers the `if bib.library is None: continue` branch in _iter_entries.
    from texlint.api import ParsedBibFile
    from texlint.journals.jss.rules.references import _iter_entries
    broken = ParsedBibFile(
        path=tmp_path / "broken.bib", source="", library=None, violations=()
    )
    doc = ParsedDocument(bib_files=(broken,))
    assert list(_iter_entries(doc)) == []


# ---------------------------------------------------------------------------
# JSS-REFS-005 — journal not abbreviated
# ---------------------------------------------------------------------------


class TestRefs005:
    def test_positive(self, run_rule):
        violations = run_rule(jss_refs_005, _bib_from_fixture("JSS-REFS-005-bad.bib"), kind="bib")
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-REFS-005"

    def test_good_fixture_no_violation(self, run_rule):
        assert run_rule(jss_refs_005, _bib_from_fixture("JSS-REFS-005-good.bib"), kind="bib") == []

    def test_journal_missing_silent(self, run_rule):
        src = "@article{a, title={T}, year={2020}}\n"
        assert run_rule(jss_refs_005, src, kind="bib") == []


# ---------------------------------------------------------------------------
# JSS-REFS-006 — loose title-case
# ---------------------------------------------------------------------------


class TestRefs006:
    def test_positive(self, run_rule):
        violations = run_rule(jss_refs_006, _bib_from_fixture("JSS-REFS-006-bad.bib"), kind="bib")
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-REFS-006"

    def test_good_fixture_no_violation(self, run_rule):
        assert run_rule(jss_refs_006, _bib_from_fixture("JSS-REFS-006-good.bib"), kind="bib") == []

    def test_title_missing_silent(self, run_rule):
        src = "@article{a, year={2020}}\n"
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_all_lowercase_is_refs002s_job(self, run_rule):
        # REFS-006 skips the entirely-lowercase case (REFS-002 owns it).
        src = "@article{a, title={literate programming}, year={2020}}\n"
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_word_after_colon_lowercase(self, run_rule):
        src = "@article{a, title={A Survey: a deeper look}, year={2020}}\n"
        violations = run_rule(jss_refs_006, src, kind="bib")
        assert len(violations) == 1
        assert "after ':'" in violations[0].suggestion

    def test_no_colon_ok(self, run_rule):
        src = "@article{a, title={A Survey of Methods}, year={2020}}\n"
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_pkg_macro_first_word_silent(self, run_rule):
        # \pkg{X} at title start — package author dictates the casing,
        # not title-case rules. Don't fire even when the package name
        # is conventionally lowercase.
        src = (
            r'@article{a, title={\pkg{ensembleBMA}: '
            r'Probabilistic Forecasting}, year={2020}}'
        ) + "\n"
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_brace_wrapped_pkg_macro_first_word_silent(self, run_rule):
        # BibTeX case-protection {\pkg{X}: ...} — same exemption.
        src = (
            r'@article{a, title={{\pkg{gunsales}: Statistical Analysis}}, '
            r'year={2020}}'
        ) + "\n"
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_pkg_macro_after_colon_silent(self, run_rule):
        # \pkg{} as the first token after ':' — exempt from after-colon
        # capitalisation check.
        src = (
            r'@article{a, title={Unifying Optimization Algorithms: '
            r'\pkg{optimx} for \proglang{R}}, year={2020}}'
        ) + "\n"
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_title_no_letter_words(self, run_rule):
        src = "@article{a, title={1984}, year={2020}}\n"
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_lowercase_package_idiom_first_word_silent(self, run_rule):
        # ``vegan: Community Ecology Package`` / ``latticeExtra: Extra
        # Graphical Utilities Based on Lattice`` — bibtex titles for R
        # packages conventionally open with the lowercase package name
        # unwrapped. When the rest of the title is in title case, the
        # lowercase first word is exempt. Reproduces FPs from
        # cran_WeightedCluster, cran_seqHMM, cran_stm, cran_effects.
        for title in (
            "vegan: Community Ecology Package",
            "latticeExtra: Extra Graphical Utilities Based on Lattice",
            "topicmodels: An R Package for Fitting Topic Models",
        ):
            src = f'@manual{{a, title={{{title}}}, year={{2020}}}}\n'
            assert run_rule(jss_refs_006, src, kind="bib") == [], title

    def test_lowercase_package_idiom_with_sentence_case_description_flagged(
        self, run_rule,
    ):
        # The first-word lowercase exemption does NOT extend to the rest
        # of the title: ``nloptr: R interface to NLopt`` and similar
        # ``pkg: <sentence-case description>`` titles still violate JSS
        # title case because ``interface`` is a principal word. Matches
        # corpus annotations like DBR/goodrich2018rstanarm.
        src = (
            '@manual{a, title={nloptr: R interface to NLopt}, year={2020}}\n'
        )
        violations = run_rule(jss_refs_006, src, kind="bib")
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-REFS-006"

    def test_word_is_uppercase_start_empty_letters(self):
        # A word with no letters (e.g., '1984') counts as "capitalised" for the
        # first-word check — exercise the empty-letters branch directly.
        from texlint.journals.jss.rules.references import _word_is_uppercase_start
        assert _word_is_uppercase_start("1984") is True

    # --- sentence-case detection (lowercase principal words) -------------

    def test_sentence_case_title_flagged(self, run_rule):
        # "The use of multiple measurements in taxonomic problems" — first
        # word capped but principals ('use', 'multiple', 'measurements',
        # 'taxonomic', 'problems') are lowercase.
        src = (
            '@article{a, title={The use of multiple measurements in '
            'taxonomic problems}, year={1936}}\n'
        )
        violations = run_rule(jss_refs_006, src, kind="bib")
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-REFS-006"

    def test_single_lowercase_principal_flagged(self, run_rule):
        # "Econometric Analysis of Panel Data, 3rd edition" — single
        # lowercase principal ('edition') still fires.
        src = (
            '@book{a, title={Econometric Analysis of Panel Data, '
            '3rd edition}, year={2001}}\n'
        )
        violations = run_rule(jss_refs_006, src, kind="bib")
        assert len(violations) == 1

    def test_hyphenated_compound_silent(self, run_rule):
        # ``Spatio-temporal`` / ``Date-time`` — hyphenated compounds stay
        # one token under the principal-word check; the leading cap
        # marks them title-cased. Without whitespace-only tokenization
        # the lowercase second element would falsely trigger.
        src = (
            '@book{a, title={Statistics for Spatio-temporal Data}, '
            'year={2011}}\n'
        )
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_lowercase_principal_after_markup_silent(self, run_rule):
        # Words wrapped in `\pkg{...}` / `\code{...}` are stripped before
        # the principal-word check — author-dictated lowercase identifiers
        # don't false-positive.
        src = (
            '@article{a, title={Unifying Optimization Algorithms: '
            r'\pkg{optimx} for \proglang{R}}, year={2020}}'
        ) + "\n"
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_parenthesized_stopword_silent(self, run_rule):
        # ``(with Discussion)`` at end of title — the leading "(" gets
        # stripped, "with" is a stop word, "Discussion)" trailing ")"
        # gets stripped → all capitalised, no fire.
        src = (
            '@article{a, title={Long-Memory Dependence (with '
            'Discussion)}, year={1989}}\n'
        )
        assert run_rule(jss_refs_006, src, kind="bib") == []

    def test_brace_protected_pkg_idiom_silent(self, run_rule):
        # ``{robustlmm}: An ...`` — case-protection braces around the
        # package idiom should also exempt the first-word check.
        src = (
            '@article{a, title={{robustlmm}: An {R} Package for Robust '
            'Estimation}, year={2016}}\n'
        )
        assert run_rule(jss_refs_006, src, kind="bib") == []


# ---------------------------------------------------------------------------
# JSS-REFS-007 — journal in title case
# ---------------------------------------------------------------------------


class TestRefs007:
    def test_positive(self, run_rule):
        violations = run_rule(jss_refs_007, _bib_from_fixture("JSS-REFS-007-bad.bib"), kind="bib")
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-REFS-007"

    def test_good_fixture_no_violation(self, run_rule):
        assert run_rule(jss_refs_007, _bib_from_fixture("JSS-REFS-007-good.bib"), kind="bib") == []

    def test_journal_missing_silent(self, run_rule):
        src = "@article{a, title={T}, year={2020}}\n"
        assert run_rule(jss_refs_007, src, kind="bib") == []

    def test_abbreviated_is_refs005s_job(self, run_rule):
        # REFS-007 skips abbreviated names (REFS-005 handles them).
        src = "@article{a, journal={J. Stat. Softw.}, year={2020}}\n"
        assert run_rule(jss_refs_007, src, kind="bib") == []

    def test_stopword_midtitle_is_ok(self, run_rule):
        src = (
            "@article{a, journal={Journal of Statistical Software},"
            " year={2020}}\n"
        )
        assert run_rule(jss_refs_007, src, kind="bib") == []

    def test_no_letter_words_silent(self, run_rule):
        src = "@article{a, journal={1234 5678}, year={2020}}\n"
        assert run_rule(jss_refs_007, src, kind="bib") == []
