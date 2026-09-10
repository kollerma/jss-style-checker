# Data Model: Release 1.2.0 — first-time-user gaps

**Plan**: [plan.md](plan.md) (rev 4)
**Contracts**: [contracts/](contracts/)

Every shape below exists in both engines (Constitution §XIII): the Python
reference dataclass in `src/texlint/api.py` (or the module named) and its
Rust mirror in `rust/jsslint-core/src/report.rs` (or the module named).
Field order in the Python dataclass is the canonical order; Rust structs
carry the same fields with the same names.

## 1. Suppression hook (plan §5.2)

```python
# src/texlint/api.py
Suppressor = Callable[[Violation], bool]      # True → drop this finding

# src/texlint/core/engine.py
def run(config: ToolConfig, target: ParsedDocument, journal: JournalRuleModule,
        *, suppress: Suppressor | None = None) -> ComplianceReport: ...
```

```rust
// rust/jsslint-core/src/engine.rs
pub trait Suppressor { fn suppress(&mut self, v: &Violation) -> bool; }
pub fn run(config: &ToolConfig, doc: &ParsedDocument) -> ComplianceReport;          // unchanged
pub fn run_with(config: &ToolConfig, doc: &ParsedDocument,
                project_extra: Option<(Vec<Violation>, Vec<Violation>)>,
                extra: Option<&mut dyn Suppressor>) -> ComplianceReport;
```

Order inside the per-rule loop, identical in both engines:

1. `rule_violations.sort(key=Violation.sort_key)`
2. drop inline-suppressed findings (`suppress.is_suppressed`)
3. drop findings for which `suppress(v)` returns `True`
4. severity remap, then applied/passed bookkeeping

Inline first, so an inline-ignored finding never consumes a baseline
count. `JSS-PARSE-000` findings are collected outside the loop and bypass
both steps.

### 1.1 `ParsedTexFile.line_offset`

```python
@dataclass(frozen=True)
class ParsedTexFile:
    ...
    line_offset: int = 0     # 0 for .tex/.Rnw; prose.line - 1 for .Rmd fragments
```

`suppress.build_index` adds `line_offset` to every directive line so
`.Rmd` fragments (whose `source` is fragment-relative) map to
file-authoritative line numbers. `directive_lines` splits on `"\n"` only.

## 2. Baseline (plan §5.3)

```python
# src/texlint/core/baseline.py — pure, no I/O
Key = tuple[str, str, str, str]                     # (rule_id, path, message, suggestion)

@dataclass(frozen=True)
class BaselineEntry:
    rule_id: str
    path: str            # posix, relative to the baseline file's directory
    message: str
    suggestion: str      # "" when the violation carries none
    count: int           # ≥ 1

@dataclass(frozen=True)
class BaselineDocument:
    schema_version: int                  # == 1
    tool_version: str
    ruleset_version: str | None
    journal: str
    entries: tuple[BaselineEntry, ...]   # sorted by (path, rule_id, message, suggestion)

@dataclass(frozen=True)
class BaselineSummary:
    path: str                            # as given on the command line / TOML
    matched: int
    stale: int                           # unmatched entries whose rule ran
    unevaluated: int                     # unmatched entries whose rule did not run
    ruleset_version: str | None          # stamped in the file

class BaselineError(ValueError): ...

def parse(text: str) -> BaselineDocument
def build(violations: Iterable[Violation], *, path_map: Mapping[str, str],
          tool_version: str, ruleset_version: str | None, journal: str) -> BaselineDocument
def dumps(doc: BaselineDocument) -> str      # json.dumps(indent=2, sort_keys=True) + "\n"

class BaselineMatcher:                       # the Suppressor
    def __init__(self, doc: BaselineDocument, path_map: Mapping[str, str]) -> None
    def __call__(self, v: Violation) -> bool  # decrement remaining[key] if > 0
    def summary(self, path: str, applied_rule_ids: AbstractSet[str]) -> BaselineSummary
```

Rust: `baseline.rs` with `BaselineEntry`, `BaselineDocument`,
`BaselineSummary`, `parse(&str) -> Result<BaselineDocument, String>`,
`build(..)`, `to_json(&self) -> String` (through
`json_output::write_value` so bytes equal CPython's `ensure_ascii=True`
output), and `BaselineMatcher { remaining: HashMap<(String,String,String,String), u32>,
matched: u32, path_map: HashMap<String,String> }` implementing `Suppressor`.

`path_map` is `{str(parsed_file.path): relative_posix}` built by the CLI
from `document.all_files()`; a file absent from the map is unsuppressible.

### 2.1 Report and config additions

```python
@dataclass(frozen=True)
class ComplianceReport:
    ...
    baseline: BaselineSummary | None = None       # filled by the CLI after run()

@dataclass(frozen=True)
class ToolConfig:
    ...
    baseline: Path | None = None                  # TOML key `baseline`
    color: Literal["auto", "always", "never"] = "auto"   # TOML key `color`
```

Rust: `ComplianceReport.baseline: Option<BaselineSummary>`,
`ToolConfig.baseline: Option<PathBuf>`, `ToolConfig.color: ColorChoice`
(`Auto | Always | Never`); `KNOWN_FIELDS` and `RawOverrides` gain both
keys, and the four `RawOverrides` struct literals (cli, wasm, py, R) are
updated.

## 3. Journal metadata (plan §7.2)

```python
@dataclass(frozen=True)
class RecallStat:
    tp: int
    fn: int
    def state(self, min_plants: int) -> Literal["measured", "limited", "unmeasured"]
    def percent(self) -> int | None      # only when state == "measured"
    def label(self, min_plants: int) -> str   # "81%" | "limited (n=4)" | "unmeasured"

@dataclass(frozen=True)
class RecallRun:
    run_timestamp: str
    corpus_hash: str
    min_plants: int
    tp: int
    fn: int

@dataclass(frozen=True)
class CoverageDirective:
    id: str                              # CLS-…, TEX-…, SG-…, AI-…
    source: str                          # jss_cls | article_tex | style_guide | author_instructions
    section: str                         # index.json key, anchor, or "internal"
    provision: str
    status: Literal["checked", "partial", "not_checked", "out_of_scope"]
    rules: tuple[str, ...]
    reason: str

@dataclass(frozen=True)
class RuleSetInfo:
    version: str | None                  # "YYYY-MM-DD"
    fingerprint: str | None              # "sha256:…"
    guide_source: str | None             # "jss.cls 3.3 (2021-05-23)"
    recall: RecallRun | None

@dataclass(frozen=True)
class JournalMetadata:
    rule_set: RuleSetInfo = RuleSetInfo(None, None, None, None)
    recall_by_rule: Mapping[str, RecallStat] = field(default_factory=dict)
    coverage: tuple[CoverageDirective, ...] = ()

class JournalRuleModule(ABC):
    ...
    def metadata(self) -> JournalMetadata:       # non-abstract; default = empty
        return JournalMetadata()
```

`engine.run` copies metadata onto the report:

```python
@dataclass(frozen=True)
class CategorySummary:
    ...
    recall: RecallStat | None = None     # pooled tp/fn over the category's rules

@dataclass(frozen=True)
class ComplianceReport:
    ...
    rule_set: RuleSetInfo
    coverage: tuple[CoverageDirective, ...] | None   # None when the journal has no data
```

Renderers read the report only; no renderer imports
`texlint.journals.jss` for these values (§IV). Rust mirrors all of the
above in `report.rs`; `catalogue.rs` exposes `recall(rule_id)`,
`coverage()`, `provenance()` from the build-time statics.

### 3.1 Integer recall arithmetic

```
n = tp + fn
state   = "unmeasured" if n == 0 else "limited" if n < min_plants else "measured"
percent = (200 * tp + n) // (2 * n)          # integer half-up; only when measured
```

No floating point anywhere in the classification or the rendered
percentages (Python `round` is banker's, Rust `f64::round` is half-away;
integer division sidesteps both). Category recall pools `tp`/`fn` over
the category's rule ids and applies the same formula. The aggregate in
`rule_set.recall` uses the same formula over all rules
(1587 / 1967 → 81).

## 4. Generated and curated data files (plan §4, §7.1)

All live in `specs/003-jss-rule-catalogue/` and are vendored to
`rust/jsslint-core/specs/…` and `r/jsslintr/src/specs/…` except
`messages.json` (Python-only).

### 4.1 `catalogue.yaml` — new top-level keys

| Key | Type | Notes |
|---|---|---|
| `ruleset_version` | `YYYY-MM-DD` | bumped whenever `ruleset_fingerprint` changes; ≥ `source_vendored_at`, ≤ today |
| `ruleset_fingerprint` | `sha256:<hex>` | over the canonical JSON of §4.4 |
| `guide_edition` | string | `"jss.cls 3.3"`; codegen composes `guide_source = f"{guide_edition} ({source_vendored_at})"` |

### 4.2 `recall.json` (generated by `tools/generate_recall_snapshot.py`)

```json
{
  "corpus_hash": "70951d5371df0734",
  "generated_by": "tools/generate_recall_snapshot.py",
  "min_plants": 10,
  "run_timestamp": "2026-07-19T10:30:02Z",
  "rules": {"JSS-ABBR-001": {"fn": 0, "tp": 4}, "…": {"fn": 0, "tp": 0}}
}
```

`json.dumps(indent=2, sort_keys=True)`; only active catalogue rules;
rules absent from the run have no entry (→ unmeasured). `eval/badge.py`
reads `run_timestamp` and sums `tp`/`fn` from this file.

### 4.3 `guide-coverage.yaml` (hand-curated)

Schema in [contracts/coverage-file.md](contracts/coverage-file.md). Shape:

```yaml
version: 1
sources:
  jss_cls:             {file: docs/jss-template/jss.cls, edition: "3.3", date: "2021-05-23"}
  article_tex:         {file: docs/jss-template/article.tex, date: "2021-12-10"}
  style_guide:         {url: "https://www.jstatsoft.org/style", fetched: "2026-04-23"}
  author_instructions: {url: "https://www.jstatsoft.org/authors", fetched: "2026-04-23"}
directives:
  - id: SG-020
    source: style_guide
    section: "#how-should-abbrevations-be-formatted"
    provision: "Introduce all abbreviations with expansion at first use"
    status: not_checked
    rules: []
    reason: "first-use tracking is implementation-brittle; JSS-ABBR-002 retired 2026-04-23"
```

### 4.4 `messages.json` (generated by `tools/generate_message_snapshot.py`)

```json
{
  "JSS-CAP-002": [["Section titles are in sentence style …", "Use sentence style in 'Robust Methods For Mixed Models'."]],
  "JSS-REFS-003": [["BibTeX entries include a doi field …", "Add a doi field to entry 'koller2023' if one is available."]]
}
```

Rule id → sorted unique `[message, suggestion]` pairs the Python
reference emits on `tests/fixtures/violations/**/*-bad.*` (plus the
resolver fixtures for `JSS-PROJECT-001/002`). Generated **after** item S.

The fingerprint input is the canonical JSON (`sort_keys`, separators
`(",", ":")`, `ensure_ascii=False`) of:

```json
{"rules": [{"rule_id", "category", "severity", "description", "guide_section", "confidence", "auto_fixable"}, …],
 "messages": <messages.json contents>}
```

with `guide_section` defaulting to `""` and `confidence` to `"high"`,
rules sorted by id. Rust never recomputes it; it embeds the stored string.

## 5. Determinism notes

- Baseline consumption happens in `Violation.sort_key` order within each
  rule's list, so which occurrences of a same-shape key are "new" is the
  same in both engines.
- The baseline file carries no timestamp; `--update-baseline` output is
  byte-identical across engines and across runs on identical input.
- `recall.json`, `messages.json`, and the fingerprint are regenerated
  with `--check` freshness tests, so a stale committed copy fails CI.
- Coverage counts and directive order in every renderer follow the
  YAML's `directives` order after a stable sort by `(status, id)`.
