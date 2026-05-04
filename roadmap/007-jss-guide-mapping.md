# 007 — JSS-guide rule mapping

**Phase:** Foundations
**Depends on:** —
**Unblocks:** 009 (`explain` subcommand), 015 (conformance report)

## Why

Authors and editors need to know *which paragraph of the JSS guide a
violation comes from*, not just an internal rule id. Without that
mapping the tool feels arbitrary; with it, the tool becomes the
canonical mechanical check for the journal.

## /speckit.specify prompt

Extend the existing `Rule` dataclass and `_catalogue_data.RULES`
metadata so every rule carries a `guide_section` string (e.g.,
`"§3.2 Citations"`) and a `guide_url` URL pointing to the public
JSS author-guide HTML/PDF anchor that defines the rule. Render
`guide_section` in terminal output ("see §3.2"), include both
fields in JSON output, include them in SARIF (006) as `helpUri` and
`shortDescription`, and in HTML output as a hyperlink. Add a
contract test that fails CI when any rule in the catalogue is
missing either field. A JSON file under `docs/jss-guide/index.json`
lists the canonical anchor URLs so they can be updated centrally
when the JSS guide is republished.

## /speckit.clarify prompt

Probe: (a) does the JSS author guide expose stable HTML anchors, or
do we ship a local mirror under `docs/jss-guide/`? (b) when one
rule implements multiple guide paragraphs, do we record a list or
pick one canonical citation? (c) do `JSS-PARSE-000` and other
tool-side rules get a special `guide_section: "internal"` value, or
are they exempt from the contract test? (d) is `guide_url`
mandatory at the catalogue level or only when the URL is known
(i.e., is a `TODO` sentinel allowed during rollout)?

## /speckit.plan prompt

Add `guide_section: str` and `guide_url: str | None` to `Rule` in
`src/texlint/api.py`. Mirror the fields in `_catalogue_data.RULES[*]`.
Backfill values for the existing 50+ rules in the catalogue, citing
the JSS author guide (https://www.jstatsoft.org/about/submissions).
Update the renderers (terminal, JSON, HTML, and 006-SARIF) to
surface the fields. Add
`tests/unit/test_catalogue.py::test_every_rule_cites_guide`
enforcing the contract. Ship a small `docs/jss-guide/index.json`
mapping section -> URL so future renderers don't hard-code links.
