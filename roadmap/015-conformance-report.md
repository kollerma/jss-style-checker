# 015 — One-page editor conformance report

**Phase:** CI / journal workflow
**Depends on:** 007 (JSS-guide mapping)
**Unblocks:** —

## Why

An editor wants one shareable artifact per submission: "this
manuscript is 87 % JSS-conformant; here are the 12 must-fix items,
with guide references." The existing per-violation list is
reviewer-noise; the conformance report is editor-signal.

## /speckit.specify prompt

Add `jss-lint report PATH [--format md|pdf|html] [--out FILE]`. The
output is a one-page summary containing: manuscript metadata
(title, author, file count), overall conformance score (% of rules
passing on this manuscript), error/warning/info counts, top-five
most violated rules with one example each (linked to the JSS guide
via spec 007), and a numbered "fix me first" list (errors before
warnings, sorted by rule precision). Markdown is the canonical
format; PDF rendered via WeasyPrint; HTML via the existing Jinja2
templates. Designed to be attached to an editorial decision letter.

## /speckit.clarify prompt

Probe: (a) is WeasyPrint an acceptable runtime dep (it pulls in
cairo) or do we offer PDF only as an extra `[pdf]`? (b) does the
score weight errors vs warnings (e.g., 3:1) or count
rules-passing/rules-total unweighted? (c) do we include
manuscript-level metadata only when the preamble exposes
`\title{}` / `\Plainauthor{}`, or do we accept CLI overrides?
(d) is the markdown output stable across runs (deterministic
section order)?

## /speckit.plan prompt

New module `src/texlint/report.py::render_report(report, doc,
format, out)`. New Jinja2 template
`src/texlint/output/templates/conformance.md.j2` plus `.html.j2`.
PDF renderer in `src/texlint/output/pdf.py` using `weasyprint`
(extra `[pdf]` dependency). Add `report` as a Click subcommand.
Score formula: `100 * (rules_with_zero_violations / total_active_rules)`,
documented in the spec. Add `tests/unit/test_report.py` with a
golden markdown fixture. Update README with a "For editors"
section showing the report.
