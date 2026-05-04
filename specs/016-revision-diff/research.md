# Research: `jss-lint diff`

**Phase**: 0
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. Identity tuple

**Decision**: `(rule_id, file, line, message)` by default;
`(rule_id, file, message)` with `--ignore-line-drift`.

**Rationale**:
- Per Clarifications §1: `severity` does not participate
  (rules don't change severity within a tool version);
  `column` does not participate (column drift is too
  noisy on real LaTeX).
- `message` (the full rendered string) participates so
  two same-rule violations on the same line that flag
  different content are distinguishable.
- `--ignore-line-drift` drops `line`; nothing else
  changes.

**Alternatives considered**:
- `(rule_id, file, line, column, message_template)`:
  rejected — column adds noise.
- `(rule_id, file, line)`: rejected — same-rule
  same-line violations on different content would
  collapse.
- `(rule_id, file)`: rejected — too coarse; would
  collapse five different `JSS-CITE-002` issues in one
  file into one.

---

## 2. Rule-rename migration map

**Decision**: A JSON file at
`docs/jss-guide/rule-renames.json` holding
`{old_id: new_id, ...}`. The diff command applies the map
to OLD violations before identity comparison.

**Rationale**:
- Renames are rare but not zero.
- Centralising the map in one file makes the "what
  renamed when" trail auditable.
- Empty map is the spec-016 baseline; entries land in
  later specs that rename rules.

**Alternatives considered**:
- No support for renames (always treat as
  fixed+introduced): rejected per Clarifications §2.
- Embed renames in the catalogue itself: rejected — the
  catalogue describes the *current* rule set; rename
  history belongs in a side file.
- Fetch rename map from PyPI metadata: rejected — would
  require a network call (Constitution §I) and would
  couple diff to package-distribution channels.

---

## 3. Markdown flavour

**Decision**: GitHub-flavoured CommonMark.

**Rationale**:
- Per Clarifications §3: GitHub PR comments are the
  primary consumer of the markdown format.
- Tables (for the summary count line) and inline code
  blocks render correctly on GitHub.

**Alternatives considered**:
- Pure CommonMark: rejected per rationale.
- Org-mode: rejected — no standardised renderer in CI
  surfaces.
- Pandoc-extended markdown: rejected — Pandoc-only
  features rendered as raw markup on GitHub.

---

## 4. Three-way diff (vs. baseline)

**Decision**: Out of scope for v1.

**Rationale**:
- Per Clarifications §4: a future `--baseline` flag
  could add the third side; v1 keeps the surface clean.
- The transitive question ("is `unchanged` defined
  vs. baseline-OLD or OLD-NEW?") needs its own design
  pass.

**Alternatives considered**:
- Add `--baseline FILE` in v1: rejected — premature.
- Define `unchanged` as the intersection of all three
  sides: rejected — rules out the most common
  three-way use case ("compared to clean template,
  what new violations did this revision add?").

---

## 5. Renderer reuse

**Decision**: Terminal format reuses the existing
spec-001 reviewer-mode renderer
(`output/terminal.py::render(report, cfg)` with
`cfg.mode = "reviewer"`). Markdown and JSON formats
have small new renderers in `diff.py`.

**Rationale**:
- The reviewer-mode style already groups by rule and
  uses colour appropriately for terminal output.
- Inventing a new terminal renderer would diverge
  styling.

**Alternatives considered**:
- Bespoke terminal renderer per format: rejected —
  styling drift.
- Force markdown / JSON to also reuse spec-001
  renderers: rejected — those renderers don't have
  the three-way partition shape.

---

## 6. Schema validation of inputs

**Decision**: Validate both OLD and NEW JSON against
the spec-001 `--output json` JSON Schema. Mismatches
exit 2 with the offending file named.

**Rationale**:
- A diff over invalid input is unsound. Better to
  fail fast.
- The spec-001 schema is the established contract;
  reusing it costs zero new schema files.

**Alternatives considered**:
- Skip validation and trust the input: rejected — a
  truncated or hand-edited JSON could pass through
  silently and produce nonsense diffs.
- Validate only the violation array shape: rejected
  — the schema covers more (counts, version);
  validating the whole shape is one call.

---

## 7. Determinism of unchanged-group rendering

**Decision**: For a violation that appears in both
OLD and NEW, the rendered entry uses NEW's `line`,
`column`, `message`. The `unchanged` group's order is
sorted by `(file, line, rule_id)` ascending.

**Rationale**:
- The `unchanged` set is what the user will *still*
  see if they re-run the linter; using NEW's values
  keeps the rendered output aligned with what the
  current source produces.
- Deterministic ordering simplifies golden tests.

**Alternatives considered**:
- Use OLD's values: rejected — confusing on revision-
  round diffs.
- No defined order: rejected — non-deterministic.

---

## 8. Exit code semantics

**Decision** (from spec FR-005):
- `0` when `len(introduced) == 0`.
- `1` when `len(introduced) > 0`.
- `2` on usage error.

**Rationale**:
- This is the practical CI signal: "did this PR add
  new violations?" The fixed / unchanged counts are
  informational, not gating.
- Exit 2 for usage error matches every other
  subcommand's convention.

**Alternatives considered**:
- Exit 1 if `len(fixed) == 0` (i.e., "we didn't fix
  anything"): rejected — penalises PRs that don't
  touch the manuscript.
- Exit 1 only if `unchanged > 0`: rejected — would
  block forever on legacy violations.

---

## Summary

All eight decisions follow from spec Clarifications and
Constitution §I, §III, §X. No remaining `NEEDS
CLARIFICATION`. Ready for Phase 1.
