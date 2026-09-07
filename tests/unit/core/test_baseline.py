"""Unit tests for the baseline file and matcher (spec 027 item B).

Contract: `specs/027-first-time-user-gaps/contracts/baseline-file.md`.

The module is pure — no filesystem, no journal, no config — so the same
matcher can back the CLI today and an in-memory binding later. Everything
about *where* the file lives belongs to the CLI layer (§XIV).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from texlint.api import Severity, Violation
from texlint.core.baseline import (
    BaselineEntry,
    BaselineError,
    BaselineMatcher,
    build,
    dumps,
    parse,
)


def _v(
    file: str = "paper.tex",
    line: int = 1,
    rule_id: str = "JSS-MARKUP-001",
    message: str = "msg",
    suggestion: str | None = "sug",
) -> Violation:
    return Violation(
        file=Path(file),
        line=line,
        column=1,
        rule_id=rule_id,
        severity=Severity.WARNING,
        message=message,
        suggestion=suggestion,
    )


def _doc(*violations: Violation, path_map: dict[str, str] | None = None):
    return build(
        violations,
        path_map=path_map or {"paper.tex": "paper.tex"},
        tool_version="1.2.0",
        ruleset_version="2026-09-07",
        journal="jss",
    )


class TestBuildAndDumps:
    def test_counts_identical_findings(self) -> None:
        doc = _doc(_v(line=3), _v(line=9))
        assert doc.entries == (
            BaselineEntry(
                rule_id="JSS-MARKUP-001",
                path="paper.tex",
                message="msg",
                suggestion="sug",
                count=2,
            ),
        )

    def test_entries_are_sorted_and_serialisation_is_stable(self) -> None:
        doc = _doc(
            _v(rule_id="JSS-XREF-002"),
            _v(rule_id="JSS-CAP-002"),
            _v(rule_id="JSS-CAP-002", message="other"),
        )
        payload = json.loads(dumps(doc))
        assert [(e["rule_id"], e["message"]) for e in payload["entries"]] == [
            ("JSS-CAP-002", "msg"),
            ("JSS-CAP-002", "other"),
            ("JSS-XREF-002", "msg"),
        ]
        assert dumps(doc) == dumps(parse(dumps(doc)))

    def test_file_carries_no_timestamp(self) -> None:
        # A timestamp would make --update-baseline non-byte-identical
        # across engines and across runs (research.md §6).
        payload = json.loads(dumps(_doc(_v())))
        assert set(payload) == {
            "entries",
            "journal",
            "ruleset_version",
            "schema_version",
            "tool_version",
        }

    def test_missing_suggestion_is_stored_as_empty_string(self) -> None:
        (entry,) = _doc(_v(suggestion=None)).entries
        assert entry.suggestion == ""

    def test_parse_errors_are_never_written(self) -> None:
        assert _doc(_v(rule_id="JSS-PARSE-000")).entries == ()

    def test_violations_outside_the_path_map_are_dropped(self) -> None:
        # A file the CLI could not relativise is unsuppressible, so
        # writing an entry for it would create a permanently stale row.
        assert _doc(_v(file="elsewhere.tex")).entries == ()

    def test_trailing_newline(self) -> None:
        assert dumps(_doc(_v())).endswith("}\n")


class TestParse:
    def test_round_trip(self) -> None:
        doc = _doc(_v(), _v(rule_id="JSS-CAP-002"))
        assert parse(dumps(doc)) == doc

    def test_rejects_unknown_schema_version(self) -> None:
        text = dumps(_doc(_v())).replace('"schema_version": 1', '"schema_version": 2')
        with pytest.raises(BaselineError, match="schema_version"):
            parse(text)

    def test_rejects_malformed_json(self) -> None:
        with pytest.raises(BaselineError):
            parse("{not json")

    def test_rejects_a_non_object_document(self) -> None:
        with pytest.raises(BaselineError):
            parse("[]")

    def test_rejects_a_malformed_entry(self) -> None:
        with pytest.raises(BaselineError, match="entries"):
            parse(
                json.dumps(
                    {
                        "schema_version": 1,
                        "tool_version": "1.2.0",
                        "ruleset_version": None,
                        "journal": "jss",
                        "entries": [{"rule_id": "JSS-CAP-002"}],
                    }
                )
            )

    def test_rejects_a_non_positive_count(self) -> None:
        with pytest.raises(BaselineError, match="count"):
            parse(
                json.dumps(
                    {
                        "schema_version": 1,
                        "tool_version": "1.2.0",
                        "ruleset_version": None,
                        "journal": "jss",
                        "entries": [
                            {
                                "rule_id": "JSS-CAP-002",
                                "path": "paper.tex",
                                "message": "m",
                                "suggestion": "s",
                                "count": 0,
                            }
                        ],
                    }
                )
            )

    def test_accepts_a_null_ruleset_version(self) -> None:
        text = dumps(_doc(_v())).replace(
            '"ruleset_version": "2026-09-07"', '"ruleset_version": null'
        )
        assert parse(text).ruleset_version is None


class TestMatcher:
    def _matcher(self, doc, path_map=None):
        return BaselineMatcher(doc, path_map or {"paper.tex": "paper.tex"})

    def test_matches_and_consumes(self) -> None:
        matcher = self._matcher(_doc(_v()))
        assert matcher(_v(line=3)) is True
        assert matcher(_v(line=9)) is False, "the count of 1 was already spent"

    def test_consumption_follows_the_offered_order(self) -> None:
        # Three occurrences, count 2: the two the engine offers first
        # (lowest lines, per Violation.sort_key) are the ones hidden.
        matcher = self._matcher(_doc(_v(line=1), _v(line=2)))
        assert [matcher(_v(line=n)) for n in (1, 2, 3)] == [True, True, False]

    def test_a_different_suggestion_is_a_different_finding(self) -> None:
        matcher = self._matcher(_doc(_v(suggestion="sug")))
        assert matcher(_v(suggestion="other")) is False

    def test_a_file_outside_the_path_map_is_never_matched(self) -> None:
        matcher = self._matcher(_doc(_v()))
        assert matcher(_v(file="elsewhere.tex")) is False

    def test_path_map_relativises_the_lookup(self) -> None:
        doc = build(
            [_v(file="/abs/dir/paper.tex")],
            path_map={"/abs/dir/paper.tex": "paper.tex"},
            tool_version="1.2.0",
            ruleset_version=None,
            journal="jss",
        )
        assert doc.entries[0].path == "paper.tex"
        matcher = BaselineMatcher(doc, {"/abs/dir/paper.tex": "paper.tex"})
        assert matcher(_v(file="/abs/dir/paper.tex")) is True


class TestSummary:
    def test_matched_stale_and_unevaluated(self) -> None:
        doc = _doc(
            _v(rule_id="JSS-CAP-002"),
            _v(rule_id="JSS-XREF-002"),
            _v(rule_id="JSS-REFS-003"),
        )
        matcher = BaselineMatcher(doc, {"paper.tex": "paper.tex"})
        matcher(_v(rule_id="JSS-CAP-002"))
        summary = matcher.summary(
            ".jss-lint-baseline.json",
            applied_rule_ids={"JSS-CAP-002", "JSS-XREF-002"},
        )
        assert (summary.matched, summary.stale, summary.unevaluated) == (1, 1, 1)
        assert summary.path == ".jss-lint-baseline.json"
        assert summary.ruleset_version == "2026-09-07"

    def test_unevaluated_counts_every_remaining_occurrence(self) -> None:
        doc = _doc(_v(rule_id="JSS-REFS-003"), _v(rule_id="JSS-REFS-003"))
        matcher = BaselineMatcher(doc, {"paper.tex": "paper.tex"})
        summary = matcher.summary("b.json", applied_rule_ids=set())
        assert (summary.matched, summary.stale, summary.unevaluated) == (0, 0, 2)
