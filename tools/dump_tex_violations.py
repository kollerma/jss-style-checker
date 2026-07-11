"""Python oracle for the spec-018 Rust tex-rule fixture-diff harness.

Calls the REAL rule check functions directly (not through the CLI/JSON
renderer) so `Fix` payloads are visible — same rationale as
`tools/dump_bib_violations.py`.

Usage: python -m tools.dump_tex_violations <rule_id> <path/to/file.tex>
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from texlint.api import ParsedDocument, ToolConfig  # noqa: E402
from texlint.core.parser import parse_tex_file  # noqa: E402
from texlint.journals.jss.rules import (  # noqa: E402
    abbreviations,
    capitalization,
    citations,
    code_style,
    code_width,
    crossrefs,
    house_style,
    markup,
    naming,
    operators,
    preamble,
    structure,
    typography,
)

_CHECKS = {
    "JSS-WIDTH-001": code_width.check_jss_width_001,
    "JSS-CODE-001": code_style.check_jss_code_001,
    "JSS-CODE-002": code_style.check_jss_code_002,
    "JSS-CODE-003": code_style.check_jss_code_003,
    "JSS-TYPO-001": typography.check_jss_typo_001,
    "JSS-TYPO-002": typography.check_jss_typo_002,
    "JSS-TYPO-003": typography.check_jss_typo_003,
    "JSS-TYPO-004": typography.check_jss_typo_004,
    "JSS-CAP-001": capitalization.check_jss_cap_001,
    "JSS-CAP-002": capitalization.check_jss_cap_002,
    "JSS-CAP-004": capitalization.check_jss_cap_004,
    "JSS-ABBR-001": abbreviations.check_jss_abbr_001,
    "JSS-STRUCT-001": structure.check_jss_struct_001,
    "JSS-STRUCT-002": structure.check_jss_struct_002,
    "JSS-STRUCT-003": structure.check_jss_struct_003,
    "JSS-STRUCT-004": structure.check_jss_struct_004,
    "JSS-STRUCT-005": structure.check_jss_struct_005,
    "JSS-STRUCT-006": structure.check_jss_struct_006,
    "JSS-OPER-001": operators.check_jss_oper_001,
    "JSS-OPER-002": operators.check_jss_oper_002,
    "JSS-OPER-003": operators.check_jss_oper_003,
    "JSS-OPER-004": operators.check_jss_oper_004,
    "JSS-HOUSE-001": house_style.check_jss_house_001,
    "JSS-HOUSE-003": house_style.check_jss_house_003,
    "JSS-NAME-001": naming.check_jss_name_001,
    "JSS-PRE-001": preamble.check_jss_pre_001,
    "JSS-PRE-002": preamble.check_jss_pre_002,
    "JSS-PRE-003": preamble.check_jss_pre_003,
    "JSS-PRE-004": preamble.check_jss_pre_004,
    "JSS-PRE-005": preamble.check_jss_pre_005,
    "JSS-PRE-006": preamble.check_jss_pre_006,
    "JSS-PRE-007": preamble.check_jss_pre_007,
    "JSS-PRE-008": preamble.check_jss_pre_008,
    "JSS-CITE-002": citations.check_jss_cite_002,
    "JSS-CITE-003": citations.check_jss_cite_003,
    "JSS-CITE-004": citations.check_jss_cite_004,
    "JSS-MARKUP-001": markup.check_jss_markup_001,
    "JSS-MARKUP-002": markup.check_jss_markup_002,
    "JSS-MARKUP-003": markup.check_jss_markup_003,
    "JSS-MARKUP-004": markup.check_jss_markup_004,
    "JSS-XREF-001": crossrefs.check_jss_xref_001,
    "JSS-XREF-002": crossrefs.check_jss_xref_002,
    "JSS-XREF-003": crossrefs.check_jss_xref_003,
    "JSS-XREF-004": crossrefs.check_jss_xref_004,
    "JSS-XREF-005": crossrefs.check_jss_xref_005,
    "JSS-XREF-006": crossrefs.check_jss_xref_006,
    "JSS-XREF-007": crossrefs.check_jss_xref_007,
}


def dump(rule_id: str, tex_path: Path) -> str:
    check = _CHECKS[rule_id]
    parsed = parse_tex_file(tex_path)
    doc = ParsedDocument(tex_files=(parsed,))
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
        print(
            "usage: python -m tools.dump_tex_violations <rule_id> <path/to/file.tex>",
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
