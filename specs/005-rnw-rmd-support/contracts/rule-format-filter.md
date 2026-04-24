# Contract: `Rule.formats` filter and `ComplianceReport.skipped_rules`

## Semantics change (API-additive)

`Rule.formats` (declared in `src/texlint/api.py`) shifts from
**file-suffix filter** (spec 001: `{".tex", ".bib"}`) to
**input-format filter** (spec 005: `{"tex", "rnw", "rmd"}`).

Valid values:

| Value | Applies to |
|---|---|
| `None` (default) | Every input format. |
| `frozenset({"tex"})` | Pure `.tex` inputs only. |
| `frozenset({"tex", "rnw"})` | `.tex` and stripped `.Rnw` (Sweave). Most common narrowing. |
| `frozenset({"rmd"})` | Rmd-specific rules. No spec-004 rule uses this; reserved. |
| `frozenset({"tex", "rnw", "rmd"})` | Semantically equivalent to `None`; prefer `None` unless future rules add a fourth format tag. |

## Dispatch algorithm

```python
def _rule_applies(rule: Rule, input_formats: set[str]) -> bool:
    if rule.formats is None:
        return True
    return bool(rule.formats & input_formats)
```

`input_formats` is the union of formats present in the current
`ParsedDocument`. For a mixed document (e.g., `jss-lint paper.tex
paper.Rmd`), `input_formats = {"tex", "rmd"}` and a rule with
`formats={"tex", "rnw"}` applies (because `"tex"` is in the
intersection); the rule sees the `.tex` input and skips the `.Rmd`
(no tex-like view is populated from the Rmd except the raw-LaTeX
islands, which are iterated via `doc.all_tex_like()`).

## Skipped-rule reporting

When a rule is NOT invoked because `rule.formats` excludes every
input format present, `engine.run` records:

```python
@dataclass(frozen=True)
class SkippedRule:
    rule_id: str
    reason: str  # e.g., "format mismatch: rule formats={'tex','rnw'}, inputs={'rmd'}"
```

in `ComplianceReport.skipped_rules`. One entry per rule per run.

## `--verbose` terminal rendering

When `ToolConfig.verbose` is `True` and `skipped_rules` is non-empty,
the terminal renderer emits an additional block after the violations
table:

```text
─────────────────────────────── Skipped rules ───────────────────────────────
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Rule                ┃ Reason                                             ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ JSS-PRE-001         │ format mismatch (rule: tex,rnw; inputs: rmd)      │
│ JSS-PRE-002         │ format mismatch (rule: tex,rnw; inputs: rmd)      │
│ … 6 more preamble rules …                                               │
└─────────────────────┴────────────────────────────────────────────────────┘
```

In non-verbose mode the section is omitted entirely (back-compat with
existing CI consumers).

## JSON / HTML rendering

- JSON: top-level `skipped_rules: [{rule_id, reason}, ...]` key.
  Always present (possibly empty).
- HTML: additional section analogous to the terminal table, rendered
  only when non-empty.

## Invariants

| # | Invariant | Enforcer |
|---|---|---|
| F-1 | A rule never appears in both `violations` and `skipped_rules` for the same run. | `test_skipped_not_violated` |
| F-2 | `CategorySummary.rules_applied` counts only rules that were NOT skipped. | `test_rules_applied_excludes_skipped` |
| F-3 | `compliance_percentage` excludes skipped rules from the denominator (inherited from spec 001's existing "SKIPPED category" behavior). | `test_compliance_pct_excludes_skipped` |
| F-4 | Non-verbose output byte-matches pre-feature output on a pure `.tex` + `.bib` input (FR-015 regression). | `test_backcompat_non_verbose` |
