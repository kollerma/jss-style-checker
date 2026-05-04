"""Public data model for ``texlint``.

Rule authors and third-party journals import from here. Everything under
``texlint.core`` and ``texlint.output`` is internal.

All dataclasses are frozen. Enum values serialise to strings.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Literal


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


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
    """A single checkable style rule.

    ``formats`` is an input-format filter (spec 005). Valid values:
      * ``None`` (default) — applies to every input format.
      * ``frozenset({"tex"})`` — pure ``.tex`` inputs only.
      * ``frozenset({"tex", "rnw"})`` — ``.tex`` and stripped ``.Rnw``
        (Sweave) inputs — the most common narrowing.
      * ``frozenset({"rmd"})`` — ``.Rmd``-specific rules (reserved).

    Prior to spec 005 this field was documented as a file-suffix
    filter (``{".tex", ".bib"}``); the semantics changed to an
    input-format filter. Existing rules with ``formats=None`` continue
    to work correctly under both readings.
    """

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
    ) -> CategorySummary:
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
class SkippedRule:
    """A rule that was NOT evaluated on the current run because its
    ``formats`` filter excluded every input format present.

    Emitted in ``ComplianceReport.skipped_rules``; surfaced in
    ``--verbose`` output (spec 005 FR-008, FR-009).
    """

    rule_id: str
    reason: str


@dataclass(frozen=True)
class ComplianceReport:
    tool_version: str
    journal_id: str
    violations: tuple[Violation, ...]
    categories: tuple[CategorySummary, ...]
    compliance_percentage: float | None
    skipped_rules: tuple[SkippedRule, ...] = ()


@dataclass(frozen=True)
class ToolConfig:
    journal: str = "jss"
    mode: Literal["author", "reviewer"] = "author"
    output: Literal["terminal", "json", "html", "sarif"] = "terminal"
    ignore_rules: frozenset[str] = field(default_factory=frozenset)
    verbose: bool = False
    code_width: int = 80
    source_root: Path = field(default_factory=Path.cwd)


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
class RmdHeading:
    level: int
    text: str
    line: int  # 1-based


@dataclass(frozen=True)
class RmdProse:
    text: str
    line: int
    n_lines: int


@dataclass(frozen=True)
class RmdCode:
    lang: str
    body: str
    open_line: int
    close_line: int


@dataclass(frozen=True)
class ParsedRmdFile:
    path: Path
    source: str
    yaml_frontmatter: Mapping[str, object] = field(default_factory=dict)
    headings: tuple[RmdHeading, ...] = ()
    prose_blocks: tuple[RmdProse, ...] = ()
    code_blocks: tuple[RmdCode, ...] = ()
    latex_fragments: tuple[ParsedTexFile, ...] = ()
    violations: tuple[Violation, ...] = ()


# Valid input-format tags for Rule.formats (spec 005).
_VALID_FORMATS: frozenset[str] = frozenset({"tex", "rnw", "rmd", "bib"})


def _file_format(f: Any) -> str:
    """Return the input-format tag ('tex' / 'rnw' / 'rmd' / 'bib') for a
    parsed-file object. Derived from the file path suffix plus dataclass
    type; case-insensitive suffix matching.
    """
    if isinstance(f, ParsedRmdFile):
        return "rmd"
    if isinstance(f, ParsedBibFile):
        return "bib"
    suffix = getattr(getattr(f, "path", None), "suffix", "").lower()
    if suffix == ".bib":
        return "bib"
    if suffix == ".rnw":
        return "rnw"
    if suffix == ".rmd":
        return "rmd"
    return "tex"


@dataclass(frozen=True)
class ParsedDocument:
    tex_files: tuple[ParsedTexFile, ...] = ()
    bib_files: tuple[ParsedBibFile, ...] = ()
    rmd_files: tuple[ParsedRmdFile, ...] = ()

    def all_files(self) -> Iterable[ParsedTexFile | ParsedBibFile | ParsedRmdFile]:
        yield from self.tex_files
        yield from self.bib_files
        yield from self.rmd_files

    def all_tex_like(self) -> Iterator[ParsedTexFile]:
        """Yield every tex-shaped parsed view: native ``.tex`` files
        plus raw-LaTeX islands extracted from ``.Rmd`` prose blocks.

        Rule modules that want to apply to Rmd prose AS WELL AS tex
        files iterate this helper instead of ``doc.tex_files``.
        """
        yield from self.tex_files
        for rmd in self.rmd_files:
            yield from rmd.latex_fragments

    def all_violations(self) -> Iterator[Violation]:
        for f in self.all_files():
            yield from f.violations

    def files_for_rule(
        self, rule: Rule
    ) -> Iterator[ParsedTexFile | ParsedBibFile | ParsedRmdFile]:
        """Yield parsed-file objects matching ``rule.formats``.

        Input-format filter (spec 005 semantics). A rule with
        ``formats={"tex", "rnw"}`` matches tex and rnw inputs; a rule
        with ``formats=None`` matches every input.

        Bibliography-inspecting rules (``formats=None``) still iterate
        ``bib_files`` because ``None`` means "all formats".
        """
        if rule.formats is None:
            yield from self.all_files()
            return
        for f in self.all_files():
            if _file_format(f) in rule.formats:
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
