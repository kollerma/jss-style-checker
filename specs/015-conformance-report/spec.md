# Feature Specification: One-page Editor Conformance Report

**Feature Branch**: `015-conformance-report`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Add `jss-lint report PATH [--format md|pdf|html] [--out FILE]`. The output is a one-page summary containing: manuscript metadata (title, author, file count), overall conformance score (% of rules passing on this manuscript), error/warning/info counts, top-five most violated rules with one example each (linked to the JSS guide via spec 007), and a numbered \"fix me first\" list (errors before warnings, sorted by rule precision). Markdown is the canonical format; PDF rendered via WeasyPrint; HTML via the existing Jinja2 templates. Designed to be attached to an editorial decision letter."

## Clarifications

### Session 2026-05-03

- Q: Is WeasyPrint an acceptable runtime dep (it pulls in cairo) or do we offer PDF only as an extra `[pdf]`? → A: Optional extra `[pdf]`. WeasyPrint pulls in cairo / pango / GLib, which is a substantial install footprint for users who only want the markdown surface. The extra gate (`pip install "jss-lint[pdf]"`) keeps the core install lean. Mirrors the spec-011 `[lsp]` pattern.
- Q: Does the score weight errors vs warnings (e.g., 3:1) or count rules-passing/rules-total unweighted? → A: Unweighted: `100 * (rules_with_zero_violations / total_active_rules)`. The score answers "how many rules is this manuscript clean against?" not "how serious are the issues?". Severity is surfaced in the per-tier counts and the fix-me ordering. A weighted formula is editorially opinionated; unweighted is the JSS-authority-neutral choice.
- Q: Do we include manuscript-level metadata only when the preamble exposes `\title{}` / `\Plainauthor{}`, or do we accept CLI overrides? → A: Both. Extract from the preamble when present; honour `--title TEXT` / `--author TEXT` overrides when the manuscript lacks the macros (or when the editor wants a specific framing for the letter).
- Q: Is the markdown output stable across runs (deterministic section order)? → A: Yes. Section order is fixed (six sections per FR-003). Within sections: top-5 ordered by `(count desc, rule_id asc)`; fix-me-first ordered by `(severity asc, precision desc, rule_id asc)`. The only non-deterministic value is the run-date line; tests compare body bytes minus that single line.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Editor attaches the report to a decision letter (Priority: P1)

A JSS desk editor reviews a submission. They run `jss-lint report
manuscript.tex --out review.pdf`. The PDF is a one-page summary
they attach to the decision letter: title, author, conformance
score, top-five rules, and a numbered fix-me-first list. The
author receives the letter and knows exactly what to address.

**Why this priority**: P1 because the conformance report is the
editor-facing surface for the entire tool. Without it, editors
have to read raw lint output and translate it into prose
themselves.

**Independent Test**: Run `jss-lint report fixture.tex --format md
--out /tmp/r.md`; the file exists, contains all six required
sections, and matches a stored golden.

**Acceptance Scenarios**:

1. **Given** a fixture with known violations, **When** `jss-lint
   report --format md` runs, **Then** stdout (or the `--out`
   file) contains: title section with manuscript metadata,
   conformance score, severity counts, top-5 rules block,
   numbered fix-me-first list, and a footer with the linter
   version + run date.
2. **Given** the same fixture, **When** `--format pdf --out
   review.pdf` runs, **Then** the PDF is one page (US Letter or
   A4), opens in standard readers, and contains the same six
   sections.
3. **Given** the same fixture, **When** `--format html --out
   review.html` runs, **Then** the HTML renders the same six
   sections via the existing Jinja2 templating layer.

---

### User Story 2 - Conformance score reflects rules passing (Priority: P1)

The score reads `87 % conformant (50 of 58 rules pass on this
manuscript)`. The editor immediately knows the manuscript is
mostly clean but has 8 rules to address.

**Why this priority**: P1 because the score is the headline
number the editor cites in the decision letter. Without it, the
report is just a list.

**Independent Test**: A fixture with 8 active rules, 6 of which
have zero violations, produces a score of `75 %`.

**Acceptance Scenarios**:

1. **Given** a fixture where 50 of 58 catalogue rules have zero
   violations, **When** the report renders, **Then** the score
   line reads exactly `87 % (50 of 58 rules pass)`.
2. **Given** an empty manuscript (zero violations), **When** the
   report renders, **Then** the score is `100 %`.
3. **Given** a manuscript with `--ignore-rules` set, **When** the
   report renders, **Then** ignored rules are excluded from the
   denominator (so a 50-of-50 result yields `100 %` even if 8
   rules are ignored).

---

### User Story 3 - Fix-me-first list is prioritised by precision (Priority: P1)

The numbered list orders fixes by rule precision: errors first,
then warnings, sorted within each tier by descending corpus
precision (rules most likely to be true positives appear first).
The editor's first fixes are also the ones they're most
confident about.

**Why this priority**: P1 because triage is the value-add over
raw lint output. A pre-sorted list is the difference between
"here are 23 things wrong" and "here are 23 things in the order
you should tackle them".

**Independent Test**: A fixture mixing errors and warnings; the
report's list places all errors before any warning, and within
each tier orders by rule precision descending (per the
precision-history DB).

**Acceptance Scenarios**:

1. **Given** a fixture with 2 error violations and 5 warning
   violations, **When** the report renders, **Then** items 1–2
   are the errors (ordered by precision) and items 3–7 are the
   warnings (ordered by precision).
2. **Given** the precision-history DB is missing, **When** the
   report renders, **Then** the within-tier ordering falls back
   to lexicographic rule-id (deterministic; documented).

---

### User Story 4 - Top-5 most-violated rules with examples (Priority: P2)

The report includes a "Top 5 most-violated rules" block: rule id,
violation count, one example excerpt from the manuscript,
guide-section link. The editor sees patterns at a glance.

**Why this priority**: P2 because the fix-me-first list is the
action item; the top-5 block is the diagnostic context.

**Independent Test**: A fixture where rule X fires 12 times;
the top-5 block lists X with count 12 and one example excerpt
referencing the manuscript file path + line.

**Acceptance Scenarios**:

1. **Given** a fixture where rule X fires 12 times, rule Y 8
   times, **When** the report renders, **Then** rule X is item
   1 in the top-5 block with count 12 and rule Y is item 2.
2. **Given** fewer than 5 distinct rules fired, **When** the
   report renders, **Then** the block lists all of them and
   states `(only N distinct rules)` rather than padding.

---

### User Story 5 - Manuscript metadata extraction (Priority: P2)

The report header shows the manuscript title (`\title{...}`),
authors (`\author{...}` or `\Plainauthor{...}`), and file count
(if multi-file project per spec 013). When `\title{}` / `\author`
are missing, the report falls back to the source file path as the
title.

**Why this priority**: P2 because the metadata adds editorial
polish; the report works with or without it.

**Independent Test**: A fixture with `\title{Foo}` and
`\author{Bar}` produces a report whose header lists those values;
a fixture without them produces a header using the file path.

**Acceptance Scenarios**:

1. **Given** a fixture with `\title{Statistical Methods}` and
   `\author{Alice Bob}`, **When** the report renders, **Then**
   the header reads `Title: Statistical Methods` and `Author:
   Alice Bob`.
2. **Given** a fixture without those macros, **When** the
   report renders, **Then** the header reads `File:
   manuscript.tex` and omits the author line.
3. **Given** the user passes `--title "Custom"` (override),
   **When** the report renders, **Then** the header reads
   `Title: Custom` regardless of the manuscript's content.

---

### Edge Cases

- All catalogue rules ignored via `--ignore-rules`: the
  conformance score reads `n/a` and the numbered list is
  empty.
- Manuscript has zero violations: the report still renders
  (score `100 %`, top-5 block empty, fix-me list empty); the
  editor can attach it as a "clean bill" letter.
- `--format pdf` without the `[pdf]` extra installed: exit 2
  with a stderr install hint (mirrors spec 011's `[lsp]`
  pattern).
- The `--out FILE` path's parent directory does not exist:
  exit 2 with a clear error.
- A manuscript with multiple `\author{}` entries: the report
  joins them with `, ` (the canonical JSS author-list
  format).
- A pure-`.bib` invocation (`jss-lint report refs.bib`): the
  report renders with `Title: refs.bib` and the relevant
  bibliography rules; metadata extraction is `.tex`-specific.
- The user passes a directory: process via the spec-013
  resolver and treat the result as a single project.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new subcommand `jss-lint report PATH` MUST be
  added (under the existing Click group from spec 009).
- **FR-002**: The subcommand MUST accept `--format
  {md,pdf,html}` (default `md`) and `--out FILE` (default
  stdout for md, required for pdf/html).
- **FR-003**: The report MUST contain six sections in this
  order:
  1. Header (title, author, file count, run date, linter
     version).
  2. Conformance score (`X %` and the formula numerator /
     denominator).
  3. Severity counts (errors / warnings / info).
  4. Top-5 most-violated rules with example excerpts and
     guide links (per spec 007).
  5. Numbered fix-me-first list (errors first, then
     warnings; precision-ordered within each tier).
  6. Footer (link to the JSS author guide; reproduction note
     stating the input commit hash if available).
- **FR-004**: The conformance score formula:
  `score = 100 * (rules_with_zero_violations /
  total_active_rules)`. `total_active_rules` excludes rules
  in `--ignore-rules` and excludes tool-side categories
  (`internal`, `parse`).
- **FR-005**: The fix-me-first list MUST order errors before
  warnings before info; within each tier, sort by descending
  rule precision (queried from
  `eval/precision-history.db` per spec 002 / 010).
- **FR-006**: When the precision DB is missing, the
  within-tier ordering MUST fall back to ascending rule id;
  this is documented in the report's footer.
- **FR-007**: Top-5 block: limit 5; show fewer when fewer
  distinct rules fired. Each entry: rule id, count, ONE
  example excerpt (file path + line + first 80 chars of the
  triggering source), guide-section link.
- **FR-008**: PDF rendering MUST use the optional `[pdf]`
  extra (`weasyprint>=60`). Without the extra, `--format
  pdf` exits 2 with the install hint.
- **FR-009**: HTML rendering MUST use the existing Jinja2
  templating layer from spec 001 (`output/html_output.py`)
  with a new `conformance.html.j2` template.
- **FR-010**: Markdown rendering MUST use a Jinja2 template
  `conformance.md.j2`. The output MUST be deterministic
  (same input → same bytes), modulo the run-date line which
  is the only non-deterministic value (and is omitted from
  the byte-equality test).
- **FR-011**: The report MUST honour the existing
  `--ignore-rules` and `.jss-lint.toml::ignore_rules`
  filters; ignored rules are excluded from the score
  numerator and denominator AND from the top-5 / fix-me
  blocks.
- **FR-012**: A `--title TEXT` and `--author TEXT` CLI
  override MUST be available so editors can set the metadata
  when the manuscript lacks `\title{}` / `\author{}`.

### Key Entities

- **Conformance score**: A single number,
  `100 * (rules_with_zero_violations / total_active_rules)`,
  rounded to the nearest integer.
- **Top-5 entry**: `(rule_id, count, example_file,
  example_line, example_excerpt, guide_section,
  guide_url)`.
- **Fix-me-first item**: `(rule_id, severity, count,
  precision)` ordered by `(severity, -precision, rule_id)`.
- **Manuscript metadata**: `(title, author, file_count,
  run_date)` with overrides honoured.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a fixture with N violations across R rules,
  `jss-lint report` produces a report whose top-5 + fix-me
  blocks together cover every violating rule (no
  rule-with-violations is missing from BOTH blocks).
- **SC-002**: The conformance score on a fixture with 50 of
  58 active rules passing reads `87 %`.
- **SC-003**: Markdown output is byte-deterministic across
  runs (modulo the run-date line).
- **SC-004**: PDF output is exactly one page on US Letter
  paper for a typical manuscript (≤30 violations); a
  manuscript with 100+ violations may overflow gracefully
  (no truncation, but flow to a second page).
- **SC-005**: HTML output renders without console errors in
  standard browsers.
- **SC-006**: The report's footer includes a
  reproducibility-note line citing the linter version + the
  manuscript's git commit hash (when discoverable).

## Assumptions

- The `[pdf]` extra brings in `weasyprint` (and its
  cairo-based dependencies); core users without the extra
  do NOT pay for it.
- Tool-side rules (`internal`, `parse`) are excluded from
  the score denominator but their violations DO appear in
  the severity counts (a parse failure is still a problem
  to flag).
- The precision DB is the spec-002 / 010 SQLite file at
  `eval/precision-history.db`. When the DB is unavailable
  in the user's install (e.g., end users without the eval
  extras), the fallback is documented and acceptable.
- The reproducibility-note's "manuscript git commit hash"
  is best-effort: the report shells out to `git rev-parse`
  in the manuscript's directory; on failure the line reads
  `(commit hash unavailable)`.
- Spec 015 does NOT change the existing `--output html`
  renderer; it adds a separate `--format html` for
  reports that uses the same Jinja2 stack but a different
  template.
- Single-page PDF is the design target, but graceful
  overflow to a second page is acceptable (per Edge Cases).
