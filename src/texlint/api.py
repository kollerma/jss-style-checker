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


# ---------------------------------------------------------------------------
# Verbatim-environment contract
# ---------------------------------------------------------------------------
#
# Single source of truth for "this environment's body is code / literal
# text, not prose". Two consumers MUST stay in sync, which is why the
# sets live here on the public surface:
#
#   * ``texlint.core.parser`` neutralises TeX-special characters inside
#     these environments before strict parsing (length-preserving), and
#   * rule modules treat content inside them as non-prose (skip
#     prose-style checks; CODE-* / WIDTH-* rules target the
#     ``CODE_DISPLAY_ENVS`` subset).
#
# Historical note: these used to be two hand-maintained lists that
# drifted apart — ``lstlisting`` was neutralised by the parser but not
# recognised as verbatim by the rules, so markup rules fired (and
# auto-fixed!) inside code listings.

#: Sweave / knitr / jss.cls code-display environments. CODE-* and
#: WIDTH-* rules lint the *content* of these.
CODE_DISPLAY_ENVS: frozenset[str] = frozenset(
    {
        "verbatim",
        "Verbatim",
        "Code",
        "CodeInput",
        "CodeOutput",
        "Sinput",
        "Soutput",
        "Scode",
        "Schunk",
        "CodeChunk",
    }
)

#: Authored-code (input) subset of :data:`CODE_DISPLAY_ENVS`. The
#: program-output environments (``CodeOutput`` / ``Soutput``) are
#: excluded: their content is verbatim tool output, not author-written
#: code, so code-*style* rules (CODE-001/002/003) must not fire on it —
#: you cannot restyle what R printed, and CODE-003's auto-fix would
#: corrupt the recorded output. WIDTH-001 still targets the full
#: :data:`CODE_DISPLAY_ENVS`, since output lines must also fit the
#: column limit.
CODE_INPUT_ENVS: frozenset[str] = CODE_DISPLAY_ENVS - {"CodeOutput", "Soutput"}

#: Other literal-body environments: their content is not prose, but it
#: is not JSS code-display either (so CODE-* / WIDTH-* do not apply).
LISTING_ENVS: frozenset[str] = frozenset(
    {"lstlisting", "alltt", "tabbing", "verbatim*"}
)

#: Every environment whose body must be neutralised by the parser and
#: skipped by prose rules.
VERBATIM_ENVS: frozenset[str] = CODE_DISPLAY_ENVS | LISTING_ENVS


class CategoryStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class FixSuggestion:
    """Reserved structured-fix payload. Spec 008 supersedes this with :class:`Fix`."""

    description: str


@dataclass(frozen=True)
class Fix:
    """A single text-edit auto-fix payload (spec 008).

    Byte offsets are 0-based, half-open. ``replacement`` is the literal
    UTF-8 text to substitute. ``confidence``:

      * ``"safe"``: the engine applies it under ``--fix`` without
        further gating.
      * ``"review"``: the engine still applies it, but the rule's
        author flagged it for human attention; reserved for a future
        ``--fix-confidence safe`` filter.
    """

    start: int
    end: int
    replacement: str
    description: str
    confidence: Literal["safe", "review"] = "safe"


@dataclass(frozen=True)
class Violation:
    file: Path
    line: int
    column: int | None
    rule_id: str
    severity: Severity
    message: str
    suggestion: str | None = None
    fix: Fix | FixSuggestion | None = None

    def sort_key(self) -> tuple[str, int, int, int, str]:
        # (file, line, column-bucket, column-value, rule_id).
        # column None sorts before any integer; we encode that with a bucket
        # (0 for None, 1 for int) and a default column value of 0.
        bucket = 0 if self.column is None else 1
        col = 0 if self.column is None else self.column
        return (str(self.file), self.line, bucket, col, self.rule_id)


RuleCheck = Callable[["ParsedDocument", "ToolConfig"], Iterator[Violation]]
RuleCheckProject = Callable[["ParsedProject"], Iterable[Violation]]


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

    ``check_project`` (spec 013 follow-up) is an optional companion
    callable that receives the entire :class:`ParsedProject` instead
    of a single :class:`ParsedDocument`. It runs only when the engine
    is invoked with a ``ParsedProject``; defaults to ``None`` so
    existing per-document rules keep working unchanged. A rule MAY
    populate both ``check`` and ``check_project``; the engine then
    runs both when given a project.
    """

    id: str
    category: str
    severity: Severity
    message_template: str
    authority: str
    check: RuleCheck
    formats: frozenset[str] | None = None
    # JSS-guide citation surface (spec 007). Both default to empty/None
    # so existing rules keep working until they are backfilled. The
    # catalogue contract test enforces population for citable
    # categories; tool-side rules use the sentinel
    # ``guide_section = "internal"``, ``guide_url = None``.
    guide_section: str = ""
    guide_url: str | None = None
    # Spec 013 follow-up: optional whole-project check. ``None`` means
    # the rule is per-document only.
    check_project: RuleCheckProject | None = None
    # Measured-precision confidence tier. ``"high"`` is the default for
    # mechanical rules; heuristic rules whose corpus precision sits
    # below the gate carry ``"medium"`` or ``"low"`` (sourced from the
    # eval-jss precision history via the rule catalogue). The engine
    # skips rules below ``ToolConfig.min_confidence``; renderers may
    # surface the tier so readers can weigh a finding accordingly.
    confidence: Literal["high", "medium", "low"] = "high"


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
    # Confidence floor: rules whose measured-precision tier sits below
    # this are skipped (reported in ``skipped_rules``). ``"low"`` (the
    # default) runs everything; ``"medium"`` drops low-confidence rules;
    # ``"high"`` keeps only the mechanical ~100%-precision rules.
    min_confidence: Literal["low", "medium", "high"] = "low"
    # Exit-code policy: the minimum severity that makes the CLI exit 1.
    # ``"warning"`` (the default) lets info-severity advisories (e.g.
    # the missing-DOI rule) pass CI while still reporting them;
    # ``"info"`` (the pre-0.2 behaviour) fails on any violation;
    # ``"error"`` fails only on errors. Error-severity parse failures
    # always exit 2.
    fail_on: Literal["error", "warning", "info"] = "warning"
    # Per-rule severity overrides, keyed by rule id. Applied centrally
    # by the engine after suppression filtering, so every renderer
    # (terminal / JSON / SARIF / LSP) and the exit-code policy agree.
    # TOML shape: ``[severity_overrides]`` with ``"JSS-CAP-003" = "info"``.
    severity_overrides: Mapping[str, Severity] = field(default_factory=dict)


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


@dataclass(frozen=True)
class ParsedProject:
    """A multi-file project rooted at a single user-passed file.

    Spec 013 surface. Built by ``texlint.core.resolver.resolve``; consumed
    by rules that need cross-file context via :attr:`Rule.check_project`.

    Fields:
      * ``root`` — the file the user invoked the linter against.
      * ``documents`` — every reachable :class:`ParsedDocument` in
        depth-first resolution order. Each entry holds the parsed view
        of one file (i.e., a single-file ``ParsedDocument``).
      * ``tree`` — adjacency list mapping each file to its direct
        ``\\input`` / ``\\include`` / ``\\subfile`` / ``\\bibliography``
        references. A leaf file maps to the empty tuple.
    """

    root: Path
    documents: tuple[ParsedDocument, ...]
    tree: dict[Path, tuple[Path, ...]]


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
