"""Baseline files: accept today's findings, fail only on new ones.

Contract: `specs/027-first-time-user-gaps/contracts/baseline-file.md`.

A manuscript that predates the linter produces hundreds of findings on
its first run, and there is no honest way to adopt the tool on it
without a way to say "this is the accepted state; tell me about what
comes next". That is what a baseline file records.

An accepted finding is identified by ``(rule_id, path, message,
suggestion)`` with an occurrence count — deliberately **not** by line
number, which survives no edit at all (1 % of findings across a real
revision round; plan §5.7). The path is relative to the baseline file's
own directory, so the file is portable between checkouts and CI.

This module is pure: no filesystem, no journal, no config. Reading and
writing the file, and computing the ``path_map``, belong to the CLI
layer (Constitution §XIV), which keeps the matcher usable from the
WASM/PyO3/R bindings later without dragging I/O into the core.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass

from texlint.api import Violation

#: The only schema version this release reads or writes.
SCHEMA_VERSION = 1

#: Parse errors signal an incomplete report, not a style finding, so
#: they can never be accepted (`baseline-file.md` C-4 §5).
_PARSE_RULE_ID = "JSS-PARSE-000"

#: The four components of an entry's identity.
Key = tuple[str, str, str, str]


class BaselineError(ValueError):
    """Raised for an unreadable, malformed, or wrong-schema file.

    The CLI turns this into exit 2 with the message on stderr; the text
    itself is a documented per-engine divergence (`baseline-file.md`
    C-10), as it is for `jss-lint diff`.
    """


@dataclass(frozen=True)
class BaselineEntry:
    rule_id: str
    path: str
    message: str
    suggestion: str
    count: int

    @property
    def key(self) -> Key:
        return (self.rule_id, self.path, self.message, self.suggestion)


@dataclass(frozen=True)
class BaselineDocument:
    schema_version: int
    tool_version: str
    ruleset_version: str | None
    journal: str
    entries: tuple[BaselineEntry, ...]


@dataclass(frozen=True)
class BaselineSummary:
    """What the run did with the baseline, for the report surfaces."""

    path: str
    matched: int
    #: Unmatched occurrences whose rule *did* run — findings the author
    #: has since fixed. `--update-baseline` prunes them.
    stale: int
    #: Unmatched occurrences whose rule did not run at all (ignored,
    #: below `--min-confidence`, format-skipped, retired). Counted apart
    #: from `stale` so a CI run with `--min-confidence high` against a
    #: default baseline does not report dozens of phantom fixes.
    unevaluated: int
    ruleset_version: str | None


def _entry_from(raw: object) -> BaselineEntry:
    if not isinstance(raw, Mapping):
        raise BaselineError("entries must be a list of objects")
    try:
        rule_id = raw["rule_id"]
        path = raw["path"]
        message = raw["message"]
        suggestion = raw["suggestion"]
        count = raw["count"]
    except KeyError as exc:
        raise BaselineError(f"entries: missing key {exc.args[0]!r}") from exc
    if not all(
        isinstance(value, str) for value in (rule_id, path, message, suggestion)
    ):
        raise BaselineError(
            "entries: rule_id, path, message, and suggestion must be strings"
        )
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise BaselineError("entries: count must be an integer >= 1")
    return BaselineEntry(
        rule_id=rule_id,
        path=path,
        message=message,
        suggestion=suggestion,
        count=count,
    )


def parse(text: str) -> BaselineDocument:
    """Read a baseline file. Raises :class:`BaselineError` on any defect."""
    try:
        payload = json.loads(text)
    except ValueError as exc:
        raise BaselineError(f"not valid JSON: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise BaselineError("document must be a JSON object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise BaselineError(
            f"unsupported schema_version {payload.get('schema_version')!r} "
            f"(this release reads {SCHEMA_VERSION})"
        )
    journal = payload.get("journal")
    if not isinstance(journal, str):
        raise BaselineError("journal must be a string")
    tool_version = payload.get("tool_version")
    if not isinstance(tool_version, str):
        raise BaselineError("tool_version must be a string")
    ruleset_version = payload.get("ruleset_version")
    if ruleset_version is not None and not isinstance(ruleset_version, str):
        raise BaselineError("ruleset_version must be a string or null")
    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list):
        raise BaselineError("entries must be a list")
    return BaselineDocument(
        schema_version=SCHEMA_VERSION,
        tool_version=tool_version,
        ruleset_version=ruleset_version,
        journal=journal,
        # Sorted on read as well as on write, so a hand-edited file
        # round-trips to the canonical byte order.
        entries=tuple(sorted(
            (_entry_from(raw) for raw in raw_entries),
            key=lambda e: (e.path, e.rule_id, e.message, e.suggestion),
        )),
    )


def build(
    violations: Iterable[Violation],
    *,
    path_map: Mapping[str, str],
    tool_version: str,
    ruleset_version: str | None,
    journal: str,
) -> BaselineDocument:
    """Accept every reported finding.

    ``path_map`` maps a parsed file's path, as violations carry it, to
    the baseline-relative posix path. A finding whose file is absent
    from the map is dropped rather than written: it could never be
    matched again, so an entry for it would be stale forever.
    """
    counts: Counter[Key] = Counter()
    for violation in violations:
        if violation.rule_id == _PARSE_RULE_ID:
            continue
        path = path_map.get(str(violation.file))
        if path is None:
            continue
        counts[
            (violation.rule_id, path, violation.message, violation.suggestion or "")
        ] += 1
    entries = tuple(
        BaselineEntry(
            rule_id=rule_id,
            path=path,
            message=message,
            suggestion=suggestion,
            count=count,
        )
        # Sorted by (path, rule_id, message, suggestion): a human
        # reviewing the diff of an updated baseline reads it file by file.
        for (rule_id, path, message, suggestion), count in sorted(
            counts.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2], kv[0][3])
        )
    )
    return BaselineDocument(
        schema_version=SCHEMA_VERSION,
        tool_version=tool_version,
        ruleset_version=ruleset_version,
        journal=journal,
        entries=entries,
    )


def dumps(doc: BaselineDocument) -> str:
    """Serialise. No timestamp, no host-specific field, sorted keys —
    so two engines and two runs produce byte-identical files."""
    payload = {
        "schema_version": doc.schema_version,
        "tool_version": doc.tool_version,
        "ruleset_version": doc.ruleset_version,
        "journal": doc.journal,
        "entries": [
            {
                "rule_id": e.rule_id,
                "path": e.path,
                "message": e.message,
                "suggestion": e.suggestion,
                "count": e.count,
            }
            for e in doc.entries
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


class BaselineMatcher:
    """The :data:`texlint.api.Suppressor` that hides accepted findings.

    Entries form a multiset: each match decrements the remaining count,
    so the *n*-th occurrence of an accepted finding is reported once the
    accepted count is exhausted. The engine offers findings in
    :meth:`Violation.sort_key` order, which makes *which* occurrences
    are hidden deterministic and identical in both engines.
    """

    def __init__(
        self, doc: BaselineDocument, path_map: Mapping[str, str]
    ) -> None:
        self._remaining: Counter[Key] = Counter()
        for entry in doc.entries:
            self._remaining[entry.key] += entry.count
        self._path_map = path_map
        self._ruleset_version = doc.ruleset_version
        self._matched = 0

    def __call__(self, violation: Violation) -> bool:
        path = self._path_map.get(str(violation.file))
        if path is None:
            return False
        key = (
            violation.rule_id,
            path,
            violation.message,
            violation.suggestion or "",
        )
        if self._remaining.get(key, 0) <= 0:
            return False
        self._remaining[key] -= 1
        self._matched += 1
        return True

    def summary(
        self, path: str, applied_rule_ids: AbstractSet[str]
    ) -> BaselineSummary:
        stale = 0
        unevaluated = 0
        for (rule_id, _path, _message, _suggestion), remaining in (
            self._remaining.items()
        ):
            if remaining <= 0:
                continue
            if rule_id in applied_rule_ids:
                stale += remaining
            else:
                unevaluated += remaining
        return BaselineSummary(
            path=path,
            matched=self._matched,
            stale=stale,
            unevaluated=unevaluated,
            ruleset_version=self._ruleset_version,
        )
