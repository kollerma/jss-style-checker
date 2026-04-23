"""Shared types for the `eval-jss` harness.

Imported by every other `eval/*.py` module; imports nothing from `texlint`
(the harness talks to `jss-lint` only through its CLI, per the spec).

See `specs/002-eval-jss-harness/data-model.md` for the authoritative
description of each type's invariants.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Verdict(str, Enum):
    TRUE_POSITIVE = "true_positive"
    FALSE_POSITIVE = "false_positive"
    UNCERTAIN = "uncertain"


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Paper:
    id: int | None
    doi: str | None
    title: str | None
    year: int | None
    path: Path
    source: str
    status: str


@dataclass(frozen=True)
class Violation:
    id: int | None
    paper_id: int
    rule_id: str
    category: str
    line: int | None
    column: int | None
    message: str
    severity: str
    verdict: Verdict | None
    verdict_reason: str | None
    reviewer: str | None
    first_seen_run_id: int


@dataclass(frozen=True)
class Run:
    id: int | None
    ts: str
    tool_version: str
    papers_scanned: int
    violations_found: int


@dataclass(frozen=True)
class LinterResult:
    exit_code: int
    stdout: str
    stderr: str
    elapsed_seconds: float


@dataclass(frozen=True)
class ClassifyResult:
    verdict: Verdict
    confidence: float
    reason: str


@dataclass(frozen=True)
class ManifestRow:
    jss_doi: str | None
    source: str
    source_id: str
    version: str
    vignette_file: str
    local_path: Path
    sha256: str
