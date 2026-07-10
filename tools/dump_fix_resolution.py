"""Python oracle for the spec-018 Rust fixer conflict-resolution
fixture-diff harness.

Calls the real `_resolve_conflicts` function directly on a synthetic
list of candidates (JSON on stdin) so the Rust port's clustering /
winner-selection logic can be differentially checked without needing
real rule violations.

Usage: python -m tools.dump_fix_resolution < candidates.json
Input: a JSON array of objects with keys rule_id, line, start, end,
       replacement, confidence (confidence optional, default "safe").
Output: two tab-separated sections (applied / skipped), one candidate
        per line as "<rule_id>\t<start>\t<end>\t<replacement>".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from texlint.api import Fix  # noqa: E402
from texlint.core.fixer import _Candidate, _resolve_conflicts  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    raw = sys.stdin.read()
    items = json.loads(raw)
    candidates = [
        _Candidate(
            file=Path("dummy.tex"),
            fix=Fix(
                start=item["start"],
                end=item["end"],
                replacement=item["replacement"],
                description="test",
                confidence=item.get("confidence", "safe"),
            ),
            rule_id=item["rule_id"],
            line=item["line"],
        )
        for item in items
    ]
    applied, skipped = _resolve_conflicts(candidates)
    for c in applied:
        print(f"{c.rule_id}\t{c.fix.start}\t{c.fix.end}\t{c.fix.replacement}")
    print("---")
    for s in skipped:
        print(f"{s.rule_id}\t{s.fix.start}\t{s.fix.end}\t{s.fix.replacement}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
