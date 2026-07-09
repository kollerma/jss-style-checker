"""Python oracle for the spec-018 Rust BibTeX parser's fixture-diff
harness. Calls the REAL `texlint.core.parser.parse_bib_source` (not raw
`bibtexparser`) so the duplicate-key / duplicate-field re-insertion
policy documented in `rust/jsslint-core/src/bib/parser.rs` is exactly
what's being diffed against.

`rust/jsslint-core/src/bib/debug.rs::dump` emits the identical format;
`rust/jsslint-core/tests/bib_parity.rs` diffs the two outputs.

Usage: python -m tools.dump_bib_entries <path/to/file.bib>
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from texlint.core.parser import parse_bib_source  # noqa: E402


def _entry_line(source: str, entry) -> str:
    fields = sorted(entry.fields_dict.items(), key=lambda kv: kv[0].lower())
    field_str = "|".join(f"{k.lower()}={v.value.strip()}" for k, v in fields)
    return f"ENTRY\t{entry.key}\t{entry.entry_type.lower()}\t{entry.start_line}\t{field_str}"


def dump(source: str) -> str:
    parsed = parse_bib_source(source, Path("<fixture>"))
    library = parsed.library

    lines: list[str] = []
    for entry in library.entries:
        lines.append(_entry_line(source, entry))

    dup_keys = []
    for block in getattr(library, "failed_blocks", ()) or ():
        if type(block).__name__ == "DuplicateBlockKeyBlock":
            key = getattr(block, "key", "") or ""
            start = getattr(block, "start_line", 0) or 0
            dup_keys.append(f"DUPKEY\t{key}\t{start}")
    dup_keys.sort()
    lines.extend(dup_keys)

    dup_fields = []
    for block in getattr(library, "failed_blocks", ()) or ():
        if type(block).__name__ == "DuplicateFieldKeyBlock":
            start = getattr(block, "start_line", 0) or 0
            names = ",".join(sorted(getattr(block, "duplicate_keys", ()) or ()))
            dup_fields.append(f"DUPFIELD\t{start}\t{names}")
    dup_fields.sort()
    lines.extend(dup_fields)

    return "\n".join(lines) + ("\n" if lines else "")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python -m tools.dump_bib_entries <path/to/file.bib>", file=sys.stderr)
        return 2
    path = Path(argv[0])
    source = path.read_text(encoding="utf-8")
    sys.stdout.write(dump(source))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
