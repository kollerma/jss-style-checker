# Phase 0 Research — Rnw / Rmd Manuscript Support

Consolidates the design decisions the plan takes from the
`/speckit.plan` input's implementation template and from the three
`/speckit.clarify` answers encoded into `spec.md`.

## 1. Rnw chunk stripping: line-preserving regex substitution

**Decision**: A single regex substitution preserves source line
numbers exactly. The stripper replaces each matched chunk with `"\n"
*` the chunk's newline count, then feeds the result to the existing
`parse_tex_file`. No new parser.

```python
_RNW_CHUNK = re.compile(
    r"<<[^>]*>>=\n.*?^@\s*$",
    re.DOTALL | re.MULTILINE,
)

def strip_rnw_chunks(src: str) -> str:
    def _blank(m: re.Match) -> str:
        return "\n" * m.group(0).count("\n")
    return _RNW_CHUNK.sub(_blank, src)
```

**Invariant**: `strip_rnw_chunks(src).count("\n") == src.count("\n")`
for all inputs. Test-enforced.

**Inline `\Sexpr{...}` handling**: a second regex stripping
single-line `\Sexpr{…}` to equivalent-length whitespace so inline
Sexpr-generated values don't false-positive. No newlines to preserve
for inline form.

```python
_RNW_SEXPR = re.compile(r"\\Sexpr\{[^{}]*\}")
# Replace with spaces of equal length so columns are preserved.
```

**Rationale**:
- Constitution §X small surface: no second AST, no parser dependency.
  The stripper is 8 lines.
- Constitution §II AST-first: the stripper is a byte-level pre-pass
  (Sweave chunks are not expressible in pylatexenc's AST); everything
  downstream remains AST-first.
- Line-preserving substitution keeps pylatexenc's line numbers
  source-authoritative, satisfying FR-003.

**Alternatives considered**:
- **Full Sweave parser**: parse chunk options, body, output captures
  into a structured node. Rejected — adds surface with no observable
  benefit for the lint step (we only need to silence the chunk body).
- **Remove chunks entirely (not whitespace)**: breaks FR-003 line
  numbers. Rejected.
- **Strip to `%` comment lines**: pylatexenc would see comments where
  code used to be; comment-aware rules could false-positive. Rejected.

**Consequence**: `core/parser.py` grows one helper
(`strip_rnw_chunks`) and one entry point (`parse_rnw_file` which
composes `strip_rnw_chunks` + `parse_tex_file`).

## 2. Rmd parser: hand-rolled state-machine tokenizer

**Decision**: hand-roll a small line-based state machine in
`core/rmd_parser.py`. **Do not** depend on `markdown-it-py` or
`mistune`.

**Spec drift**: `/speckit.clarify` Q1 recorded `markdown-it-py` as the
Markdown parser choice. The `/speckit.plan` input supersedes this:
hand-roll instead. Rationale:

- The Rmd surface we care about is shallow: frontmatter → (heading |
  prose | fenced-code)*. Every Markdown feature beyond these four
  token kinds is either (a) rendered prose from the author's
  perspective (italics, bold, links) that can be linted as-is, or
  (b) irrelevant to style rules (list markers, image alts).
- `markdown-it-py` ships a CommonMark AST we'd immediately flatten
  back to our four-token model. The full AST is surface we'd never
  benefit from.
- Constitution §X small surface: a ~50-line state machine with ~12
  local unit tests is cheaper to review and maintain than a
  third-party parser dep with version-compatibility churn.
- Spec clarification: updated in `spec.md` Clarifications section to
  reflect the planning decision.

**Tokenizer state machine**:

```text
state = START
for each line (1-based index):
  START:
    - line == "---": state = FRONTMATTER; buffer=[]
    - else: state = BODY  (reprocess line)

  FRONTMATTER:
    - line == "---": run yaml.safe_load(buffer); state = BODY
    - else: buffer.append(line)

  BODY:
    - re.match(r"^```(\{.*\})?$", line): state = FENCE; open_line = i
    - re.match(r"^(#+)\s+(.+)$", line): yield Heading(level, text, line=i)
    - else: accumulate prose; flush on blank line to yield Prose(text, line=start_i)

  FENCE:
    - re.match(r"^```\s*$", line): yield CodeBlock(body, line=open_line); state = BODY
    - else: fence_body.append(line)
```

**Line numbers**: every token carries its 1-based start line in the
source. The `Prose` token additionally records the number of lines so
embedded raw-LaTeX islands can be offset correctly.

**Inline R code `` `r expr` `` handling**: post-tokenization pass
over prose blocks only. `re.sub(r"`r\s[^`]*`", lambda m: " " *
len(m.group(0)), prose)` — same-width whitespace so columns are
preserved. Does not touch code-block bodies (rules don't look at
those anyway).

**YAML frontmatter**: `yaml.safe_load(buffer_text)`. On
`yaml.YAMLError`, emit a `JSS-PARSE-000` violation and leave
`yaml_frontmatter = {}`. The tokenizer continues past the frontmatter
sentinel regardless, so a broken YAML block doesn't abort parsing.

**Rationale**:
- Zero new deps (pyyaml is already the frontmatter parser).
- Line numbers are trivially preserved because the tokenizer is
  line-based from the start.
- Malformed inputs (unterminated fence, unterminated frontmatter,
  unbalanced `` ``` `` counts) degrade gracefully to `JSS-PARSE-000`
  with a line number.

**Alternatives considered**:
- **`markdown-it-py`**: the spec's Clarifications Q1 choice.
  Superseded by the plan input — see spec drift discussion above.
- **`mistune`**: smaller / faster than markdown-it-py but same
  objection (CommonMark AST is surface we flatten).
- **`commonmark`**: older, maintenance-thin, same objection.
- **Pandoc shell-out**: adds a non-Python system dep; huge overkill
  for our scope.

## 3. Raw-LaTeX island handling in Rmd prose

**Decision**: for each `Prose` token, run `parse_tex_source` on the
block text and attach the resulting `ParsedTexFile` to
`ParsedRmdFile.latex_fragments` with a synthetic path like
`"<rmd-path>:block@<start_line>"`. Rules that traverse
`doc.tex_files` also traverse `latex_fragments` via the new
`doc.all_tex_like()` helper.

**Rationale**:
- Spec Clarifications Q3: inline LaTeX in Rmd prose is parsed as
  raw-LaTeX islands. This is the implementation of that decision.
- Existing `.tex` rules work unchanged: they walk a
  `ParsedTexFile` and yield `Violation`s with the tex-file's `path`
  and `walker.pos_to_lineno_colno`.
- Line numbers: the prose block's starting line becomes the island's
  base offset; pylatexenc's line numbers are relative to the island
  string, so the engine adds `start_line - 1` when translating to
  source line.

**Alternatives considered**:
- **Detect inline LaTeX inside the tokenizer and emit dedicated
  tokens**: splits the surface between "tex" and "rmd" parsers. The
  chosen approach keeps everything above the tex parser boundary in
  `core/rmd_parser.py` and re-uses `parse_tex_source` unchanged.
  Rejected.
- **Pre-process the whole Rmd to a pseudo-tex and parse as tex**:
  code fences and frontmatter would need to be stripped to
  whitespace, which conflates them with Rnw chunk-stripping. Rejected
  — the Rmd parser's segment model is more precise.

## 4. Rule-format filter semantics

**Decision**: `Rule.formats: frozenset[str] | None` semantics
**change** from Step 1's file-suffix filter (`{".tex", ".bib"}`) to an
input-format filter (`{"tex", "rnw", "rmd"}`). `None` continues to
mean "applies to all inputs".

**Rationale**:
- Step 1 defined `formats` as file-suffix filter in
  `data-model.md` and `files_for_rule` iterates
  `doc.all_files()` filtering by `f.path.suffix`. This
  breaks for Rmd inputs: the file suffix is `.Rmd`, but the rule
  should apply to the tex-like content inside.
- The new semantics is "which input-format's parsed view does this
  rule apply to". For tex rules (which walk `doc.tex_files`), `"tex"`
  / `"rnw"` both produce a `ParsedTexFile`, so a rule with
  `formats={"tex", "rnw"}` applies to both. Rmd prose raw-LaTeX
  islands are `ParsedTexFile` under the hood but their enclosing file
  is `.Rmd` — `"rmd"` is the format tag.
- `Rule.formats=None` (the default for 50 of 58 spec-004 rules) keeps
  working: the rule applies to every input.

**Migration**:
- Spec 004 rules: all currently set `formats=None`. No migration
  except the preamble category (8 rules) which gains
  `formats=frozenset({"tex", "rnw"})`.
- BibTeX-only rules (`JSS-BIBTEX-001..004`,
  `JSS-REFS-001..007`, `JSS-NAME-002`, `JSS-HOUSE-002`): currently
  `formats=None`. They iterate `doc.bib_files`; Rmd input has a
  sibling `.bib` or doesn't (FR-012 warns on the missing case). Keep
  `formats=None`; whether they find entries is a data question, not
  a format-filter question.

**Alternatives considered**:
- **Rule.input_formats (new field, keep formats as suffix filter)**:
  two overlapping filters would confuse contributors. Rejected —
  extend the existing field in place.
- **Auto-derive formats from the rule's category**: too clever; the
  preamble→tex/rnw mapping is the only current case, and
  explicitness beats inference.

**Consequence**: `data-model.md` §1 documents the semantics change;
`contracts/rule-format-filter.md` pins the skipped-rules payload
shape.

## 5. Skipped-rule reporting

**Decision**: `ComplianceReport.skipped_rules:
tuple[SkippedRule, ...]` where `SkippedRule` is a small frozen
dataclass with `rule_id: str` and `reason: str`. Populated inside
`engine.run` whenever `rule.formats is not None and input_format not
in rule.formats`.

`--verbose` terminal output renders a "Skipped rules" section after
the violations table; JSON / HTML outputs include the list in a
dedicated top-level key. Default (non-verbose) terminal output is
unchanged (FR-009).

**Rationale**:
- Contributors need to tell "rule passed" apart from "rule not
  applied" (FR-008). The existing `CategorySummary.rules_applied`
  count already encodes this at the category level; exposing per-rule
  skipping is the drill-down.
- Output-format back-compat: the JSON field is additive; older
  consumers that don't look for `skipped_rules` see no difference
  (Assumption in spec).

**Alternatives considered**:
- **Inline skipped rules as a new severity tier in `Violation`**:
  couples skip reporting with violation reporting. Rejected — a skip
  is not a violation.
- **Drop skip reporting, document that "missing rule id in output =
  not applied"**: ambiguity between "rule passed" and "rule didn't
  run". Rejected.

## 6. Engine dispatch by file extension

**Decision**: `parse_document(paths: Sequence[Path]) →
ParsedDocument` dispatches each path by extension:

```python
_PARSERS: Mapping[str, Callable[[Path], Any]] = {
    ".tex": parse_tex_file,
    ".rnw": parse_rnw_file,
    ".rmd": parse_rmd_file,
    ".bib": parse_bib_file,
}
```

Unknown extensions → exit 2 with a clear error message (matches
spec 001's existing `_unsupported_suffix_exits_two` behaviour).
Dispatch is case-insensitive (`.Rnw` and `.RMD` are accepted per
CLI-user convention).

**Rationale**:
- Symmetric with spec 001's existing `parse_tex_file` /
  `parse_bib_file` pattern.
- Unknown-extension error preserves existing CLI exit-code contract
  (`2` = invocation error).

## 7. Corpus expansion (spec Q4 → option B)

**Decision**: add a small real CRAN-vignette batch via the existing
`eval-jss corpus fetch` manifest mechanism (spec 002):

- 3–5 `.Rnw` vignette rows (target packages favouring Sweave-classical
  style: e.g., `lme4`, `zoo`, `quantreg`).
- 2–3 `.Rmd` vignette rows (target packages favouring knitr-style:
  e.g., `ggplot2`, `brms` if available via CRAN vs the JSS galley
  mentioned in spec 004's summary).

Each row pinned by SHA256 at fetch time. The manifest schema from
spec 002 handles this without changes — the extension is just more
rows, not new columns.

**`eval-jss report` per-format slicing**: new `--by-format` flag that
partitions the violation set by `papers.path` suffix
(`.tex` | `.Rnw` | `.Rmd`) and emits a per-format precision row.
Default (no flag) behaviour is unchanged — the combined number is the
authoritative single-rule figure, the per-format breakdown is
drill-down. Isolates the `.tex` baseline from new-format numbers
(FR-016 / SC-006).

**Alternatives considered**:
- **Synthetic-only** (option A from clarify Q4): ships faster but
  leaves every rule at NOT MEASURED on `.Rnw` / `.Rmd`. Rejected —
  the feature's value is defeated without at least some real-paper
  precision signal.
- **Parallel-spec for corpus** (option C): keeps spec 005 scope tight
  but delays real-world validation to a follow-up. Rejected —
  corpus is cheap enough to bundle now.

**Consequence**: `tasks.md` will include a Phase 0 task "curate 5–8
CRAN vignette candidates and verify reachability" before any
manifest-row commits.

## 8. Agent-context updates

**Decision**: `CLAUDE.md` plan reference (between `<!-- SPECKIT START
-->` / `<!-- SPECKIT END -->` markers) is updated to point at this
plan file. No other doc changes in Phase 1; `quickstart.md` is the
authoritative contributor onboarding doc for this step.

## Summary of drift reconciliations

1. **Markdown parser choice**: spec Q1 said `markdown-it-py`; plan
   input supersedes with hand-rolled state machine. Both Clarifications
   Q1 record and spec Assumptions were updated to reflect the planning
   decision.

No outstanding `NEEDS CLARIFICATION` items at Phase 0 exit.
