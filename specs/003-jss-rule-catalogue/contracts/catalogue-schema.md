# Contract: `catalogue.yaml` — Rule Catalogue Schema

**Path**: `specs/003-jss-rule-catalogue/catalogue.yaml`
**Format**: YAML 1.1 (PyYAML `safe_load`; no custom tags, no `!!python/object`)
**Source of truth**: yes. Markdown at `catalogue.md` is re-rendered from this file; any drift between them fails `tests/unit/journals/jss/test_render.py`.

## Top-level document

Exactly one YAML mapping at the document root, with exactly these keys:

```yaml
version: 1
source_vendored_at: "2021-05-23"
categories:
  - preamble
  - structure
  - markup
  - citations
  - references
  - bibtex
  - naming
  - capitalization
  - typography
  - abbreviations
  - code_style
  - code_width
  - operators
  - crossrefs
  - house_style
rules:
  - {rule fields — see below}
  - ...
```

| Key | Type | Notes |
|---|---|---|
| `version` | int | Schema version. Starts at `1`. Bump on any backwards-incompatible field change. |
| `source_vendored_at` | str (ISO-8601 date) | The vendored `docs/jss-template/jss.cls`'s `\filedate`. Updated when the annual re-fetch lands. |
| `categories` | list[str] | The pinned category list (FR-005). A category may be added, merged, or dropped here; rule rows must then align. |
| `rules` | list[mapping] | The rule rows. Order here is irrelevant — `render_catalogue.py` sorts on output. |

## Per-rule fields

Every entry in `rules` is a YAML mapping with **exactly** these keys (extra keys fail the catalogue test; missing required keys fail it):

### Required

```yaml
rule_id: JSS-CITE-001
category: citations
severity: warning          # error | warning | info
description: \emph{Key1984} looks like a citation key; use \cite
authority: style_guide     # jss_cls | article_tex | style_guide | author_instructions
authority_ref: "#what-are-the-different-cite-citet-citep-commands-about"
example_violation: |
  Recently, \emph{Knuth1984} showed that ...
example_fix: |
  Recently, \cite{Knuth1984} showed that ...
inspects: [tex_files]      # non-empty subset of {tex_files, bib_files, raw_source}
auto_fixable: false
```

### Optional

```yaml
notes: |
  Losing authority: author_instructions prose is silent on this; the style
  guide anchor is authoritative.
```

## Field-by-field contract

### `rule_id`

- Format: `^JSS-[A-Z]+-\d{3}$` (anchored regex).
- Unique across the whole file (not merely within its category).
- Once a rule is committed, its `rule_id` is permanent. A retired rule is removed from the file; its `rule_id` is never reassigned (spec FR-004).
- The category portion (the `[A-Z]+` between dashes) is an abbreviation of the `category` value. Canonical abbreviations:

  | category | rule_id prefix |
  |---|---|
  | preamble | `JSS-PRE-` |
  | structure | `JSS-STRUCT-` |
  | markup | `JSS-MARKUP-` |
  | citations | `JSS-CITE-` |
  | references | `JSS-REFS-` |
  | bibtex | `JSS-BIBTEX-` |
  | naming | `JSS-NAME-` |
  | capitalization | `JSS-CAP-` |
  | typography | `JSS-TYPO-` |
  | abbreviations | `JSS-ABBR-` |
  | code_style | `JSS-CODE-` |
  | code_width | `JSS-WIDTH-` |
  | operators | `JSS-OPER-` |
  | crossrefs | `JSS-XREF-` |
  | house_style | `JSS-HOUSE-` |

### `category`

- Must equal the string of exactly one entry in the top-level `categories` list.
- Matches the filename `src/texlint/journals/jss/rules/<category>.py`.

### `severity`

- One of `error`, `warning`, `info`. No other values accepted.
- Default assignment guidance: objectively-wrong → `error`; stylistic → `warning`; informational → `info`. Deviations explained in `notes`.

### `description`

- Non-empty single line.
- Max 120 characters.
- No leading/trailing whitespace.
- No trailing period (rendered tables look uniform).

### `authority`

- One of `jss_cls`, `article_tex`, `style_guide`, `author_instructions`.
- Priority on conflict (FR-003): `jss_cls > article_tex > style_guide > author_instructions`. Losing authority recorded in `notes`.

### `authority_ref`

Format depends on `authority`:

| authority | format | example | validator (in `test_catalogue.py`) |
|---|---|---|---|
| `jss_cls` | `jss.cls:N` (line number) or `jss.cls:\macroname` | `jss.cls:477` or `jss.cls:\pkg` | line in `1..len(lines)` of vendored file; or exactly one hit for `\macroname` (fixed-string search). |
| `article_tex` | `article.tex:N` or `article.tex:§label` | `article.tex:86` or `article.tex:§sec:intro` | line exists or `\label{sec:...}` / `\label{app:...}` appears in vendored file. |
| `style_guide` | `#anchor-id` | `#how-should-abbrevations-be-formatted` | matches `^#[a-z0-9-]+$`. |
| `author_instructions` | section slug or `#anchor-id` | `manuscript-preparation` or `#requirements` | matches `^#?[a-z0-9-]+$`; no line numbers (FR-010). |

### `example_violation` and `example_fix`

- YAML `|` (literal block) scalar — preserves newlines and backslashes byte-for-byte.
- Minimal self-contained LaTeX or BibTeX fragment.
- Should match the rule's check — a reviewer running the example through `jss-lint` sees exactly one violation for the `example_violation` and zero for the `example_fix`.
- Trailing newline is permitted (YAML `|` adds one); the renderer strips a single trailing newline when laying out the markdown table cell.

### `inspects`

- YAML sequence of strings, at least one element.
- Each element is one of `tex_files`, `bib_files`, `raw_source`.
- `raw_source` requires a matching `notes` entry justifying the choice (Constitution §II).

### `auto_fixable`

- Strict boolean (YAML `true` / `false`). No `null`, no string.
- `true` asserts the fix is mechanically expressible (promise to Step 5); `false` declares diagnosis-only.

### `notes` (optional)

- Free text, any length.
- Use cases: losing-authority record, §II justification for `raw_source`, narrowing rationale, cross-reference to another rule the check could have fallen under.

## Forbidden keys

Any key not in the required-or-optional sets above fails `test_catalogue.py`. This includes:

- `fix` / `fix_suggestion` — Step 5 scope, not this spec.
- `formats` — always `None` in this spec (FR-014); narrowing is Step 4 scope.
- `status` / `ready` / `deprecated` — retirement is by removal, not by flag (spec §Edge Cases, FR-004).
- `owner` / `author` / `reviewed_by` — PR metadata, not catalogue metadata.

## Validation invariants

Every invariant below is enforced by `tests/unit/journals/jss/test_catalogue.py`:

1. Top-level keys are exactly `{version, source_vendored_at, categories, rules}`.
2. `version == 1`.
3. Every `rule_id` is globally unique.
4. Every `rule_id` matches the category prefix table.
5. Every `category` appears in the top-level `categories` list.
6. Every top-level category appears on ≥ 1 rule.
7. Every `authority_ref` resolves per the validator table above.
8. Every rule carries the required fields; no rule carries a forbidden key.
9. No rule has an empty or whitespace-only `description`, `example_violation`, or `example_fix`.
10. Every `raw_source` inspects entry has a non-empty `notes` field.

## Example entry

```yaml
- rule_id: JSS-CITE-001
  category: citations
  severity: warning
  description: \emph used where a citation key is meant; use \cite instead
  authority: style_guide
  authority_ref: "#what-are-the-different-cite-citet-citep-commands-about"
  example_violation: |
    Recently \emph{Knuth1984} described algorithms.
  example_fix: |
    Recently \cite{Knuth1984} described algorithms.
  inspects: [tex_files]
  auto_fixable: true
  notes: |
    Retrofit of the Step 1 smoke rule cite_001_emph.py. The check walks the
    AST for \emph macros whose argument matches the bibkey regex
    ^[A-Za-z][A-Za-z0-9_-]*\d{4}$.
```
