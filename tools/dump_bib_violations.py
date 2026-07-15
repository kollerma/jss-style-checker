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
from texlint.journals.jss.rules import (  # noqa: E402
    bibtex,
    house_style,
    naming,
    references,
)

_CHECKS = {
    "JSS-BIBTEX-001": bibtex.check_jss_bibtex_001,
    "JSS-BIBTEX-002": bibtex.check_jss_bibtex_002,
    "JSS-BIBTEX-003": bibtex.check_jss_bibtex_003,
    "JSS-BIBTEX-004": bibtex.check_jss_bibtex_004,
    "JSS-BIBTEX-005": bibtex.check_jss_bibtex_005,
    "JSS-NAME-002": naming.check_jss_name_002,
    "JSS-REFS-001": references.check_jss_refs_001,
    "JSS-REFS-003": references.check_jss_refs_003,
    "JSS-REFS-004": references.check_jss_refs_004,
    "JSS-REFS-005": references.check_jss_refs_005,
    "JSS-REFS-006": references.check_jss_refs_006,
    "JSS-REFS-007": references.check_jss_refs_007,
    "JSS-HOUSE-002": house_style.check_jss_house_002,
}


def _format_violations(violations) -> str:
    lines = []
    for v in sorted(violations, key=lambda v: v.sort_key()):
        fix = v.fix
        fix_str = "-" if fix is None else f"{fix.start}:{fix.end}:{fix.replacement}"
        lines.append(
            f"{v.rule_id}\t{v.line}\t{v.column}\t{v.message}\t{v.suggestion}\t{fix_str}"
        )
    return "\n".join(lines) + ("\n" if lines else "")


def dump(rule_id: str, bib_path: Path) -> str:
    parsed = parse_bib_file(bib_path)
    doc = ParsedDocument(bib_files=(parsed,))
    cfg = ToolConfig()
    return _format_violations(_CHECKS[rule_id](doc, cfg))


def dump_all(bib_path: Path) -> dict[str, str]:
    """Run every rule against `bib_path`, parsing it only once.

    Used by the Rust parity harness (`tests/bib_rules_parity.rs`) to cut
    subprocess/reparse overhead ~26x: one process + one parse per fixture
    instead of one per (fixture, rule) pair.
    """
    parsed = parse_bib_file(bib_path)
    doc = ParsedDocument(bib_files=(parsed,))
    cfg = ToolConfig()
    return {rule_id: _format_violations(check(doc, cfg)) for rule_id, check in _CHECKS.items()}


# NUL can't appear in real BibTeX source, so it's a safe frame delimiter for
# `--all` mode's combined output — unlike splitting on newlines, this
# survives a violation's `fix.replacement` containing embedded newlines.
# Must match tools/dump_tex_violations.py's identical convention.
_RULE_SENTINEL = "\x00"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 2 and argv[0] == "--all":
        result = dump_all(Path(argv[1]))
        for rule_id in sorted(result):
            sys.stdout.write(f"{_RULE_SENTINEL}{rule_id}{_RULE_SENTINEL}")
            sys.stdout.write(result[rule_id])
        return 0
    if len(argv) != 2:
        print(
            "usage: python -m tools.dump_bib_violations <rule_id> <path/to/file.bib>\n"
            "       python -m tools.dump_bib_violations --all <path/to/file.bib>",
            file=sys.stderr,
        )
        return 2
    rule_id, path = argv
    if rule_id not in _CHECKS:
        print(f"unknown rule_id {rule_id!r}; known: {sorted(_CHECKS)}", file=sys.stderr)
        return 2
    sys.stdout.write(dump(rule_id, Path(path)))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
