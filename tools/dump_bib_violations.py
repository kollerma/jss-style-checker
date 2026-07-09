"""Python oracle for the spec-018 Rust bib-rule fixture-diff harness.

Calls the REAL rule check functions directly (not through the CLI/JSON
renderer) so `Fix` payloads are visible — `output/json_output.py`
hardcodes `"fix": null` (see rust/jsslint-core/src/json_output.rs's doc
comment), which would otherwise hide exactly the data these rules'
auto-fix behavior needs validating against.

Usage: python -m tools.dump_bib_violations <rule_id> <path/to/file.bib>
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from texlint.api import ParsedDocument, ToolConfig  # noqa: E402
from texlint.core.parser import parse_bib_file  # noqa: E402
from texlint.journals.jss.rules import bibtex, house_style, naming  # noqa: E402

_CHECKS = {
    "JSS-BIBTEX-001": bibtex.check_jss_bibtex_001,
    "JSS-BIBTEX-002": bibtex.check_jss_bibtex_002,
    "JSS-BIBTEX-003": bibtex.check_jss_bibtex_003,
    "JSS-BIBTEX-004": bibtex.check_jss_bibtex_004,
    "JSS-BIBTEX-005": bibtex.check_jss_bibtex_005,
    "JSS-NAME-002": naming.check_jss_name_002,
    "JSS-HOUSE-002": house_style.check_jss_house_002,
}


def dump(rule_id: str, bib_path: Path) -> str:
    check = _CHECKS[rule_id]
    parsed = parse_bib_file(bib_path)
    doc = ParsedDocument(bib_files=(parsed,))
    cfg = ToolConfig()
    violations = sorted(check(doc, cfg), key=lambda v: v.sort_key())

    lines = []
    for v in violations:
        fix = v.fix
        fix_str = "-" if fix is None else f"{fix.start}:{fix.end}:{fix.replacement}"
        lines.append(
            f"{v.rule_id}\t{v.line}\t{v.column}\t{v.message}\t{v.suggestion}\t{fix_str}"
        )
    return "\n".join(lines) + ("\n" if lines else "")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage: python -m tools.dump_bib_violations <rule_id> <path/to/file.bib>", file=sys.stderr)
        return 2
    rule_id, path = argv
    if rule_id not in _CHECKS:
        print(f"unknown rule_id {rule_id!r}; known: {sorted(_CHECKS)}", file=sys.stderr)
        return 2
    sys.stdout.write(dump(rule_id, Path(path)))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
