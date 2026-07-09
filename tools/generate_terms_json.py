"""Generate ``specs/003-jss-rule-catalogue/terms.json`` from ``terms.py``.

Spec 018 (Rust core) needs the canonicalisation lookup tables in a
language-neutral form so ``jsslint-core`` can embed the same data at
build time instead of re-declaring it. ``texlint.journals.jss.terms``
stays the single source of truth; this script only mirrors it.

Invoke from the repository root::

    python -m tools.generate_terms_json          # write the file
    python -m tools.generate_terms_json --check   # exit 1 if the file drifts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_JSON = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "terms.json"

sys.path.insert(0, str(REPO_ROOT / "src"))


def build_payload() -> dict:
    from texlint.journals.jss import terms

    return {
        "languages": sorted(terms.LANGUAGES),
        "r_packages": sorted(terms.R_PACKAGES),
        "canonical": dict(sorted(terms.CANONICAL.items())),
        "publisher_canonical": dict(sorted(terms.PUBLISHER_CANONICAL.items())),
        "journal_canonical": dict(sorted(terms.JOURNAL_CANONICAL.items())),
        # Order is semantically significant (first match wins) — do NOT sort.
        "publisher_prefix_canonical": [
            list(pair) for pair in terms.PUBLISHER_PREFIX_CANONICAL
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.generate_terms_json",
        description="Generate terms.json from texlint.journals.jss.terms.",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-path", type=Path, default=OUTPUT_JSON)
    args = parser.parse_args(argv)

    rendered = render(build_payload())

    if args.check:
        if not args.output_path.exists():
            print(
                f"error: {args.output_path} does not exist; run without --check first",
                file=sys.stderr,
            )
            return 1
        committed = args.output_path.read_text(encoding="utf-8")
        if committed != rendered:
            print(
                f"error: {args.output_path} is out of date with terms.py. "
                "Re-run without --check.",
                file=sys.stderr,
            )
            return 1
        return 0

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
