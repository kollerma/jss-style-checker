"""Spec 011 — pure-Python projections from texlint types to LSP shapes.

Importable without ``pygls``; the actual LSP server is gated behind
the ``[lsp]`` extra and lives in a sibling module.

LSP semantics:

* ``range.start.line`` / ``end.line`` are 0-based.
* ``range.start.character`` is 0-based.
* ``severity``: 1=Error, 2=Warning, 3=Information, 4=Hint.

The texlint engine is 1-based for both line and column (see
:class:`texlint.api.Violation`).
"""

from __future__ import annotations

import re
from typing import Any

from texlint.api import Fix, Severity, Violation

LSP_SEVERITY: dict[Severity, int] = {
    Severity.ERROR: 1,
    Severity.WARNING: 2,
    Severity.INFO: 3,
}


_TOKEN_AT_RE = re.compile(r"\S+")


def violation_to_diagnostic(
    v: Violation,
    *,
    guide_url: str | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    """Project a :class:`Violation` to an LSP ``Diagnostic`` dict.

    With ``source`` (the document text), the range spans the token at
    the violation's column — or, when the violation carries no column,
    the whole (rstripped) line — so editors render a visible squiggle.
    Without ``source`` the range is zero-width (back-compat for
    callers that have no document text at hand).
    """
    line = max(v.line - 1, 0)
    col = max((v.column or 1) - 1, 0)
    end_col = col
    if source is not None:
        lines = source.splitlines()
        if line < len(lines):
            text = lines[line].rstrip()
            if v.column is None:
                col = 0
                end_col = len(text)
            else:
                col = min(col, len(text))
                m = _TOKEN_AT_RE.match(text, col)
                end_col = m.end() if m else len(text)
    diag: dict[str, Any] = {
        "range": {
            "start": {"line": line, "character": col},
            "end": {"line": line, "character": end_col},
        },
        "severity": LSP_SEVERITY[v.severity],
        "code": v.rule_id,
        "source": "jss-lint",
        "message": v.message,
    }
    if guide_url:
        diag["codeDescription"] = {"href": guide_url}
    return diag


def _byte_offset_to_lsp_position(text: str, offset: int) -> dict[str, int]:
    """Convert a 0-based byte offset into the source to an LSP
    ``Position`` (0-based line + 0-based character). Naive ASCII path
    matches spec 008's auto-fix engine; multibyte content is
    deferred."""
    chunk = text[:offset]
    line = chunk.count("\n")
    last_nl = chunk.rfind("\n")
    char = offset - (last_nl + 1)
    return {"line": line, "character": char}


def fix_to_text_edit(fix: Fix, source: str) -> dict[str, Any]:
    """Project a :class:`Fix` to an LSP ``TextEdit`` dict, given the
    source bytes of the file being edited."""
    return {
        "range": {
            "start": _byte_offset_to_lsp_position(source, fix.start),
            "end": _byte_offset_to_lsp_position(source, fix.end),
        },
        "newText": fix.replacement,
    }


def violation_to_code_action(
    v: Violation, *, source: str, uri: str
) -> dict[str, Any] | None:
    """Project a :class:`Violation` carrying a :class:`Fix` to an LSP
    ``CodeAction``. Returns ``None`` when the violation has no fix."""
    if not isinstance(v.fix, Fix):
        return None
    edit = fix_to_text_edit(v.fix, source)
    return {
        "title": v.fix.description,
        "kind": "quickfix",
        "edit": {"changes": {uri: [edit]}},
    }
