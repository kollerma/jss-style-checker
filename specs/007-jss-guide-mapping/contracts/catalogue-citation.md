# Contract: Catalogue Citation Invariants

**Phase**: 1 (Design & Contracts)
**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

This contract documents the invariants that
`tests/unit/test_catalogue.py::test_every_rule_cites_guide` and
`test_guide_urls_resolve_through_index` enforce.

## C-1 `guide_section` is non-empty for every rule

For every `rule` in `_catalogue_data.RULES`:
`isinstance(rule.guide_section, str) and rule.guide_section != ""`.

Failure mode: contract test names the offending rule id and the
field, e.g.
`JSS-CITE-002 has empty guide_section`.

## C-2 Citable rules have a real URL

For every `rule` whose `category in CITABLE_CATEGORIES`:

- `rule.guide_url is not None`.
- `isinstance(rule.guide_url, str)`.
- `rule.guide_url.startswith("https://")`.
- `rule.guide_section != "internal"`.

Failure mode: contract test names the rule id and the violated
sub-invariant, e.g.
`JSS-CITE-002 has guide_url=None but category=markup is citable`.

## C-3 Tool-side rules use the sentinel exactly

For every `rule` whose `category in {"internal", "parse"}`:

- `rule.guide_section == "internal"`.
- `rule.guide_url is None`.

Failure mode: contract test names the rule id and the violated
sub-invariant, e.g.
`JSS-PARSE-000 has guide_url="https://..." but category=parse must use sentinel`.

## C-4 Citable rules' `guide_section` resolves through the index

For every `rule` whose `category in CITABLE_CATEGORIES`, with
`idx = load_guide_index()`:

- `rule.guide_section in idx`.
- `idx[rule.guide_section] == rule.guide_url`.

Failure mode: contract test names the rule id and the section,
e.g.
`JSS-CITE-002 cites §3.2 Citations but index.json has no such key`
or
`JSS-CITE-002 guide_url disagrees with index.json["§3.2 Citations"]`.

## C-5 `index.json` URLs are absolute

For every `(section, url)` pair in `idx`:
`url.startswith("https://")`.

Failure mode: contract test names the offending section and URL.

## C-6 Citation contract is part of CI

The two contract tests run as part of the standard `pytest`
invocation. CI fails on the first violation; the failure message
is sufficient to fix without consulting the spec.

## C-7 No `TODO` placeholders

The contract tests reject `guide_url` values that contain the
substring `"TODO"` (case-insensitive) or `guide_section` values
that contain that substring. There is no "in-progress" sentinel —
either the rule has a real URL or it is tool-side.

Failure mode: contract test names the rule id, the field, and
echoes the offending substring.

## C-8 Renderer projection invariants

These invariants are enforced by the renderer tests, not the
catalogue contract test, but are documented here for cross-
reference:

- **terminal**: line for a citable violation contains exactly one
  occurrence of `(see <Rule.guide_section>)`. Sentinel violation
  lines contain zero occurrences of `(see `.
- **JSON**: every violation entry contains both `guide_section`
  and `guide_url` keys; sort order is preserved by
  `sort_keys=True`.
- **SARIF**: `tool.driver.rules[]` entry for a citable rule has
  `helpUri == Rule.guide_url`; `shortDescription.text` contains
  `Rule.guide_section`. Sentinel rules omit `helpUri` and have
  unaugmented `shortDescription`.
- **HTML**: row for a citable violation contains
  `<a href="<guide_url>">…</a>`; sentinel rows render the
  section as plain text.

## C-9 Backwards compatibility

This contract is additive at the JSON / SARIF level. Pre-spec-007
consumers that ignore unknown fields continue to work. Pre-spec-007
golden fixtures in this repo are regenerated as part of the spec.
