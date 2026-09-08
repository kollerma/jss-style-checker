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
from typing import TYPE_CHECKING, Any, ClassVar, Literal

if TYPE_CHECKING:
    from texlint.core.baseline import BaselineSummary
    from texlint.core.resolver import ResolvedReference


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


#: A caller-supplied filter applied to every finding just before the
#: engine's bookkeeping. Returning ``True`` drops the finding, exactly as
#: an inline ``% jss-lint: ignore`` does — the baseline matcher (spec
#: 027 item B) is the first implementation. Called in
#: :meth:`Violation.sort_key` order within each rule so that *which*
#: occurrences of an identical finding are dropped is deterministic.
Suppressor = Callable[["Violation"], bool]

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
    #: Measured recall pooled over this category's rules, from the
    #: journal's snapshot. ``None`` for a journal with no recall data at
    #: all; a category whose rules have no annotated instances pools to
    #: ``RecallStat(0, 0)`` and renders ``unmeasured``.
    recall: RecallStat | None = None

    @classmethod
    def build(
        cls,
        *,
        category_id: str,
        title: str,
        rules_applied: int,
        rules_passed: int = 0,
        violations: tuple[Violation, ...] = (),
        recall: RecallStat | None = None,
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
            recall=recall,
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
class RecallStat:
    """Measured recall for one rule, or pooled over a category.

    ``tp``/``fn`` are annotated instances of a planted defect that the
    rule did / did not catch, from the shipped snapshot
    (``specs/003-jss-rule-catalogue/recall.json``). Both counts, not a
    ratio, so categories can pool them.

    Below ``min_plants`` instances the state is ``limited`` and **no
    percentage is shown**: a rule with two plants that caught one has
    not been measured at 50 %, and printing that would read as a
    measurement (spec 027 D3).
    """

    tp: int
    fn: int

    @property
    def plants(self) -> int:
        return self.tp + self.fn

    def state(self, min_plants: int) -> Literal["measured", "limited", "unmeasured"]:
        if self.plants == 0:
            return "unmeasured"
        return "limited" if self.plants < min_plants else "measured"

    def percent(self) -> int | None:
        """Integer half-up percentage, or ``None`` with no plants.

        Deliberately integer arithmetic: Python's ``round`` is banker's
        and Rust's ``f64::round`` is half-away, so a float path would
        make the two engines disagree on exactly the values that land on
        .5 (data-model §3.1).
        """
        if self.plants == 0:
            return None
        return (200 * self.tp + self.plants) // (2 * self.plants)

    def label(self, min_plants: int) -> str:
        """What every surface prints: ``81%`` / ``limited (n=4)`` /
        ``unmeasured``."""
        state = self.state(min_plants)
        if state == "unmeasured":
            return "unmeasured"
        if state == "limited":
            return f"limited (n={self.plants})"
        return f"{self.percent()}%"


@dataclass(frozen=True)
class RecallRun:
    """Provenance of the shipped recall snapshot."""

    run_timestamp: str
    corpus_hash: str
    min_plants: int
    #: Annotated papers behind the measurement. Quoted next to the
    #: percentage because "81 %" means something different over 17
    #: papers than over three.
    papers: int
    tp: int
    fn: int

    @property
    def stat(self) -> RecallStat:
        return RecallStat(tp=self.tp, fn=self.fn)


@dataclass(frozen=True)
class CoverageDirective:
    """One provision of one authority, and what the tool does about it.

    ``status`` is ``checked`` (a rule enforces it), ``partial`` (enforced
    in part — ``reason`` says what is missing), ``not_checked`` (a real
    gap), or ``out_of_scope`` (not checkable from the manuscript source
    at all: compilability, graphics legibility, submission metadata).
    Out-of-scope provisions are listed but excluded from the "checks N of
    M" ratio, since they were never checkable.
    """

    id: str
    source: str
    section: str
    provision: str
    status: Literal["checked", "partial", "not_checked", "out_of_scope"]
    rules: tuple[str, ...]
    reason: str = ""


@dataclass(frozen=True)
class CoverageCounts:
    checked: int
    partial: int
    not_checked: int
    out_of_scope: int

    @property
    def checkable(self) -> int:
        """Provisions a source-level linter could check at all."""
        return self.checked + self.partial + self.not_checked

    @property
    def covered(self) -> int:
        return self.checked + self.partial

    @classmethod
    def of(cls, directives: Iterable[CoverageDirective]) -> CoverageCounts:
        tally = {"checked": 0, "partial": 0, "not_checked": 0, "out_of_scope": 0}
        for directive in directives:
            tally[directive.status] += 1
        return cls(**tally)


@dataclass(frozen=True)
class RuleSetInfo:
    """Provenance of a journal's rule set (spec 027 item D).

    ``version`` is a date, not a semantic version: it names *which* rule
    set produced a finding, which is what a baseline file stamps and
    ``--version`` prints. ``fingerprint`` is what forces that date to
    move when a rule or its wording changes. The two guide fields are
    kept apart rather than pre-joined because the two renderings differ:
    ``--version`` writes ``jss.cls 3.3, vendored 2021-05-23`` while JSON
    and the report carry :attr:`guide_source`.

    A journal that ships no provenance leaves every field ``None``; the
    surfaces then render ``n/a`` (``--version``) or ``null`` (JSON).
    """

    version: str | None = None
    fingerprint: str | None = None
    guide_edition: str | None = None
    source_vendored_at: str | None = None
    #: The recall run this rule set ships, or ``None`` for a journal
    #: that publishes no measurement.
    recall: RecallRun | None = None

    @property
    def guide_source(self) -> str | None:
        if self.guide_edition is None:
            return None
        if self.source_vendored_at is None:
            return self.guide_edition
        return f"{self.guide_edition} ({self.source_vendored_at})"


@dataclass(frozen=True)
class ComplianceReport:
    tool_version: str
    journal_id: str
    violations: tuple[Violation, ...]
    categories: tuple[CategorySummary, ...]
    compliance_percentage: float | None
    skipped_rules: tuple[SkippedRule, ...] = ()
    #: What a ``--baseline`` run hid, or ``None`` when no baseline was
    #: applied. Filled in by the CLI *after* :func:`engine.run` — the
    #: engine never sees the file (§XIV); it only takes the matcher as a
    #: :data:`Suppressor`.
    baseline: BaselineSummary | None = None
    #: Provenance of the rule set that produced these findings, copied
    #: from the journal's :meth:`JournalRuleModule.metadata`. Carried on
    #: the report so no renderer has to import a journal package (§IV);
    #: empty for a journal that supplies none.
    rule_set: RuleSetInfo = field(default_factory=RuleSetInfo)
    #: The journal's guide-coverage matrix, or ``None`` when it publishes
    #: none. ``None`` and "everything is checked" are different claims.
    coverage: tuple[CoverageDirective, ...] | None = None


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
    # Optional online DOI resolver, injected by ``jss-lint --crossref``
    # (never from TOML, so the linter stays offline by default). ``None``
    # keeps every rule offline. Called per BibTeX entry as
    # ``(lowercase_field_map, entry_type) -> doi string | None``;
    # JSS-REFS-003 uses it to online-verify and (with ``--fix``) populate
    # missing DOIs.
    doi_resolver: Callable[[Mapping[str, str], str], str | None] | None = None
    # Baseline file to apply (spec 027 item B). TOML key ``baseline``,
    # relative to the ``.jss-lint.toml`` directory; ``--baseline`` wins.
    # There is deliberately no auto-discovery: a file that silences
    # findings must be named, never found (research.md §6).
    baseline: Path | None = None
    # Colour policy for terminal output (spec 027 item F). TOML key
    # `color`; `--color` wins; the environment (NO_COLOR /
    # CLICOLOR_FORCE) beats both, per `texlint.color.should_colorize`.
    # The config records *intent* — the CLI resolves it to a bool and
    # hands that to the renderer.
    color: Literal["auto", "always", "never"] = "auto"


@dataclass(frozen=True)
class ParsedTexFile:
    path: Path
    source: str
    nodes: tuple[Any, ...]
    walker: Any
    violations: tuple[Violation, ...] = ()
    #: Line number of this file's ``source`` within the file on disk,
    #: minus one. ``0`` for ``.tex``/``.ltx``/``.Rnw``, whose sources are
    #: the whole file; for an ``.Rmd`` prose block — parsed as a
    #: standalone LaTeX fragment starting at line 1 — it is the block's
    #: first line minus one. Violations are already offset to
    #: file-authoritative line numbers by the parser; this field lets
    #: anything reading ``source`` directly (inline suppression) do the
    #: same arithmetic.
    line_offset: int = 0


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
      * ``missing`` — references that did not resolve to an existing
        file, one entry per unresolved macro hit. Consumed by
        ``JSS-PROJECT-002``.
    """

    root: Path
    documents: tuple[ParsedDocument, ...]
    tree: dict[Path, tuple[Path, ...]]
    missing: tuple[ResolvedReference, ...] = ()


@dataclass(frozen=True)
class JournalMetadata:
    """Journal-level facts that no rule decides on, but users read.

    Supplied by :meth:`JournalRuleModule.metadata`, copied onto the
    :class:`ComplianceReport` by the engine, and read from there by the
    renderers — so no renderer imports a journal package (Constitution
    §IV).
    """

    rule_set: RuleSetInfo = RuleSetInfo()
    #: Per-rule measured recall, keyed by rule id. Rules absent from the
    #: snapshot are unmeasured; the engine pools these per category.
    recall_by_rule: Mapping[str, RecallStat] = field(default_factory=dict)
    #: The guide-coverage matrix, in file order. Empty for a journal that
    #: publishes none — the surfaces then omit the coverage block rather
    #: than claiming full coverage.
    coverage: tuple[CoverageDirective, ...] = ()


class JournalRuleModule(ABC):
    id: ClassVar[str]

    @abstractmethod
    def categories(self) -> tuple[RuleCategory, ...]:  # pragma: no cover - abstract
        ...

    def rules(self) -> tuple[Rule, ...]:
        return tuple(r for c in self.categories() for r in c.rules)

    def metadata(self) -> JournalMetadata:
        """Provenance and measurement facts about this journal's rules.

        Non-abstract: a third-party journal that supplies nothing keeps
        working and its surfaces degrade to ``n/a`` / ``null``.
        """
        return JournalMetadata()


class JournalNotFoundError(LookupError):
    """Raised when ``--journal <id>`` does not resolve to any registered entry point."""


class InvalidJournalError(TypeError):
    """Raised when a registered entry point does not satisfy the ``JournalRuleModule`` contract."""
