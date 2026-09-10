# Contract: Guide coverage file and its surfaces

**Plan**: [../plan.md](../plan.md) §7.1, §7.3
**Data model**: [../data-model.md](../data-model.md) §4.3

## C-1 Location and authority

`specs/003-jss-rule-catalogue/guide-coverage.yaml` is the single source
of truth for "which guide provisions does the tool check". It is
hand-curated, vendored beside `catalogue.yaml` into the Rust crate and
the R package, and read by both engines' codegen. The markdown matrix in
`checklists/rule-catalogue-review.md` §1 becomes a historical record with
a note pointing here.

## C-2 Schema

```yaml
version: 1
sources:
  jss_cls:             {file: docs/jss-template/jss.cls, edition: "3.3", date: "2021-05-23"}
  article_tex:         {file: docs/jss-template/article.tex, date: "2021-12-10"}
  style_guide:         {url: "https://www.jstatsoft.org/style", fetched: "2026-04-23"}
  author_instructions: {url: "https://www.jstatsoft.org/authors", fetched: "2026-04-23"}
directives:
  - id: SG-024
    source: style_guide
    section: "§4.3 Typography"
    provision: "All table row/column headers are in sentence style"
    status: not_checked
    rules: []
    reason: "needs a tabular-cell-aware check"
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | unique; prefix `CLS-`, `TEX-`, `SG-`, `AI-` matching `source` |
| `source` | enum | yes | `jss_cls`, `article_tex`, `style_guide`, `author_instructions` |
| `section` | string | yes | a key of `docs/jss-guide/index.json`, a `#anchor`, a `jss.cls:N`/`article.tex:N` locator, or `internal` |
| `provision` | string | yes | one line |
| `status` | enum | yes | `checked`, `partial`, `not_checked`, `out_of_scope` |
| `rules` | list | yes | active catalogue rule ids; non-empty iff status ∈ {checked, partial} |
| `reason` | string | iff status ≠ checked | one line |

`sources` records the dated edition of each authority: this is the
release's answer to "which edition of the guide the rule set derives
from" (the prose guide has no edition; the fetch date is the honest pin).

## C-3 Validator (`tools/_coverage_validate.py` + contract test)

Fails the build when:

- an `id` repeats or its prefix does not match `source`;
- `status` is outside the enum;
- `rules` is empty for `checked`/`partial` or non-empty otherwise;
- any listed rule is not an **active** catalogue rule (retirement turns
  the row red — this is what caught the seven rows crediting
  `JSS-CITE-001/ABBR-002/REFS-002/CAP-003`);
- `reason` is missing for a non-checked row;
- `section` is not resolvable as above;
- any active, non-`internal` catalogue rule is claimed by no directive
  (Constitution §V: a rule without a provision has no authority).

## C-4 Counts

`counts` = number of directives per status over all four sources. The
author footer prints `checks N of M` where `N = checked + partial` and
`M = checked + partial + not_checked` (out-of-scope provisions are not
"checkable from source" and are excluded from the ratio but listed by the
subcommand).

## C-5 Reviewer-mode block (terminal and HTML, both engines)

After the `Overall:` and `Measured recall:` lines:

```
──────────────────────────── Not checked by jss-lint ────────────────────────────
┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Directive ┃ Status      ┃ Provision                                            ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ SG-014    │ partial     │ In title style, capitalise all principal words …    │
│ SG-020    │ not checked │ Introduce all abbreviations with expansion at …     │
└───────────┴─────────────┴──────────────────────────────────────────────────────┘
Run jss-lint coverage for the full matrix (71 checked, 6 partial, 9 not checked, 34 out of scope).
```

Rows: `partial` first, then `not_checked`, each group sorted by `id`.
`out_of_scope` rows are not listed here. HTML: `<table class="coverage">`
with the same rows and the same closing sentence in a `<p>`.

## C-6 `coverage` subcommand formats

| Format | Content |
|---|---|
| `terminal` | header `Guide coverage — jss (rule set 2026-09-15)`, counts line, then one group per status in the order checked, partial, not checked, out of scope; each directive as `  <id>  <section>  <provision>` followed by `        reason: …` (non-checked) and `        rules: …` (checked/partial). |
| `markdown` | one table per source (`Directive | Status | Provision | Rules | Reason`), sources in the order of the `sources` block. |
| `json` | `{"counts": {...}, "sources": {...}, "directives": [full objects incl. provision]}`, `sort_keys`, indent 2. |

Byte-identical across engines (`coverage_parity.rs`).

## C-7 Report JSON

`json-output-1.2.md` C-4: `counts` plus `items` restricted to
`partial`/`not_checked` without provision text.

## C-8 `explain`

`jss-lint explain RULE` prints `Covers: SG-027, SG-028` listing every
directive whose `rules` include the rule, sorted by id; omitted for
`internal`-only rules.

## C-9 Catalogue page

`tools/render_catalogue.py` renders a `Coverage` section from this file
(one table per source, same columns as the markdown format) below the
per-category rule tables.
