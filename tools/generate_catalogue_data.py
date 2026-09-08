"""Generate ``src/texlint/journals/jss/_catalogue_data.py`` from the catalogue.

Invoke from the repository root::

    python -m tools.generate_catalogue_data          # write the file
    python -m tools.generate_catalogue_data --check  # exit 1 if the file
                                                     # or the fingerprint drifts
    python -m tools.generate_catalogue_data --stamp-fingerprint \\
        --ruleset-version YYYY-MM-DD                 # re-stamp the rule set

The source of truth is ``specs/003-jss-rule-catalogue/catalogue.yaml``.
The output is a generated Python module; runtime imports from it never
parse YAML.

Rule-set provenance (spec 027 item D): the catalogue carries a
``ruleset_version`` date guarded by a ``ruleset_fingerprint`` over both
the catalogue-declared contract fields of every active rule and the
message/suggestion wording in ``messages.json``. ``--check`` fails when
the stored fingerprint no longer matches; ``--stamp-fingerprint``
refuses to keep the old date once the fingerprint has moved. Users'
baseline entries are keyed on that wording, so a silent rewording would
strand them with no version signal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from tools._catalogue_validate import CatalogueError, validate

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOGUE_YAML = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "catalogue.yaml"
MESSAGES_JSON = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "messages.json"
RECALL_JSON = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "recall.json"
OUTPUT_PY = REPO_ROOT / "src" / "texlint" / "journals" / "jss" / "_catalogue_data.py"
TEMPLATE_DIR = REPO_ROOT / "docs" / "jss-template"

#: Catalogue-declared fields that form the contract half of the
#: fingerprint. Deliberately narrower than the whole rule record:
#: prose fields users never key on (``explanation``, ``notes``, the
#: example fragments) may be improved in a patch release.
_FINGERPRINT_RULE_FIELDS: tuple[str, ...] = (
    "rule_id",
    "category",
    "severity",
    "description",
    "guide_section",
    "confidence",
    "auto_fixable",
)

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


def render(doc: Mapping[str, Any], recall: Mapping[str, Any] | None = None) -> str:
    recall = recall or {"rules": {}}
    recall_rules: Mapping[str, Any] = recall.get("rules", {})
    recall_run = {
        "run_timestamp": recall.get("run_timestamp", ""),
        "corpus_hash": recall.get("corpus_hash", ""),
        "min_plants": recall.get("min_plants", 0),
        "papers": recall.get("papers", 0),
        "tp": sum(c["tp"] for c in recall_rules.values()),
        "fn": sum(c["fn"] for c in recall_rules.values()),
    }
    categories: list[str] = list(doc["categories"])
    rules = sorted(
        (dict(r) for r in doc["rules"]),
        key=lambda r: _sort_key(r, categories),
    )
    retired: list[str] = list(doc.get("retired_rule_ids") or ())
    deterministic: list[str] = list(doc.get("deterministic_rule_ids") or ())

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
        # Measured-precision confidence tier; emit only when the YAML
        # narrows it ("high" is the runtime default for absent keys).
        if rule.get("confidence"):
            out.append(f"        \"confidence\": {_py_str(rule['confidence'])},\n")
        # spec 007: optional citation surface; emit only when present
        # in the YAML so existing rules without a backfill stay clean.
        if rule.get("guide_section"):
            out.append(f"        \"guide_section\": {_py_str(rule['guide_section'])},\n")
        if rule.get("guide_url"):
            out.append(f"        \"guide_url\": {_py_str(rule['guide_url'])},\n")
        # spec 009: optional explain surface — per-rule prose plus
        # optional bad/good fixture fragments. Same pattern as the
        # citation fields: emit only when populated.
        if rule.get("explanation"):
            out.append(f"        \"explanation\": {_py_str(rule['explanation'])},\n")
        if rule.get("example_bad"):
            out.append(f"        \"example_bad\": {_py_str(rule['example_bad'])},\n")
        if rule.get("example_good"):
            out.append(f"        \"example_good\": {_py_str(rule['example_good'])},\n")
        out.append("    }),\n")
    out.append("})\n\n")

    out.append("RETIRED_RULE_IDS: frozenset[str] = frozenset({\n")
    for rid in sorted(retired):
        out.append(f"    {_py_str(rid)},\n")
    out.append("})\n\n")

    out.append(
        "# Mechanically-decidable rules: the linter is authoritative, so the\n"
        "# eval pipeline auto-accepts their firings (see catalogue.yaml).\n"
    )
    out.append("DETERMINISTIC_RULE_IDS: frozenset[str] = frozenset({\n")
    for rid in sorted(deterministic):
        out.append(f"    {_py_str(rid)},\n")
    out.append("})\n\n")

    out.append(
        "# Rule-set provenance (spec 027 item D). GUIDE_SOURCE is the\n"
        "# report/JSON rendering; GUIDE_EDITION and SOURCE_VENDORED_AT are its\n"
        "# parts, which `--version` line 3 lays out differently.\n"
    )
    out.append(f"RULESET_VERSION: str = {_py_str(doc['ruleset_version'])}\n")
    out.append(f"RULESET_FINGERPRINT: str = {_py_str(doc['ruleset_fingerprint'])}\n")
    out.append(f"GUIDE_EDITION: str = {_py_str(doc['guide_edition'])}\n")
    out.append(f"SOURCE_VENDORED_AT: str = {_py_str(doc['source_vendored_at'])}\n")
    guide_source = f"{doc['guide_edition']} ({doc['source_vendored_at']})"
    out.append(f"GUIDE_SOURCE: str = {_py_str(guide_source)}\n\n")

    out.append(
        "# Measured recall, from specs/003-jss-rule-catalogue/recall.json\n"
        "# (spec 027 item A). RECALL_RUN pins the run; RECALL holds the\n"
        "# per-rule counts. Rules absent from RECALL are unmeasured.\n"
    )
    out.append("RECALL_RUN: Mapping[str, object] = MappingProxyType({\n")
    for key in ("run_timestamp", "corpus_hash", "min_plants", "papers", "tp", "fn"):
        value = recall_run[key]
        literal = _py_str(value) if isinstance(value, str) else repr(value)
        out.append(f"    {_py_str(key)}: {literal},\n")
    out.append("})\n\n")
    out.append("RECALL: Mapping[str, tuple[int, int]] = MappingProxyType({\n")
    for rule_id, counts in sorted(recall_rules.items()):
        out.append(
            f"    {_py_str(rule_id)}: ({counts['tp']}, {counts['fn']}),\n"
        )
    out.append("})\n\n")

    out.append("# Rollout order (from catalogue.yaml top-level categories field).\n")
    out.append("ROLLOUT_ORDER: tuple[str, ...] = (\n")
    for cat in categories:
        out.append(f"    {_py_str(cat)},\n")
    out.append(")\n")

    return "".join(out)


def fingerprint_input(
    doc: Mapping[str, Any], messages: Mapping[str, Any]
) -> str:
    """Canonical JSON the fingerprint hashes. Stable across hosts."""
    rules = [
        {
            field: (
                rule.get(field, "")
                if field == "guide_section"
                else rule.get(field, "high")
                if field == "confidence"
                else rule[field]
            )
            for field in _FINGERPRINT_RULE_FIELDS
        }
        for rule in sorted(doc["rules"], key=lambda r: r["rule_id"])
    ]
    return json.dumps(
        {"rules": rules, "messages": messages},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def compute_fingerprint(doc: Mapping[str, Any], messages: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(
        fingerprint_input(doc, messages).encode("utf-8")
    ).hexdigest()
    return f"sha256:{digest}"


def _load_messages(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_recall(path: Path) -> Mapping[str, Any]:
    """The shipped recall snapshot, or empty when it does not exist yet.

    Deliberately not part of the fingerprint: re-measuring recall on a
    bigger corpus changes what the tool *reports*, not which findings it
    produces, so it must not force a rule-set date bump (users' baselines
    are unaffected).
    """
    if not path.exists():
        return {"rules": {}}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _rewrite_top_key(text: str, key: str, value: str) -> str:
    """Replace one single-line top-level ``key: "value"`` scalar.

    PyYAML cannot round-trip this file (the comment header carries the
    retirement rationale that the whole catalogue is documented by), so
    stamping is a line rewrite, not a load-and-dump.
    """
    pattern = re.compile(rf'^{re.escape(key)}: *"[^"]*"$', re.MULTILINE)
    replaced, count = pattern.subn(f'{key}: "{value}"', text)
    if count != 1:
        raise SystemExit(
            f"error: expected exactly one top-level `{key}:` line to rewrite, "
            f"found {count}"
        )
    return replaced


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
    parser.add_argument(
        "--stamp-fingerprint",
        action="store_true",
        help=(
            "Rewrite ruleset_fingerprint (and, with --ruleset-version, the "
            "rule-set date) in catalogue.yaml, then regenerate."
        ),
    )
    parser.add_argument(
        "--ruleset-version",
        default=None,
        metavar="YYYY-MM-DD",
        help="The rule-set date to stamp. Required when the fingerprint changed.",
    )
    parser.add_argument("--yaml-path", type=Path, default=CATALOGUE_YAML)
    parser.add_argument("--messages-path", type=Path, default=MESSAGES_JSON)
    parser.add_argument("--recall-path", type=Path, default=RECALL_JSON)
    parser.add_argument("--output-path", type=Path, default=OUTPUT_PY)
    parser.add_argument("--template-dir", type=Path, default=TEMPLATE_DIR)
    args = parser.parse_args(argv)

    if not args.yaml_path.exists():
        print(f"error: {args.yaml_path} does not exist", file=sys.stderr)
        return 2
    if not args.messages_path.exists():
        print(
            f"error: {args.messages_path} does not exist; run "
            "`python -m tools.generate_message_snapshot` first",
            file=sys.stderr,
        )
        return 2

    doc = _load_doc(args.yaml_path)
    errors = validate(doc, template_dir=args.template_dir)
    if errors:
        return _report_and_exit(errors)

    messages = _load_messages(args.messages_path)
    computed = compute_fingerprint(doc, messages)
    recall = _load_recall(args.recall_path)

    if args.stamp_fingerprint:
        return _stamp(args, doc, computed)

    rendered = render(doc, recall)

    if args.check:
        if doc["ruleset_fingerprint"] != computed:
            print(
                f"error: {args.yaml_path}'s ruleset_fingerprint is stale "
                f"(stored {doc['ruleset_fingerprint']}, computed {computed}). "
                "The rule set changed: re-run "
                "`python -m tools.generate_catalogue_data --stamp-fingerprint "
                "--ruleset-version YYYY-MM-DD` with today's date.",
                file=sys.stderr,
            )
            return 1
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


def _stamp(
    args: argparse.Namespace, doc: Mapping[str, Any], computed: str
) -> int:
    """Rewrite the two provenance keys, then regenerate the Python module.

    The policy gate lives here: once the fingerprint has moved, the date
    must be named explicitly and may never move backwards. A rule set
    that changed silently is exactly the failure users' baselines cannot
    survive. Re-stamping the *same* date is allowed — two rule-set
    changes on one day share one date — but only as a deliberate act,
    never as the tool's default.
    """
    stored_version = doc["ruleset_version"]
    changed = computed != doc["ruleset_fingerprint"]
    if changed and args.ruleset_version is None:
        print(
            "error: the rule-set fingerprint changed, so --ruleset-version is "
            f"required (stored date {stored_version!r}). A rule, its severity, "
            "or the wording users' baselines key on has moved:\n"
            "  python -m tools.generate_catalogue_data --stamp-fingerprint "
            "--ruleset-version YYYY-MM-DD",
            file=sys.stderr,
        )
        return 1
    new_version = args.ruleset_version or stored_version
    if new_version < stored_version:
        print(
            f"error: --ruleset-version {new_version} is older than the stored "
            f"{stored_version}; the rule-set date never moves backwards.",
            file=sys.stderr,
        )
        return 1

    text = args.yaml_path.read_text(encoding="utf-8")
    text = _rewrite_top_key(text, "ruleset_version", new_version)
    text = _rewrite_top_key(text, "ruleset_fingerprint", computed)
    _atomic_write(args.yaml_path, text)
    print(f"stamped {args.yaml_path}: {new_version} {computed}")

    updated = _load_doc(args.yaml_path)
    errors = validate(updated, template_dir=args.template_dir)
    if errors:
        return _report_and_exit(errors)
    _atomic_write(args.output_path, render(updated, _load_recall(args.recall_path)))
    print(f"wrote {args.output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover — CLI entry point
    raise SystemExit(main())
