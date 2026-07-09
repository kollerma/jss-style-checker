"""Generate ``specs/003-jss-rule-catalogue/latex-macro-specs.json`` from
pylatexenc's default macro/environment context database.

Spec 018 (Rust core) hand-writes a tolerant LaTeX tokenizer that must
replicate pylatexenc's known-macro argument parsing (see
``texlint.core.parser`` and ``rust/jsslint-core/src/tex/``). Rather than
hand-porting ~240 macro/environment argspecs by reading pylatexenc's
Python source, this script extracts them mechanically from the live
``pylatexenc.latexwalker.get_default_latex_context_db()`` object — the
exact database ``LatexWalker(tolerant_parsing=...)`` uses — so the two
languages read the same source of truth instead of a hand-copied one
that can silently drift as pylatexenc versions change.

Invoke from the repository root::

    python -m tools.generate_latex_specs_json          # write the file
    python -m tools.generate_latex_specs_json --check   # exit 1 if stale
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_JSON = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "latex-macro-specs.json"


def build_payload() -> dict:
    from pylatexenc.latexwalker import get_default_latex_context_db

    db = get_default_latex_context_db()

    macros: dict[str, str] = {}
    verbatim_macros: list[str] = []
    for cat in db.category_list:
        for spec in db.iter_macro_specs(categories=[cat]):
            ap = spec.args_parser
            cls = type(ap).__name__
            if cls == "MacroStandardArgsParser":
                # Later categories override earlier ones on name clash,
                # matching db.get_macro_spec's own category-list-order
                # precedence (natbib's \cite wins over latex-base's, etc.).
                macros[spec.macroname] = ap.argspec or ""
            elif cls == "VerbatimArgsParser":
                verbatim_macros.append(spec.macroname)
            else:
                raise AssertionError(
                    f"unhandled args parser {cls} for macro {spec.macroname!r}"
                )

    envs: dict[str, str] = {}
    verbatim_envs: list[str] = []
    for cat in db.category_list:
        for spec in db.iter_environment_specs(categories=[cat]):
            ap = spec.args_parser
            cls = type(ap).__name__
            if cls == "MacroStandardArgsParser":
                envs[spec.environmentname] = ap.argspec or ""
            elif cls == "VerbatimArgsParser":
                verbatim_envs.append(spec.environmentname)
            else:
                raise AssertionError(
                    f"unhandled args parser {cls} for environment {spec.environmentname!r}"
                )

    # "Specials": literal token sequences pylatexenc tokenizes as their
    # own node (not a macro, not plain chars) — e.g. `~` (nbsp), `&`
    # (tab align), `--`/`---` (dash ligatures), ``` `` ```/`''` (smart
    # quote ligatures), `` !` ``/`` ?` `` (Spanish punctuation
    # ligatures). None take arguments in the default database.
    specials: list[str] = []
    for cat in db.category_list:
        for spec in db.iter_specials_specs(categories=[cat]):
            assert spec.args_parser is None, (
                f"unexpected args_parser for specials {spec.specials_chars!r}"
            )
            specials.append(spec.specials_chars)

    return {
        "macros": dict(sorted(macros.items())),
        "verbatim_macros": sorted(verbatim_macros),
        "environments": dict(sorted(envs.items())),
        "verbatim_environments": sorted(verbatim_envs),
        # Longest-first so a tokenizer doing literal-prefix matching
        # naturally prefers "---" over its "--" prefix.
        "specials": sorted(set(specials), key=lambda s: (-len(s), s)),
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.generate_latex_specs_json",
        description="Extract pylatexenc's default macro/environment argspecs to JSON.",
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
                f"error: {args.output_path} is out of date with pylatexenc's "
                "default context db. Re-run without --check.",
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
