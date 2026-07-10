"""Python oracle for the spec-018 Rust LSP conversions differential
harness.

Calls the real `texlint.lsp.conversions` functions directly on a
synthetic Violation (JSON on stdin) so the Rust port's
Violation/Fix -> LSP Diagnostic/CodeAction projections can be
differentially checked without needing a running LSP server.

Usage: python -m tools.dump_lsp_conversions < input.json
Input: {"violation": {file, line, column, rule_id, severity, message,
        suggestion, fix: {start, end, replacement, description,
        confidence} | null}, "source": str | null, "guide_url": str | null,
        "uri": str}
Output: JSON {"diagnostic": {...}, "code_action": {...} | null}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from texlint.api import Fix, Severity, Violation  # noqa: E402
from texlint.lsp.conversions import (  # noqa: E402
    violation_to_code_action,
    violation_to_diagnostic,
)


def main() -> int:
    payload = json.loads(sys.stdin.read())
    v_in = payload["violation"]
    fix_in = v_in.get("fix")
    fix = (
        Fix(
            start=fix_in["start"],
            end=fix_in["end"],
            replacement=fix_in["replacement"],
            description=fix_in["description"],
            confidence=fix_in.get("confidence", "safe"),
        )
        if fix_in is not None
        else None
    )
    v = Violation(
        file=Path(v_in["file"]),
        line=v_in["line"],
        column=v_in.get("column"),
        rule_id=v_in["rule_id"],
        severity=Severity(v_in["severity"]),
        message=v_in["message"],
        suggestion=v_in.get("suggestion"),
        fix=fix,
    )
    source = payload.get("source")
    guide_url = payload.get("guide_url")
    uri = payload.get("uri", "file:///m.tex")

    diagnostic = violation_to_diagnostic(v, guide_url=guide_url, source=source)
    code_action = None
    if source is not None:
        code_action = violation_to_code_action(v, source=source, uri=uri)

    print(json.dumps({"diagnostic": diagnostic, "code_action": code_action}, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
