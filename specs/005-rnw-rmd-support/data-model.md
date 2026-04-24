# Phase 1 Data Model — Rnw / Rmd Manuscript Support

All existing types from specs 001–004 are unchanged except where
called out below. This spec introduces one new dataclass
(`ParsedRmdFile`), one new helper method on `ParsedDocument`
(`all_tex_like()`), one new field on `ComplianceReport`
(`skipped_rules`), and amends the semantics of `Rule.formats` (same
field, extended meaning).

## 1. `Rule.formats` — semantics change (API-additive)

**Location**: `src/texlint/api.py`.

**Before (spec 001)**: `formats: frozenset[str] | None` was a
file-suffix filter (`{".tex", ".bib"}`). `ParsedDocument.files_for_rule`
iterated all files and filtered by `f.path.suffix`.

**After (spec 005)**: `formats: frozenset[str] | None` is an
**input-format filter** (`{"tex", "rnw", "rmd"}`). Values:

| Value | Meaning |
|---|---|
| `None` | Rule applies to all input formats (unchanged default). |
| `frozenset({"tex"})` | Rule applies only to pure `.tex` inputs. |
| `frozenset({"tex", "rnw"})` | Rule applies to `.tex` and `.Rnw` (preamble rules). |
| `frozenset({"rmd"})` | Rmd-specific rule (none ship in this spec; placeholder module exists per FR-018). |

**Invariants**:

| # | Invariant | Enforcer |
|---|---|---|
| R-1 | Every `Rule.formats` value is either `None` or a non-empty frozenset whose elements are in `{"tex", "rnw", "rmd"}`. | `test_rule_formats_well_formed` |
| R-2 | `Rule.formats=frozenset({"tex", "rnw"})` rules yield violations on stripped `.Rnw` inputs identical in count and line number to what they yield on the equivalent hand-written `.tex` input (modulo the author's actual content). | `test_rnw_parity` integration test |
| R-3 | Rules with `formats=None` run on every input format without being added to `skipped_rules`. | `test_none_formats_never_skipped` |

**Migration**: spec 004's catalogue had `Rule.formats=None` for all 58
rules. After spec 005 lands, JSS-PRE-001..008 narrow to
`frozenset({"tex", "rnw"})`; the other 50 stay `None`.

## 2. `ParsedRmdFile` — new dataclass

**Location**: `src/texlint/api.py`.

```python
@dataclass(frozen=True)
class ParsedRmdFile:
    path: Path
    source: str                           # original source, unchanged
    yaml_frontmatter: Mapping[str, object]  # empty dict if none / malformed
    headings: tuple[RmdHeading, ...]
    prose_blocks: tuple[RmdProse, ...]
    code_blocks: tuple[RmdCode, ...]
    latex_fragments: tuple[ParsedTexFile, ...]  # one per prose block with tex content
    violations: tuple[Violation, ...] = ()       # JSS-PARSE-000 on malformed input
```

Supporting frozen dataclasses (also in `api.py`):

```python
@dataclass(frozen=True)
class RmdHeading:
    level: int                  # 1..6 (number of '#' in ATX heading)
    text: str
    line: int                   # 1-based

@dataclass(frozen=True)
class RmdProse:
    text: str                   # inline R code (`r expr`) replaced with whitespace
    line: int                   # 1-based start line
    n_lines: int                # number of source lines covered

@dataclass(frozen=True)
class RmdCode:
    lang: str                   # language tag from opening fence, or ''
    body: str
    open_line: int              # 1-based line of opening ```
    close_line: int             # 1-based line of closing ```
```

**Invariants**:

| # | Invariant | Enforcer |
|---|---|---|
| D-1 | `headings`, `prose_blocks`, `code_blocks` line numbers are monotonically increasing within each tuple. | `test_rmd_token_ordering` |
| D-2 | Every `ParsedTexFile` in `latex_fragments` has `path == f"{rmd.path}:block@{start_line}"`. | `test_latex_fragment_path` |
| D-3 | `yaml_frontmatter` is always a `Mapping` (possibly empty); never `None`. | `test_frontmatter_present` |
| D-4 | `violations` contains a `JSS-PARSE-000` if YAML parsing failed or the tokenizer detected an unterminated fence / frontmatter; empty otherwise. | `test_rmd_parse_errors` |
| D-5 | Line numbers in `latex_fragments` violations are source-accurate: the violation's `line` equals `prose.line + pylatexenc_line - 1`. | `test_rmd_latex_line_offset` |

## 3. `ParsedDocument` — additive extensions

**Location**: `src/texlint/api.py`.

Adds `rmd_files` field and `all_tex_like()` helper:

```python
@dataclass(frozen=True)
class ParsedDocument:
    tex_files: tuple[ParsedTexFile, ...] = ()
    bib_files: tuple[ParsedBibFile, ...] = ()
    rmd_files: tuple[ParsedRmdFile, ...] = ()      # NEW

    def all_files(self) -> Iterable[ParsedTexFile | ParsedBibFile | ParsedRmdFile]:
        yield from self.tex_files
        yield from self.bib_files
        yield from self.rmd_files                   # NEW

    def all_tex_like(self) -> Iterator[ParsedTexFile]:
        """Iterate every tex-shaped parsed view: native tex files plus
        raw-LaTeX islands from Rmd prose blocks.
        """
        yield from self.tex_files
        for rmd in self.rmd_files:
            yield from rmd.latex_fragments

    def all_violations(self) -> Iterator[Violation]:
        for f in self.all_files():
            yield from f.violations

    def files_for_rule(self, rule: Rule) -> Iterator[ParsedTexFile | ParsedBibFile | ParsedRmdFile]:
        # Semantics change: filter by INPUT FORMAT, not file suffix.
        # See rule.formats section above.
        ...
```

**Why `all_tex_like()` matters**: existing rules walk
`doc.tex_files`. If a rule needs to ALSO see raw-LaTeX inside Rmd
prose (which is the default — most rules don't know about Rmd), it
walks `doc.all_tex_like()` instead. Bulk migration is a
search-replace from `doc.tex_files` → `doc.all_tex_like()` in rule
modules that should apply to Rmd prose.

**Invariants**:

| # | Invariant | Enforcer |
|---|---|---|
| P-1 | `all_tex_like()` yields `tex_files` first, then fragments in `rmd_files` order. | `test_all_tex_like_order` |
| P-2 | `ParsedDocument(rmd_files=(rmd,))` with a Rmd that has no prose blocks yields an empty iterator from `all_tex_like()`. | `test_all_tex_like_empty_rmd` |
| P-3 | `files_for_rule(rule)` skips formats not in `rule.formats` (when non-None). | `test_files_for_rule_filter` |

## 4. `ComplianceReport` — new `skipped_rules` field

**Location**: `src/texlint/api.py`.

```python
@dataclass(frozen=True)
class SkippedRule:
    rule_id: str
    reason: str  # e.g., "format 'rmd' not in formats={'tex', 'rnw'}"


@dataclass(frozen=True)
class ComplianceReport:
    tool_version: str
    journal_id: str
    violations: tuple[Violation, ...]
    categories: tuple[CategorySummary, ...]
    compliance_percentage: float | None
    skipped_rules: tuple[SkippedRule, ...] = ()    # NEW, additive
```

**Invariants**:

| # | Invariant | Enforcer |
|---|---|---|
| C-1 | `skipped_rules` contains each rule-id at most once per input format. Duplicates are reduced to the one with the most specific reason. | `test_skipped_rules_unique` |
| C-2 | A rule appearing in `skipped_rules` MUST NOT also appear in `violations` for the same input. | `test_skipped_not_in_violations` |
| C-3 | `CategorySummary.rules_applied` excludes skipped rules. | `test_rules_applied_excludes_skipped` |

## 5. Tokenizer / parser entry-point contracts

Engine-level changes, not new dataclasses, but documented here for
completeness:

### `core/parser.py`

- `strip_rnw_chunks(src: str) -> str` — see contracts/rnw-stripper.md
  for the full contract.
- `parse_rnw_file(path: Path) -> ParsedTexFile` — composes
  `strip_rnw_chunks` with `parse_tex_file`. Returns a `ParsedTexFile`
  whose `path` is the original `.Rnw` file and whose `source` is the
  stripped (but still line-preserving) text.
- `parse_rmd_file(path: Path) -> ParsedRmdFile` — delegates to
  `core/rmd_parser.py`.

### `core/rmd_parser.py`

- `parse_rmd_source(path: Path, src: str) -> ParsedRmdFile` — the
  pure-function form usable in tests without a tempfile.

### `core/engine.py`

- `parse_document(paths: Sequence[Path]) -> ParsedDocument` — new
  engine-level dispatcher. Sorts each path into the appropriate
  parser by extension; assembles the `ParsedDocument` with
  `tex_files`, `bib_files`, and `rmd_files` populated appropriately.
- `run(doc: ParsedDocument, journal_id: str, cfg: ToolConfig) ->
  ComplianceReport` — modified to populate `skipped_rules` when
  `rule.formats` excludes the detected input format. Detection per
  file: each parsed-file object knows its input format via a
  private `_input_format: str` attribute set at parse time.
