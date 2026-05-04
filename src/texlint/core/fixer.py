"""Auto-fix engine for spec 008.

Public entry-point :func:`apply_fixes` takes a :class:`ComplianceReport`
that already carries one or more :class:`Violation`s with a non-None
``fix`` payload, partitions them by file, resolves overlapping
ranges deterministically (data-model §6), and either prints a
unified diff (``mode="dry-run"``), applies the fixes via
``tempfile`` + ``os.replace`` (``mode="write"``), or steps through
them interactively (``mode="interactive"``).

After every per-file rewrite the engine MUST re-validate the file
by re-parsing + re-linting; if a fixed `(rule_id, line)` re-appears,
the engine rolls back to the cached pre-fix bytes (Constitution
§VII).
"""

from __future__ import annotations

import difflib
import os
import sys
import tempfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TextIO

from texlint.api import ComplianceReport, Fix, Violation

ApplyMode = Literal["write", "dry-run", "interactive"]
SkipReason = Literal["conflict", "rule-not-selected", "user-skipped"]
RejectReason = Literal["regression", "permission-denied"]


@dataclass(frozen=True)
class FixApplication:
    file: Path
    fix: Fix
    rule_id: str


@dataclass(frozen=True)
class FixSkip:
    file: Path
    fix: Fix
    rule_id: str
    reason: SkipReason


@dataclass(frozen=True)
class FixRejection:
    file: Path
    fix: Fix
    rule_id: str
    reason: RejectReason


@dataclass(frozen=True)
class FixReport:
    applied: tuple[FixApplication, ...]
    skipped: tuple[FixSkip, ...]
    rejected: tuple[FixRejection, ...]


@dataclass(frozen=True)
class _Candidate:
    file: Path
    fix: Fix
    rule_id: str
    line: int


def _candidates(violations: Iterable[Violation]) -> list[_Candidate]:
    out: list[_Candidate] = []
    for v in violations:
        if isinstance(v.fix, Fix):
            out.append(_Candidate(v.file, v.fix, v.rule_id, v.line))
    return out


def _resolve_conflicts(
    candidates: Sequence[_Candidate],
) -> tuple[list[_Candidate], list[FixSkip]]:
    """Partition fixes for a single file into (applied, skipped).

    Algorithm (research §5): sort by ``Fix.start``, scan and group
    overlapping intervals into clusters, pick a deterministic winner
    per cluster.
    """
    if not candidates:
        return [], []

    ordered = sorted(candidates, key=lambda c: c.fix.start)
    applied: list[_Candidate] = []
    skipped: list[FixSkip] = []
    cluster: list[_Candidate] = []
    cluster_end = -1

    def flush() -> None:
        nonlocal cluster, cluster_end
        if not cluster:
            return
        winner = min(
            cluster,
            key=lambda c: (
                0 if c.fix.confidence == "safe" else 1,
                c.rule_id,
                c.fix.start,
                c.fix.end,
            ),
        )
        applied.append(winner)
        for c in cluster:
            if c is not winner:
                skipped.append(FixSkip(c.file, c.fix, c.rule_id, "conflict"))
        cluster = []

    for c in ordered:
        if c.fix.start >= cluster_end:
            flush()
            cluster = [c]
            cluster_end = c.fix.end
        else:
            cluster.append(c)
            cluster_end = max(cluster_end, c.fix.end)
    flush()
    return applied, skipped


def _apply_to_text(text: str, fixes: Sequence[_Candidate]) -> str:
    """Apply fixes to ``text`` in reverse-position order so earlier
    offsets are not shifted by later edits (FR-007).

    Note: pylatexenc reports ``pos`` as a byte offset; for the typical
    JSS manuscript (mostly ASCII), 1 byte == 1 Python str character so
    naive slicing is correct. Multibyte content is a known imperfection
    deferred to a follow-up spec.
    """
    new = text
    for c in sorted(fixes, key=lambda c: c.fix.start, reverse=True):
        new = new[: c.fix.start] + c.fix.replacement + new[c.fix.end :]
    return new


def _atomic_write(target: Path, contents: bytes) -> None:
    """Tempfile + os.replace per Constitution §VII / spec FR-003."""
    parent = target.parent
    fd, tmp_path = tempfile.mkstemp(prefix=".jss-lint.", dir=parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(contents)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:  # pragma: no cover - some VFS layers don't fsync
                pass
        os.replace(tmp_path, target)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:  # pragma: no cover
            pass
        raise


def _unified_diff(file: Path, before: str, after: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=str(file),
            tofile=str(file),
        )
    )


def _re_validate(
    target: Path,
    rule_id_lines_before: set[tuple[str, int]],
) -> bool:
    """Re-parse + re-lint *target*. Return True iff none of the
    `(rule_id, line)` pairs in ``rule_id_lines_before`` re-appear in
    the post-fix report. ``False`` triggers rollback in the caller.

    Implementation note: the spec-008 engine reuses the existing
    pipeline. To avoid circular imports, lazy-load the engine inside
    the function.
    """
    # Local imports to dodge the circular boot path between
    # texlint.core.engine -> .api -> ... -> texlint.core.fixer.
    from texlint.config import load as load_config
    from texlint.core.engine import load_journal, parse_document, run

    cfg = load_config({}, target.parent)
    document = parse_document([target])
    try:
        journal = load_journal(cfg.journal)
    except Exception:  # pragma: no cover - already validated upstream
        return True
    report = run(cfg, document, journal)
    after = {(v.rule_id, v.line) for v in report.violations}
    return rule_id_lines_before.isdisjoint(after)


def apply_fixes(
    report: ComplianceReport,
    *,
    mode: ApplyMode = "write",
    rules: frozenset[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> FixReport:
    """Apply auto-fixes from *report* per spec 008."""
    out = stdout or sys.stdout
    err = stderr or sys.stderr
    inp = stdin or sys.stdin

    candidates = _candidates(report.violations)
    if rules is not None:
        before_filter = candidates
        candidates = [c for c in candidates if c.rule_id in rules]
        rule_skips: list[FixSkip] = [
            FixSkip(c.file, c.fix, c.rule_id, "rule-not-selected")
            for c in before_filter
            if c.rule_id not in rules
        ]
    else:
        rule_skips = []

    by_file: dict[Path, list[_Candidate]] = {}
    for c in candidates:
        by_file.setdefault(c.file, []).append(c)

    applied_all: list[FixApplication] = []
    skipped_all: list[FixSkip] = list(rule_skips)
    rejected_all: list[FixRejection] = []

    for path, fixes in sorted(by_file.items(), key=lambda x: str(x[0])):
        per_file_applied, per_file_skipped = _resolve_conflicts(fixes)
        skipped_all.extend(per_file_skipped)

        if not per_file_applied:
            continue

        try:
            before = path.read_text(encoding="utf-8")
        except OSError as exc:
            for c in per_file_applied:
                rejected_all.append(
                    FixRejection(c.file, c.fix, c.rule_id, "permission-denied")
                )
            err.write(f"jss-lint: {path}: {exc}\n")
            continue

        accepted: list[_Candidate] = []
        if mode == "interactive":
            for c in per_file_applied:
                hunk = _unified_diff(
                    path,
                    before,
                    _apply_to_text(before, [c]),
                )
                out.write(hunk)
                out.write(f"Apply fix for {c.rule_id} at line {c.line}? [y/n/a/q] ")
                out.flush()
                reply = (inp.readline() or "q").strip().lower()
                if reply == "y":
                    accepted.append(c)
                elif reply == "a":
                    accepted.append(c)
                    accepted.extend(per_file_applied[per_file_applied.index(c) + 1 :])
                    break
                elif reply == "q":
                    skipped_all.extend(
                        FixSkip(x.file, x.fix, x.rule_id, "user-skipped")
                        for x in per_file_applied[per_file_applied.index(c) :]
                        if x not in accepted
                    )
                    break
                else:
                    skipped_all.append(FixSkip(c.file, c.fix, c.rule_id, "user-skipped"))
        else:
            accepted = list(per_file_applied)

        if not accepted:
            continue

        after = _apply_to_text(before, accepted)
        if mode == "dry-run":
            out.write(_unified_diff(path, before, after))
            applied_all.extend(
                FixApplication(c.file, c.fix, c.rule_id) for c in accepted
            )
            continue

        # mode == "write" or "interactive" with accepted fixes.
        _atomic_write(path, after.encode("utf-8"))

        rule_id_lines_before = {(c.rule_id, c.line) for c in accepted}
        if not _re_validate(path, rule_id_lines_before):
            # Roll back.
            _atomic_write(path, before.encode("utf-8"))
            rejected_all.extend(
                FixRejection(c.file, c.fix, c.rule_id, "regression")
                for c in accepted
            )
            for c in accepted:
                err.write(
                    f"jss-lint: {c.rule_id} fix rejected (regression on rewrite); "
                    f"file rolled back: {path}\n"
                )
            continue

        applied_all.extend(
            FixApplication(c.file, c.fix, c.rule_id) for c in accepted
        )

    return FixReport(
        applied=tuple(applied_all),
        skipped=tuple(skipped_all),
        rejected=tuple(rejected_all),
    )
