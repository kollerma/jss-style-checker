"""Spec 016 — `jss-lint diff` engine tests."""

from __future__ import annotations

from texlint.diff import compare


def _v(rule_id: str, file: str = "m.tex", line: int = 1, message: str = "x") -> dict:
    return {
        "file": file,
        "line": line,
        "column": 1,
        "rule_id": rule_id,
        "severity": "warning",
        "message": message,
        "suggestion": None,
        "fix": None,
    }


class TestCompare:
    def test_identical_inputs(self) -> None:
        a = [_v("JSS-CITE-002")]
        diff = compare(a, list(a))
        assert diff.fixed == ()
        assert diff.introduced == ()
        assert len(diff.unchanged) == 1

    def test_fix_only(self) -> None:
        old = [_v("JSS-CITE-002")]
        new = []
        diff = compare(old, new)
        assert len(diff.fixed) == 1
        assert diff.introduced == ()

    def test_introduced_only(self) -> None:
        old = []
        new = [_v("JSS-CITE-002")]
        diff = compare(old, new)
        assert diff.fixed == ()
        assert len(diff.introduced) == 1

    def test_mixed(self) -> None:
        old = [_v("JSS-A"), _v("JSS-B")]
        new = [_v("JSS-A"), _v("JSS-C")]
        diff = compare(old, new)
        fixed_ids = [v["rule_id"] for v in diff.fixed]
        intro_ids = [v["rule_id"] for v in diff.introduced]
        unchanged_ids = [v["rule_id"] for v in diff.unchanged]
        assert fixed_ids == ["JSS-B"]
        assert intro_ids == ["JSS-C"]
        assert unchanged_ids == ["JSS-A"]

    def test_line_drift_default_separates(self) -> None:
        old = [_v("JSS-A", line=10)]
        new = [_v("JSS-A", line=30)]
        diff = compare(old, new)
        # Default identity includes line: line drift => fixed + introduced.
        assert len(diff.fixed) == 1
        assert len(diff.introduced) == 1
        assert len(diff.unchanged) == 0

    def test_ignore_line_drift_collapses(self) -> None:
        old = [_v("JSS-A", line=10)]
        new = [_v("JSS-A", line=30)]
        diff = compare(old, new, ignore_line_drift=True)
        assert diff.fixed == ()
        assert diff.introduced == ()
        assert len(diff.unchanged) == 1

    def test_rule_rename(self) -> None:
        old = [_v("JSS-OLD")]
        new = [_v("JSS-NEW")]
        diff = compare(old, new, rule_renames={"JSS-OLD": "JSS-NEW"})
        assert diff.fixed == ()
        assert diff.introduced == ()
        assert len(diff.unchanged) == 1

    def test_rule_rename_without_map(self) -> None:
        old = [_v("JSS-OLD")]
        new = [_v("JSS-NEW")]
        diff = compare(old, new)
        assert len(diff.fixed) == 1
        assert len(diff.introduced) == 1
