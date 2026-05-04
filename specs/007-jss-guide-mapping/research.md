# Research: JSS-guide Rule Mapping

**Phase**: 0 (Outline & Research)
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

This file resolves the design decisions identified during planning.

---

## 1. URL stability of the public JSS author guide

**Decision**: The canonical citation source is the public JSS
author-guide page at `https://www.jstatsoft.org/about/submissions`,
extended with anchors when the published HTML exposes them. URLs
are indirected through `docs/jss-guide/index.json`, which is the
single point of update when the guide is republished.

**Rationale**:
- A republished guide changes anchors; centralising URLs in one
  file keeps the catalogue stable across re-publications.
- Anchor-based deep links exist for the major sections; we
  prefer them when available, page-level URLs as fall-backs.
- Mirroring the guide content locally was rejected (research §2).

**Alternatives considered**:
- Hard-code URLs in `_catalogue_data.RULES`: rejected — every
  re-publication touches ~50 lines spread across the file.
- Mirror the guide as Markdown under `docs/jss-guide/`: rejected
  per research §2.

---

## 2. Mirroring the JSS guide locally

**Decision**: Do NOT mirror the guide content. `docs/jss-guide/`
contains exactly one file, `index.json`.

**Rationale**:
- Hosting a copy of the journal's authorship documentation
  inside the linter repo creates an authoritativeness conflict
  (the official guide is the law; our copy is forever a moment
  behind).
- Maintenance cost: every re-publication would require a
  re-render and a content-diff review, instead of a single URL
  update.
- Constitution §X (Small Surface): a local mirror is dead weight
  compared with a URL.

**Alternatives considered**:
- Vendor the guide as PDF: rejected — binary blob in version
  control, copyright friction, Constitution §X.
- Vendor the guide as Markdown extracted from the PDF: rejected
  — extraction is manual, drifts from upstream.

---

## 3. Multi-paragraph rule citations

**Decision**: `guide_section` is a scalar `str`. Rules that span
multiple paragraphs cite the *single most-canonical* (highest-
numbered, most specific) paragraph. The full coverage prose lives
in `Rule.description`.

**Rationale**:
- Scalar simplifies every renderer (no array splat, no "n more"
  UI affordance).
- Highest-numbered convention prefers specificity (e.g., §3.2.4
  over §3.2). Specific citations help authors find the exact
  rule faster than broad ones.
- `description` is already the right place for "see also §3.3,
  §3.4" prose.

**Alternatives considered**:
- `guide_section: list[str]`: rejected — every renderer would
  need to choose between joining, truncating, or splatting; the
  UI surface multiplies without proportional value.
- `guide_section: str` + `guide_section_extras: list[str]`:
  rejected — double-bookkeeping, two contract tests, two
  failure modes for the same field.

---

## 4. Tool-side rules and the contract test

**Decision**: Tool-side rules (categories `internal`, `parse`)
use the sentinel `guide_section = "internal"` and `guide_url =
None`. The contract test treats this combination as valid; any
other combination fails CI.

**Rationale**:
- A made-up "JSS author guide §0" anchor would mislead authors
  who clicked it.
- Skipping these rules from the contract test entirely creates
  a category-membership trap (which rules are "tool-side"? the
  test has to know).
- An explicit sentinel is auditable. Reviewers see
  `guide_section = "internal"` and know to look at the
  category check, not the URL.

**Alternatives considered**:
- Empty string `""` as sentinel: rejected — "" is also the
  "missing" failure mode, conflating two states.
- Skip the contract test for `category in {"internal", "parse"}`:
  rejected — drift-prone (a future tool-side rule's category
  would need to be added to the skip list).
- A `Rule.is_internal: bool` field: rejected — increases surface
  for one corner case; the sentinel encodes the same bit.

---

## 5. `TODO` strings during rollout

**Decision**: No `TODO` sentinel. `guide_url` is either a real
URL string or `None` (only for sentinel rules). The contract
test enforces this.

**Rationale**:
- A `TODO` string would silently survive reviews and ship to
  authors as a non-clickable "URL". Either it's a URL or it
  isn't.
- The page-level URL of the JSS author guide is always
  available as a fall-back, so no rule should ever lack a URL
  during rollout.

**Alternatives considered**:
- Allow `"TODO"` and ignore in renderers: rejected — invisible
  rot accumulator.
- Require URLs only for new rules (grandfather existing): rejected
  — defeats the SC-001 100% target.

---

## 6. `index.json` schema

**Decision**: A single top-level key `sections` mapping
section labels (the same strings used as `Rule.guide_section`)
to absolute URLs:

```json
{
  "sections": {
    "§3.2 Citations": "https://www.jstatsoft.org/.../section-3-2",
    "§5.1 Bibliography": "https://www.jstatsoft.org/.../section-5-1"
  }
}
```

The catalogue contract test loads this file once and checks two
invariants:
1. Every citable rule's `guide_section` appears as a key in
   `sections`.
2. Every citable rule's `guide_url` matches `sections[
   guide_section]`.

**Rationale**:
- Single-file source of truth with O(1) look-up.
- Matching both `section` and `url` catches drift where a rule
  copies an old URL after the index updates.

**Alternatives considered**:
- Store URLs only on rules; no index file: rejected per
  research §1.
- Index file as a list of `{section, url}` objects: rejected —
  the dict form gives constant-time look-up and JSON object
  ordering is preserved by Python ≥3.7.
- Add an `aliases` field for legacy section names: rejected —
  premature; we'll add it the first time we need it.

---

## 7. Renderer integration of `helpUri` (SARIF)

**Decision**: SARIF's `tool.driver.rules[].helpUri` reads from
`Rule.guide_url`. Spec 006's prior `helpUri` source (the existing
`Rule.help_url` field, if any) is replaced; if both fields exist
we treat `guide_url` as authoritative.

**Rationale**:
- Spec 006 already wired `helpUri` to "an existing
  `Rule.help_url` when known". Spec 007 makes that field the
  same thing as `guide_url`.
- Maintaining two URLs (`help_url` and `guide_url`) per rule
  creates ambiguity for downstream consumers.

**Alternatives considered**:
- Keep both fields with `help_url` as a per-renderer override:
  rejected — Constitution §X.
- Concatenate both URLs as a SARIF array: rejected — SARIF
  allows multiple `helpUri` only via per-result overrides;
  the rule-level field is scalar.

**Migration**: spec 007 deletes `Rule.help_url` if it exists in
the spec-006 implementation, replacing it with `guide_url`.
This is a public-API removal — documented in plan
`Project Structure`. The deletion is safe because no external
plugin has shipped against the spec-006 catalogue.

---

## 8. SARIF `shortDescription` augmentation

**Decision**: When the rule has a non-`None` `guide_url`,
`shortDescription.text` reads as `"<Rule.title> (<Rule.guide_section>)"`.
For sentinel rules, `shortDescription.text` is `Rule.title`
unchanged.

**Rationale**:
- GitHub code scanning displays `shortDescription` in
  list views; bundling the section into the title means
  reviewers see it without expanding the result.
- SARIF allows arbitrary text in `shortDescription`; this is
  the format-canonical surface for rule-level guidance.

**Alternatives considered**:
- Add a custom `properties.section` field: rejected — GitHub's
  UI ignores unknown properties.
- Render the section into `fullDescription` only: rejected —
  not surfaced in list views.

---

## Summary

All eight decisions follow from the spec Clarifications and
Constitution §I, §IV, §X. No remaining `NEEDS CLARIFICATION`.
Ready for Phase 1.
