"""Public data model for ``texlint``.

Rule authors and third-party journals import from here. Everything under
``texlint.core`` and ``texlint.output`` is internal.

All dataclasses are frozen. Enum values serialise to strings.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Literal


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class CategoryStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class FixSuggestion:
    """Reserved structured-fix payload. Step 4 adds offsets and replacement text."""

    description: str


@dataclass(frozen=True)
class Violation:
    file: Path
    line: int
    column: int | None
    rule_id: str
    severity: Severity
    message: str
    suggestion: str | None = None
    fix: FixSuggestion | None = None

    def sort_key(self) -> tuple[str, int, int, int, str]:
        # (file, line, column-bucket, column-value, rule_id).
        # column None sorts before any integer; we encode that with a bucket
        # (0 for None, 1 for int) and a default column value of 0.
        bucket = 0 if self.column is None else 1
        col = 0 if self.column is None else self.column
        return (str(self.file), self.line, bucket, col, self.rule_id)


RuleCheck = Callable[["ParsedDocument", "ToolConfig"], Iterator[Violation]]


@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    severity: Severity
    message_template: str
    authority: str
    check: RuleCheck
    formats: frozenset[str] | None = None


@dataclass(frozen=True)
class RuleCategory:
    id: str
    title: str
    rules: tuple[Rule, ...]


@dataclass(frozen=True)
class CategorySummary:
    category_id: str
    title: str
    status: CategoryStatus
    rules_applied: int
    rules_passed: int
    violations: tuple[Violation, ...] = ()

    @classmethod
    def build(
        cls,
        *,
        category_id: str,
        title: str,
        rules_applied: int,
        rules_passed: int = 0,
        violations: tuple[Violation, ...] = (),
    ) -> "CategorySummary":
        if rules_applied == 0:
            status = CategoryStatus.SKIPPED
        elif violations:
            status = CategoryStatus.FAIL
        else:
            status = CategoryStatus.PASS
        return cls(
            category_id=category_id,
            title=title,
            status=status,
            rules_applied=rules_applied,
            rules_passed=rules_passed,
            violations=violations,
        )


@dataclass(frozen=True)
class ComplianceReport:
    tool_version: str
    journal_id: str
    violations: tuple[Violation, ...]
    categories: tuple[CategorySummary, ...]
    compliance_percentage: float | None


@dataclass(frozen=True)
class ToolConfig:
    journal: str = "jss"
    mode: Literal["author", "reviewer"] = "author"
    output: Literal["terminal", "json", "html"] = "terminal"
    ignore_rules: frozenset[str] = field(default_factory=frozenset)
    verbose: bool = False
    code_width: int = 80


@dataclass(frozen=True)
class ParsedTexFile:
    path: Path
    source: str
    nodes: tuple[Any, ...]
    walker: Any
    violations: tuple[Violation, ...] = ()


@dataclass(frozen=True)
class ParsedBibFile:
    path: Path
    source: str
    library: Any
    violations: tuple[Violation, ...] = ()


@dataclass(frozen=True)
class ParsedDocument:
    tex_files: tuple[ParsedTexFile, ...] = ()
    bib_files: tuple[ParsedBibFile, ...] = ()

    def all_files(self) -> Iterable[ParsedTexFile | ParsedBibFile]:
        yield from self.tex_files
        yield from self.bib_files

    def all_violations(self) -> Iterator[Violation]:
        for f in self.all_files():
            yield from f.violations

    def files_for_rule(self, rule: Rule) -> Iterator[ParsedTexFile | ParsedBibFile]:
        if rule.formats is None:
            yield from self.all_files()
            return
        for f in self.all_files():
            if f.path.suffix in rule.formats:
                yield f


class JournalRuleModule(ABC):
    id: ClassVar[str]

    @abstractmethod
    def categories(self) -> tuple[RuleCategory, ...]:  # pragma: no cover - abstract
        ...

    def rules(self) -> tuple[Rule, ...]:
        return tuple(r for c in self.categories() for r in c.rules)


class JournalNotFoundError(LookupError):
    """Raised when ``--journal <id>`` does not resolve to any registered entry point."""


class InvalidJournalError(TypeError):
    """Raised when a registered entry point does not satisfy the ``JournalRuleModule`` contract."""
