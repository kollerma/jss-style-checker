# Data Model: Conformance Report

**Phase**: 1
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. `ConformanceSummary`

```python
@dataclass(frozen=True)
class ConformanceSummary:
    title: str | None              # from preamble or --title override
    author: str | None             # from preamble or --author override
    file_count: int                # 1 for single-file; >1 for multi-file projects (spec 013)
    run_date: str                  # ISO-8601 date
    linter_version: str
    commit_hash: str | None        # from git rev-parse, or None

    score_percent: int             # rounded conformance score
    rules_passing: int             # numerator
    rules_total_active: int        # denominator (excluding ignored + tool-side)

    error_count: int
    warning_count: int
    info_count: int

    top_five: tuple[TopFiveEntry, ...]    # max length 5
    fix_me_first: tuple[FixMeItem, ...]
```

### TopFiveEntry

```python
@dataclass(frozen=True)
class TopFiveEntry:
    rule_id: str
    count: int
    example_file: Path
    example_line: int
    example_excerpt: str          # ≤80 chars
    guide_section: str
    guide_url: str | None
```

### FixMeItem

```python
@dataclass(frozen=True)
class FixMeItem:
    rule_id: str
    severity: Severity
    count: int
    precision: float | None       # None when DB absent or rule has no row
```

`fix_me_first` is sorted by `(severity ascending, -precision,
rule_id ascending)`. `top_five` is sorted by `(-count,
rule_id ascending)`.

## 2. `render_report` signature

```python
def render_report(
    summary: ConformanceSummary,
    *,
    fmt: Literal["md", "html", "pdf"],
    out: Path | TextIO | None = None,
) -> bytes | str: ...
```

| Parameter   | Purpose                                                                                |
| ----------- | -------------------------------------------------------------------------------------- |
| `summary`   | Pre-computed `ConformanceSummary` (the building of which is a sibling function).       |
| `fmt`       | Output format.                                                                         |
| `out`       | Output sink. `Path` → write to file; `TextIO` → write to stream; `None` → return.      |

The function returns `str` for `md`/`html` and `bytes` for
`pdf`. When `out` is set, the return value is the same as
when `out` is `None` (the caller may choose).

## 3. `_compute_summary` signature

```python
def _compute_summary(
    report: ComplianceReport,
    document: ParsedDocument | ParsedProject,
    *,
    title_override: str | None,
    author_override: str | None,
    db_path: Path | None,
) -> ConformanceSummary: ...
```

A pure function. Encapsulates: metadata extraction (title,
author), score computation, severity counts, top-5
selection, fix-me ordering. The DB read is the only I/O.

## 4. Score computation

```python
ignored = set(cfg.ignore_rules)
tool_side = {"internal", "parse"}

active = [
    r for r in catalogue
    if r.rule_id not in ignored
    and r.category not in tool_side
]
denominator = len(active)

violating_rules = {v.rule_id for v in report.violations}
numerator = sum(
    1 for r in active
    if r.rule_id not in violating_rules
)

score_percent = round(100 * numerator / denominator) if denominator > 0 else 100
```

When `denominator == 0` (every rule ignored), the score is
`n/a`; spec §Edge Cases.

## 5. CLI surface

```text
Usage: jss-lint report [OPTIONS] PATH

Options:
  --format [md|html|pdf]   Output format (default: md).
  --out FILE               Write to FILE (default: stdout for md; required for html/pdf).
  --title TEXT             Manuscript title override.
  --author TEXT            Manuscript author override.
  -h, --help               Show this message and exit.
```

The `--ignore-rules` and `--journal` root options are
honoured (they apply to the lint pass that produces
`ComplianceReport`).

## 6. Templates

Three Jinja2 templates under
`src/texlint/output/templates/`:

| Template                  | Purpose                                                              |
| ------------------------- | -------------------------------------------------------------------- |
| `conformance.md.j2`       | Markdown body. Six sections per spec FR-003.                         |
| `conformance.html.j2`     | Standalone HTML page. Reuses the spec-001 stylesheet.                |
| `conformance.pdf.j2`      | Print-CSS HTML. Fed to WeasyPrint for one-page A4 / US Letter output.|

The three templates render the SAME `ConformanceSummary`;
no template-side data lookup.

## 7. PDF surface

```python
# src/texlint/output/pdf.py — only when [pdf] extra installed
def render_pdf(html_str: str) -> bytes:
    try:
        import weasyprint
    except ImportError as exc:
        raise PdfNotAvailable(
            'PDF support not installed; install with pip install "jss-lint[pdf]"'
        ) from exc
    return weasyprint.HTML(string=html_str).write_pdf()
```

The `PdfNotAvailable` exception is caught in
`cli.py::report` and converted to exit 2 with the install
hint message.

## 8. Out of scope

| Item                                            | Reason                                                                  |
| ----------------------------------------------- | ----------------------------------------------------------------------- |
| Severity-weighted score                         | Out per Clarifications §2.                                              |
| LaTeX → PDF rendering                           | Out per research §1.                                                     |
| Multi-page PDF for >100-violation manuscripts   | Acceptable per spec edge cases; no special handling.                     |
| Localised report (non-English)                  | Out — the existing catalogue strings are English; localisation is its own spec. |
| Cross-manuscript comparison report              | Out — spec 016 (`jss-lint diff`) covers the across-runs comparison.      |
