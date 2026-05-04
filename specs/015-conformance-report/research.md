# Research: Conformance Report

**Phase**: 0
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. PDF rendering: WeasyPrint vs. alternatives

**Decision**: WeasyPrint, gated behind the `[pdf]` extra.

**Rationale**:
- WeasyPrint is the most widely-supported pure-CSS-to-PDF
  toolchain in the Python ecosystem. Its CSS coverage is
  good enough for a one-page report.
- Gating behind `[pdf]` keeps cairo/pango out of the core
  install (Clarifications §1).
- The HTML/CSS template approach lets us share styling
  between the HTML-format and PDF-format outputs.

**Alternatives considered**:
- `reportlab`: rejected — imperative API, no HTML/CSS
  reuse with the HTML format.
- `wkhtmltopdf`: rejected — abandoned upstream, depends on
  a Qt webkit fork.
- LaTeX → PDF: rejected — would re-introduce LaTeX as a
  build dep, which the linter is supposed to obviate.
- Markdown → pandoc → PDF: rejected — pandoc is a
  separate binary install; not Python.

---

## 2. Markdown as canonical format

**Decision**: Markdown is the canonical format. HTML and
PDF are renderings derived from the same template logic.

**Rationale**:
- Markdown is the smallest surface; editors who don't have
  WeasyPrint installed can still produce + share the
  report.
- A markdown report is also pleasant to read in plain
  text; many editors will paste it directly into a
  decision-letter draft.
- HTML / PDF gain styling but no information.

**Alternatives considered**:
- HTML canonical: rejected — markdown is more portable.
- PDF canonical: rejected — opaque to text-pipeline
  consumers (grep, diff, version-control review).

---

## 3. Score formula

**Decision**: `score = 100 * (rules_with_zero_violations /
total_active_rules)` (unweighted, integer rounding).

**Rationale**:
- Per Clarifications §2: weighted formulas are
  editorially opinionated.
- Integer rounding gives a single number for the decision
  letter (`87 %` not `86.21 %`).
- `total_active_rules` excludes ignored rules (so
  ignoring a rule does not lower the score) and tool-side
  rules (parse / internal — they are tool-execution
  events, not style judgments).

**Alternatives considered**:
- Severity-weighted (e.g., 3:1:1 for error/warning/info):
  rejected per Clarifications §2.
- Rule-precision-weighted: rejected — would couple the
  visible score to private precision data, surprising
  authors.

---

## 4. Fix-me ordering: precision tiebreaker

**Decision**: Within each severity tier, sort by descending
corpus precision. Falls back to ascending rule id when the
DB is missing.

**Rationale**:
- The fix-me list is most useful when the highest-
  precision items are at the top: the editor's first
  fixes are also the ones most likely to be true
  positives.
- Lexicographic fall-back is deterministic and documented;
  the report's footer notes which fall-back applied.

**Alternatives considered**:
- Sort by violation count: rejected — would surface a
  noisy low-precision rule above a rare high-precision
  rule, defeating the triage value.
- Random tiebreaker: rejected — non-deterministic.

---

## 5. Top-5 most-violated block

**Decision**: Top 5 by violation count descending; tiebreak
on rule id ascending. Each entry shows ONE example
excerpt: file path, line, first 80 chars of the
triggering source.

**Rationale**:
- Five is a screen's worth; ten dilutes attention.
- One example per rule shows the reader what the
  violation looks like without padding the report.
- 80 chars matches typical terminal width.

**Alternatives considered**:
- Top 10: rejected — pushes the fix-me list off the page
  for typical violation counts.
- Multiple examples per rule: rejected — bloats the
  report.

---

## 6. Manuscript metadata extraction

**Decision**: Extract `\title{...}` and `\author{...}` /
`\Plainauthor{...}` from the parsed document's preamble
via the existing pylatexenc AST. Honour `--title` /
`--author` CLI overrides when set.

**Rationale**:
- The preamble already carries the data; reusing it is
  no extra parse cost.
- Overrides cover the case where the editor wants a
  specific framing (anonymised author for double-blind
  review, e.g.).

**Alternatives considered**:
- Override-only (no extraction): rejected — would force
  editors to type the title for every report.
- Extract from filename: rejected — the filename is
  rarely the title.

---

## 7. Reproducibility footer

**Decision**: The report's footer cites
`linter-version: <version>` and
`commit-hash: <hash or "unavailable">`. The hash is
computed via `git rev-parse HEAD` in the manuscript's
parent directory; on failure (not a git repo, git not
installed), the line reads `commit-hash: unavailable`.

**Rationale**:
- Reproducibility is the editor-side contract: "if I run
  this same linter on this same commit, I get the same
  report".
- Best-effort detection avoids a hard requirement on
  git, which not every author uses.

**Alternatives considered**:
- Require git: rejected — too hostile.
- Skip the footer entirely: rejected — losing the
  reproduction note removes the audit trail.

---

## 8. Template engine choice

**Decision**: Jinja2 (already a dep). Three templates:
`conformance.md.j2`, `conformance.html.j2`,
`conformance.pdf.j2`. The PDF template is HTML with
print-CSS for one-page layout; WeasyPrint converts.

**Rationale**:
- Jinja2 is already used by `output/html_output.py` from
  spec 001; reusing it is zero new dep.
- Three templates (vs. one shared template with format
  branches) keeps each format's logic readable.

**Alternatives considered**:
- One template with `{% if fmt == "md" %}` everywhere:
  rejected — readability collapses.
- Hand-written string formatting in Python: rejected —
  Constitution §X allows the existing Jinja2 dep.

---

## Summary

All eight decisions follow from spec Clarifications and
Constitution §I, §III, §X. No remaining `NEEDS
CLARIFICATION`. Ready for Phase 1.
