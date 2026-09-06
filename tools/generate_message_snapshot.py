"""Generate ``specs/003-jss-rule-catalogue/messages.json``.

Invoke from the repository root::

    python -m tools.generate_message_snapshot          # write the file
    python -m tools.generate_message_snapshot --check  # exit 1 if it drifts

The snapshot maps each rule id to the sorted unique ``[message,
suggestion]`` pairs the Python reference engine emits on the per-rule
violation fixtures (``tests/fixtures/violations/**/*-bad.*``) plus the
two resolver-project fixtures that exercise ``JSS-PROJECT-001`` and
``JSS-PROJECT-002`` (the only active rules without a ``-bad`` fixture).

Why it exists: the rule-set fingerprint (spec 027 D4) covers the
*wording* users see, not only the catalogue-declared contract fields. A
baseline entry is keyed on ``(rule_id, path, message, suggestion)``, so
rewording a message or a suggestion invalidates users' baselines. Making
the wording an input to the fingerprint turns any rewording into a
mandatory ``ruleset_version`` bump, which the baseline summary line then
reports back to the user.

This file is Python-only: it is not vendored into the Rust crate or the
R package, and ``build.rs`` never reads it. Rust embeds the *stored*
fingerprint string from ``catalogue.yaml``; the vendored-catalogue sync
test keeps the two equal.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from texlint.api import ToolConfig
from texlint.core.engine import load_journal, parse_document, resolve_project, run

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "violations"
RESOLVER_DIR = REPO_ROOT / "tests" / "fixtures" / "resolver_projects"
OUTPUT_JSON = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "messages.json"

#: Roots whose resolver graph makes ``JSS-PROJECT-001`` (cycle) and
#: ``JSS-PROJECT-002`` (unresolved target) fire. Both are already
#: exercised by ``rust/jsslint-cli/tests/cli_parity.rs``.
_PROJECT_ROOTS: tuple[str, ...] = ("cycle/a.tex", "missing/root.tex")

_PARSE_RULE_ID = "JSS-PARSE-000"


def _bad_fixtures() -> list[Path]:
    return sorted(FIXTURES_DIR.rglob("*-bad.*"))


def _repo_relative(text: str) -> str:
    """Strip the absolute repository prefix out of a message.

    ``JSS-PROJECT-001``'s message quotes the resolved (absolute) paths of
    the cycle it found, and ``resolver.resolve`` canonicalises them, so
    the raw text is host-specific. The fingerprint must be identical on
    every machine, so the checkout prefix is removed; what remains is the
    fixture-relative path, which is exactly the varying part of the
    wording we want to track.
    """
    return text.replace(f"{REPO_ROOT}{os.sep}", "")


def collect(journal_id: str = "jss") -> dict[str, list[list[str]]]:
    """Run the reference engine over every fixture and group the wording.

    Returns ``{rule_id: [[message, suggestion], ...]}`` with the pairs
    sorted and de-duplicated. ``JSS-PARSE-000`` is excluded: its message
    embeds a parser error string, which is not rule wording.
    """
    config = ToolConfig()
    journal = load_journal(journal_id)
    pairs: dict[str, set[tuple[str, str]]] = {}

    def record(violations: Sequence[object]) -> None:
        for violation in violations:
            rule_id = violation.rule_id  # type: ignore[attr-defined]
            if rule_id == _PARSE_RULE_ID:
                continue
            suggestion = violation.suggestion or ""  # type: ignore[attr-defined]
            pairs.setdefault(rule_id, set()).add(
                (
                    _repo_relative(violation.message),  # type: ignore[attr-defined]
                    _repo_relative(suggestion),
                )
            )

    for fixture in _bad_fixtures():
        report = run(config, parse_document([fixture]), journal)
        record(report.violations)

    for relative in _PROJECT_ROOTS:
        project = resolve_project(RESOLVER_DIR / relative)
        report = run(config, project, journal)
        record(report.violations)

    return {
        rule_id: [list(pair) for pair in sorted(entries)]
        for rule_id, entries in sorted(pairs.items())
    }


def render(snapshot: dict[str, list[list[str]]]) -> str:
    return json.dumps(snapshot, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", delete=False, dir=path.parent, prefix=path.name + "."
    ) as tmp:
        tmp.write(content)
        tmp_name = tmp.name
    os.replace(tmp_name, path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.generate_message_snapshot",
        description="Generate messages.json from the per-rule violation fixtures.",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-path", type=Path, default=OUTPUT_JSON)
    args = parser.parse_args(argv)

    rendered = render(collect())

    if args.check:
        if not args.output_path.exists():
            print(
                f"error: {args.output_path} does not exist; run without --check first",
                file=sys.stderr,
            )
            return 1
        if args.output_path.read_text(encoding="utf-8") != rendered:
            print(
                f"error: {args.output_path} is out of date with the violation "
                "fixtures. Re-run without --check, then re-stamp the rule set: "
                "python -m tools.generate_catalogue_data --stamp-fingerprint "
                "--ruleset-version YYYY-MM-DD",
                file=sys.stderr,
            )
            return 1
        return 0

    _atomic_write(args.output_path, rendered)
    print(f"wrote {args.output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover — CLI entry point
    raise SystemExit(main())
