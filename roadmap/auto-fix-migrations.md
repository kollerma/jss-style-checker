# Auto-fix migrations — 23 rules with `auto_fixable: true`

The spec-008 auto-fix engine reads a `Fix(start, end, replacement,
description, confidence)` payload off each `Violation`. Two
catalogue rules already emit one (`JSS-CITE-003`, `JSS-NAME-001`);
the 23 below are flagged `auto_fixable: true` in
`specs/003-jss-rule-catalogue/catalogue.yaml` but their rule-side
implementations still ship `fix=None`.

This file is the rule-by-rule migration TODO. Each item, when
shipped, follows the pattern established by `JSS-CITE-003`:

  1. Compute the byte range of the offending token from the
     pylatexenc node (`node.pos` and `node.len`, or the `start()`
     / `end()` of an internal `re.Match`).
  2. Build the canonical replacement string.
  3. Yield the violation with `fix=Fix(start, end, replacement,
     description, confidence="safe")`.
  4. Add a fixture pair under
     `tests/fixtures/auto-fix/<RULE-ID>/{before,after}.tex`.
  5. Extend `tests/unit/journals/jss/rules/test_<rule_module>.py`
     with two tests: payload shape + in-memory application
     equals the after-fixture byte-for-byte.
  6. Extend `tests/integration/test_cli_fix_apply.py` with one
     end-to-end CLI test.

Confidence MUST stay `"safe"` for every migration in this file.
Anything that needs human judgement is not on this list.

Migrations are grouped by structural complexity so a contributor
can pick a batch of similar rules.

## Batch A — single-token wrap / replace (simplest)

Pattern: AST walker has already located the offending token; the
fix is a string substitution at `node.pos` / `node.len` (or
equivalent) with a deterministic canonical form.

- [ ] **JSS-MARKUP-001** — wrap programming-language name in
      `\proglang{...}`. Fix: `start = match.start()`, `end =
      match.end()`, `replacement = f"\\proglang{{{token}}}"`.
- [ ] **JSS-MARKUP-002** — wrap software-package name in `\pkg{...}`.
      Same pattern as MARKUP-001 but with `\pkg{}`.
- [ ] **JSS-NAME-002** — BibTeX publisher / journal canonicalisation
      (e.g. `Springer` → `Springer-Verlag`). Fix: replace the
      `publisher = {...}` or `journal = {...}` string-literal value
      with the canonical form. Operates on `.bib` files.
- [ ] **JSS-HOUSE-001** — insert `,` after `e.g.` / `i.e.` so the
      period isn't treated as end-of-sentence. Fix: insert `,` at
      `match.end() - 1` (one-byte deletion-and-replacement of `.`
      with `.,`). Confidence safe because the regex constrains
      context.
- [ ] **JSS-HOUSE-002** — book-edition rendering: `second
      edition` → `2nd edition`. Fix: replace the matched ordinal
      word with the digit form.
- [ ] **JSS-STRUCT-002** — replace `Acknowledgements` with
      `Acknowledgments`. Fix: single-token spelling swap.

## Batch B — structural shim (medium)

Pattern: extract a plain-text projection of an existing macro's
argument and emit a sibling macro with that projection.

- [ ] **JSS-PRE-003** — when `\title{}` contains markup, emit
      `\Plaintitle{<plain text>}`. Fix: insert
      `\Plaintitle{...}` after the existing `\title{...}` line.
- [ ] **JSS-PRE-007** — same as PRE-003 but for `\author{}` →
      `\Plainauthor{}`.
- [ ] **JSS-PRE-008** — same as PRE-003 but for `\Keywords{}` →
      `\Plainkeywords{}`.
- [ ] **JSS-PRE-006** — `\Plaintitle{}` / `\Plainauthor{}` /
      `\Plainkeywords{}` must be markup-free. Fix: strip markup
      from the existing brace argument; replace the macro's
      content range with the cleaned text.
- [ ] **JSS-MARKUP-004** — `\section[plain-text]{markup}` shim.
      Fix: insert `[plain]` after `\section`.
- [ ] **JSS-STRUCT-005** — `\author{A \and B}` → `\author{A \And
      B}`. Fix: replace `\and` with `\And` (or `\AND`) inside
      the matched `\author{}` block.
- [ ] **JSS-STRUCT-006** — appendix needs a `\newpage` separator
      after `\bibliography{}`. Fix: insert `\newpage\n` at the
      reported position.
- [ ] **JSS-TYPO-001** — figure / table captions end with a
      period. Fix: insert `.` at the end of the caption text
      argument.

## Batch C — math / operator typesetting (judgement-y but bounded)

Pattern: mathematical macros / spacing inside `$...$` or display
math. Bounded because the catalogue describes the canonical form;
implementation needs careful position arithmetic to avoid
nesting / verbatim hazards.

- [ ] **JSS-OPER-001** — `p-value` → `$p$~value`,
      `t-statistic` → `$t$~statistic`, etc. Fix: replace the
      matched token range.
- [ ] **JSS-OPER-002** — transpose: prime / `T` superscript →
      `\top`. Fix: replace the offending superscript with
      `\top`.
- [ ] **JSS-OPER-004** — expectation / variance / covariance /
      probability shortcuts: `\mathbb{E}` → `\E`, etc. Fix:
      one-to-one macro substitution from a small fixed table.
- [ ] **JSS-XREF-002** — `(\ref{eq:foo})` → `Equation~\ref{eq:foo}`.
      Fix: replace the parenthesised reference span.

## Batch D — code-style / spacing rules (most invasive)

Pattern: edits inside `\code{}` / `verbatim` blocks or R code
chunks. Non-trivial because the rule's match domain must agree
with the fix domain (don't touch the surrounding `\code{}`
delimiters). Confidence "safe" requires a self-applying
re-check.

- [ ] **JSS-CODE-002** — R `library(...)` / `data(...)` first
      arg quoted: `library(MASS)` → `library("MASS")`. Fix:
      wrap the bareword first argument in double quotes.
- [ ] **JSS-CODE-003** — spaces around operators / after commas
      in code samples. Fix: insert spaces; this is multi-edit
      territory and may require multiple `Fix` payloads or a
      single fix spanning the line.
- [ ] **JSS-OPER-003** — display equations: drop blank lines
      immediately before / after. Fix: replace blank-line bytes
      with `%\n` to suppress paragraph break.

## Batch E — abbreviations + house style (tail)

- [ ] **JSS-ABBR-001** — abbreviations uppercased without
      periods or formatting. Fix: replace `U.S.A.` with `USA`,
      `Ph.D` with `PhD`, etc.
- [ ] **JSS-HOUSE-003** — preamble `\usepackage{graphicx}` /
      `\usepackage{xcolor}` etc. when `jss.cls` already
      provides them. Fix: delete the offending `\usepackage{}`
      line entirely.

## Tracking

When a migration ships:

1. Tick the box here.
2. Add it to `roadmap/follow-ups.md` under feature 008 (the
   parent follow-up is already shipped; sub-rules are
   incremental).
3. The catalogue's `auto_fixable` flag stays `true` — rule
   metadata never changes; the runtime fix payload appearing
   on `Violation.fix` is the observable bit.

## Out-of-scope

The 33 catalogue rules NOT flagged `auto_fixable: true`
(JSS-PRE-001, JSS-PRE-002, JSS-PRE-004, JSS-PRE-005,
JSS-STRUCT-001, JSS-STRUCT-003, JSS-STRUCT-004, JSS-STRUCT-007,
JSS-STRUCT-008, JSS-MARKUP-003, JSS-MARKUP-005..009,
JSS-CITE-002, JSS-CITE-004, JSS-CITE-005, JSS-CITE-006,
JSS-CITE-007, JSS-REFS-001..007, JSS-BIBTEX-001..002,
JSS-NAME-002 (already in batch A), JSS-CAP-001..003,
JSS-CODE-001, JSS-CODE-004, JSS-WIDTH-001, JSS-XREF-001,
JSS-XREF-003) intentionally have no deterministic fix in the
catalogue. They require human judgement (e.g.
`JSS-WIDTH-001` line-width violations need a manual rewrap;
`JSS-CITE-002` needs the author to pick a citation; etc.).
Don't touch this list.
