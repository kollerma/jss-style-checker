"""Generate ``src/texlint/journals/jss/_catalogue_data.py`` from the catalogue.

Invoke from the repository root::

    python -m tools.generate_catalogue_data          # write the file
    python -m tools.generate_catalogue_data --check  # exit 1 if the file drifts

The source of truth is ``specs/003-jss-rule-catalogue/catalogue.yaml``.
The output is a generated Python module; runtime imports from it never
parse YAML.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from tools._catalogue_validate import CatalogueError, validate

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOGUE_YAML = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "catalogue.yaml"
OUTPUT_PY = REPO_ROOT / "src" / "texlint" / "journals" / "jss" / "_catalogue_data.py"
TEMPLATE_DIR = REPO_ROOT / "docs" / "jss-template"

_SEVERITY_MAP: Mapping[str, str] = {
    "error": "Severity.ERROR",
    "warning": "Severity.WARNING",
    "info": "Severity.INFO",
}

_HEADER = (
    "# AUTO-GENERATED from specs/003-jss-rule-catalogue/catalogue.yaml.\n"
    "# Do not edit by hand; run `python -m tools.generate_catalogue_data`.\n"
    "\n"
    "from __future__ import annotations\n"
    "\n"
    "from collections.abc import Mapping\n"
    "from types import MappingProxyType\n"
    "\n"
    "from texlint.api import Severity\n"
    "\n"
)


def _rule_id_counter(rule_id: str) -> int:
    return int(rule_id.rsplit("-", 1)[-1])


def _sort_key(rule: Mapping[str, Any], category_order: Sequence[str]) -> tuple[int, int]:
    try:
        idx = category_order.index(rule["category"])
    except ValueError:
        idx = len(category_order)
    return (idx, _rule_id_counter(rule["rule_id"]))


def _py_str(value: str) -> str:
    """Python-literal string. Uses repr so escapes are guaranteed valid."""
    return repr(value)


def render(doc: Mapping[str, Any]) -> str:
    categories: list[str] = list(doc["categories"])
    rules = sorted(
        (dict(r) for r in doc["rules"]),
        key=lambda r: _sort_key(r, categories),
    )
    retired: list[str] = list(doc.get("retired_rule_ids") or ())

    out: list[str] = [_HEADER]

    out.append("# One entry per active rule in catalogue.yaml.\n")
    out.append("RULES: Mapping[str, Mapping[str, object]] = MappingProxyType({\n")
    for rule in rules:
        rule_id = rule["rule_id"]
        category = rule["category"]
        severity = _SEVERITY_MAP[rule["severity"]]
        message = _py_str(rule["description"])
        authority = _py_str(rule["authority"])
        authority_ref = _py_str(rule["authority_ref"])
        inspects = tuple(rule["inspects"])
        inspects_literal = "(" + ", ".join(_py_str(x) for x in inspects)
        inspects_literal += ",)" if len(inspects) == 1 else ")"
        auto_fixable = "True" if rule["auto_fixable"] else "False"
        out.append(f"    {_py_str(rule_id)}: MappingProxyType({{\n")
        out.append(f"        \"category\": {_py_str(category)},\n")
        out.append(f"        \"severity\": {severity},\n")
        out.append(f"        \"message_template\": {message},\n")
        out.append(f"        \"authority\": {authority},\n")
        out.append(f"        \"authority_ref\": {authority_ref},\n")
        out.append(f"        \"inspects\": {inspects_literal},\n")
        out.append(f"        \"auto_fixable\": {auto_fixable},\n")
        # spec 007: optional citation surface; emit only when present
        # in the YAML so existing rules without a backfill stay clean.
        if rule.get("guide_section"):
            out.append(f"        \"guide_section\": {_py_str(rule['guide_section'])},\n")
        if rule.get("guide_url"):
            out.append(f"        \"guide_url\": {_py_str(rule['guide_url'])},\n")
        out.append("    }),\n")
    out.append("})\n\n")

    out.append("RETIRED_RULE_IDS: frozenset[str] = frozenset({\n")
    for rid in sorted(retired):
        out.append(f"    {_py_str(rid)},\n")
    out.append("})\n\n")

    out.append("# Rollout order (from catalogue.yaml top-level categories field).\n")
    out.append("ROLLOUT_ORDER: tuple[str, ...] = (\n")
    for cat in categories:
        out.append(f"    {_py_str(cat)},\n")
    out.append(")\n")

    return "".join(out)


def _load_doc(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _report_and_exit(errors: Sequence[CatalogueError]) -> int:
    print("catalogue.yaml is invalid:", file=sys.stderr)
    for err in errors:
        print(f"  {err}", file=sys.stderr)
    return 2


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
        prog="python -m tools.generate_catalogue_data",
        description="Generate _catalogue_data.py from catalogue.yaml.",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--yaml-path", type=Path, default=CATALOGUE_YAML)
    parser.add_argument("--output-path", type=Path, default=OUTPUT_PY)
    parser.add_argument("--template-dir", type=Path, default=TEMPLATE_DIR)
    args = parser.parse_args(argv)

    if not args.yaml_path.exists():
        print(f"error: {args.yaml_path} does not exist", file=sys.stderr)
        return 2

    doc = _load_doc(args.yaml_path)
    errors = validate(doc, template_dir=args.template_dir)
    if errors:
        return _report_and_exit(errors)

    rendered = render(doc)

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
                f"error: {args.output_path} is out of date with {args.yaml_path}. "
                "Re-run without --check.",
                file=sys.stderr,
            )
            return 1
        return 0

    _atomic_write(args.output_path, rendered)
    print(f"wrote {args.output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover — CLI entry point
    raise SystemExit(main())
