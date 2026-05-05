"""Spec 016 follow-up — diff renderer + schema-validation tests."""

from __future__ import annotations

import json

import pytest

from texlint.diff import (
    DiffReport,
    SchemaMismatch,
    compare,
    render_json,
    render_markdown,
    render_terminal,
    validate_payload,
)


def _v(rule_id: str, *, file: str = "m.tex", line: int = 1) -> dict:
    return {
        "rule_id": rule_id,
        "file": file,
        "line": line,
        "column": 1,
        "message": f"violation of {rule_id}",
        "severity": "warning",
    }


class TestRenderTerminal:
    def test_summary_line(self) -> None:
        diff = DiffReport(fixed=(_v("A"),), introduced=(), unchanged=(_v("B"),))
        out = render_terminal(diff)
        assert "fixed: 1 introduced: 0 unchanged: 1" in out

    def test_groups_present(self) -> None:
        diff = DiffReport(
            fixed=(_v("A"),),
            introduced=(_v("B"),),
            unchanged=(_v("C"),),
        )
        out = render_terminal(diff)
        assert "== Fixed ==" in out
        assert "== Introduced ==" in out
        assert "== Unchanged ==" in out

    def test_empty_groups_omitted(self) -> None:
        diff = DiffReport(fixed=(), introduced=(), unchanged=())
        out = render_terminal(diff)
        assert "== Fixed ==" not in out
        assert "== Introduced ==" not in out
        assert "== Unchanged ==" not in out


class TestRenderMarkdown:
    def test_h2_sections_always_present(self) -> None:
        diff = DiffReport(fixed=(), introduced=(), unchanged=())
        out = render_markdown(diff)
        assert "## Fixed" in out
        assert "## Introduced" in out
        assert "## Unchanged" in out

    def test_summary_bold(self) -> None:
        diff = DiffReport(fixed=(_v("A"),), introduced=(), unchanged=())
        out = render_markdown(diff)
        assert "**fixed:** 1" in out
        assert "**introduced:** 0" in out

    def test_violation_bullet(self) -> None:
        diff = DiffReport(
            fixed=(),
            introduced=(_v("JSS-X-001", file="m.tex", line=42),),
            unchanged=(),
        )
        out = render_markdown(diff)
        assert "- `JSS-X-001`" in out
        assert "m.tex:42" in out


class TestRenderJson:
    def test_shape(self) -> None:
        diff = DiffReport(fixed=(), introduced=(_v("A"),), unchanged=(_v("B"),))
        out = render_json(diff)
        payload = json.loads(out)
        assert payload["summary"] == {
            "fixed": 0,
            "introduced": 1,
            "unchanged": 1,
        }
        assert isinstance(payload["fixed"], list)
        assert isinstance(payload["introduced"], list)
        assert isinstance(payload["unchanged"], list)
        assert payload["introduced"][0]["rule_id"] == "A"

    def test_deterministic(self) -> None:
        diff = compare([_v("A"), _v("B")], [_v("A"), _v("C")])
        assert render_json(diff) == render_json(diff)


class TestValidatePayload:
    def _ok_payload(self, violations: list[dict] | None = None) -> dict:
        return {
            "tool_version": "0.0.0-test",
            "journal_id": "jss",
            "violations": violations or [],
        }

    def test_happy_path_returns_violations(self) -> None:
        payload = self._ok_payload([_v("A")])
        viols = validate_payload(payload, "test")
        assert len(viols) == 1
        assert viols[0]["rule_id"] == "A"

    def test_non_object_raises(self) -> None:
        with pytest.raises(SchemaMismatch) as exc:
            validate_payload([], "test")
        assert "not a JSON object" in str(exc.value)

    def test_missing_top_level_key(self) -> None:
        with pytest.raises(SchemaMismatch) as exc:
            validate_payload({"violations": []}, "test")
        assert "missing required key" in str(exc.value)

    def test_violations_not_list(self) -> None:
        with pytest.raises(SchemaMismatch) as exc:
            validate_payload(
                {
                    "tool_version": "x",
                    "journal_id": "y",
                    "violations": "not-a-list",
                },
                "test",
            )
        assert "must be a list" in str(exc.value)

    def test_per_violation_missing_key(self) -> None:
        bad = {"rule_id": "A", "file": "m.tex"}  # missing line + message
        with pytest.raises(SchemaMismatch) as exc:
            validate_payload(self._ok_payload([bad]), "test")
        assert "violations[0]" in str(exc.value)

    def test_per_violation_not_object(self) -> None:
        with pytest.raises(SchemaMismatch) as exc:
            validate_payload(self._ok_payload(["string"]), "test")  # type: ignore[list-item]
        assert "not an object" in str(exc.value)
