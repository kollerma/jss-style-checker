# Phase 0 Research — JSS Rule Modules

Consolidates the design decisions the plan takes from the `/speckit.plan` input's implementation template, from spec 003's reverted Phase 5 prior art, and from the four `/speckit.clarify` answers encoded into `spec.md`.

## 1. Check callable naming: public `check_<rule_id_suffix>`

**Decision**: each rule module exports a **public** callable named `check_<lowercased_rule_id_with_underscores>` (e.g., `JSS-CITE-002` → `check_jss_cite_002`). The `Rule` object's `check` field binds the same callable. No underscore-prefixed private variant.

**Rationale**:
- Test files can import the callable directly: `from texlint.journals.jss.rules.citations import check_jss_cite_002`. This is what the user's test template in `/speckit.plan` input uses.
- Matching name and `rule_id`: rule `JSS-CITE-002` binds callable `check_jss_cite_002`. Grep-discoverable; no mental translation.
- Module-level public API is small and regular: one callable per rule plus one `Rule` instance per rule plus one module-level `rules: tuple[Rule, ...]`. That's the entire surface.

**Alternatives considered**:
- **Underscore-prefixed private** (`_check_jss_citations_001`, keyed by category + counter): what spec 003's `contracts/rules-module.md` pinned. Clearer encapsulation but loses direct test-import access; requires reviewers to translate category+counter ↔ rule id. Rejected because spec 003's rule-module contract was never materialised (catalogue-only scope) and the plan input supersedes it.
- **Decorator registration**: `@register(id="JSS-CITE-002")`. Import-time side effects; violates §IV's "no ad-hoc registration". Rejected.

**Consequence**: `contracts/rules-module.md` pins the name shape; the CI consistency test in `contracts/catalogue-consistency.md` doesn't need to walk modules — it only walks `JSSJournal.categories()`'s returned `RuleCategory` tuples.

## 2. Shared helpers: private `_helpers.py` inside `rules/`

**Decision**: a single private module at `src/texlint/journals/jss/rules/_helpers.py` exports the shared walker + verbatim/comment safety primitives. The module is underscore-prefixed to mark it private to the `rules/` package.

**Exports**:
- `_walk(nodes) -> Iterator[Node]`: pre-order traversal over a pylatexenc node list. Yields every `LatexNode` subclass (macros, environments, groups, chars, math, comments). Recurses into environment bodies, group contents, math-node contents, and macro argument groups.
- `_macro_args_text(macro_node) -> str`: concatenated char content of the macro's first argument group, stripped. Handles both pylatexenc-known macros (arg in `nodeargd.argnlist`) and unknown macros (arg is the next sibling `LatexGroupNode`) — the lesson from spec 003's reverted Phase 5 work.
- `_next_group_arg(parent_nodelist, idx) -> LatexGroupNode | None`: fallback for the unknown-macro case; returns the sibling group after `parent[idx]`.
- `_iter_with_parent(nodes) -> Iterator[tuple[Sequence, int, Node]]`: the walker variant that yields `(parent_nodelist, index, node)` triples — needed for sibling-context checks like `(\cite{...})` bracket-in-bracket detection.
- `_is_inside_verbatim(node_path) -> bool`: given a parent-chain path (list of ancestors), returns True if any ancestor is a verbatim-class environment (`verbatim`, `Verbatim`, `Code`, `CodeInput`, `CodeOutput`, `Sinput`, `Soutput`, `Scode`, `Schunk`, `CodeChunk`) or a verbatim-class macro (`\verb`, `\code`). Used by §II-carve-out rules like `JSS-CITE-004` (hardcoded citations) and `JSS-HOUSE-001` (e.g./i.e. comma) that scan char content.
- `_is_inside_comment(node) -> bool`: True for `LatexCommentNode` descendants.

**Rationale**:
- §X small-surface rule: each helper has a concrete use case. `_walk` has 15+ callers (every category). `_macro_args_text` has ~30 callers (every rule that matches a macro). `_is_inside_verbatim` has ~5 callers (the code-aware rules). Zero speculative helpers.
- `_helpers.py` lives under `rules/` not at the journal level because the helpers are rule-authoring-specific, tuned to the pylatexenc AST shape; they don't belong next to `terms.py` (which is data).
- Private naming (`_helpers`) signals "internal to the rules package" without publishing an API that third-party journals might rely on (Constitution §IV boundary).

**Alternatives considered**:
- **Per-module helper copy-paste**: repeats ~50 lines across 15 modules, violates DRY, and creates drift risk during bug fixes.
- **Top-level `texlint.core.ast_utils`**: promotes walker helpers to core. Rejected per §IV — JSS-specific rules should not contaminate the core.
- **Inline helpers per category**: acceptable for a single-use helper but the walker and macro-arg extractor are universally reused. Factored out.

**Consequence**: `_helpers.py` gets its own 100% branch-coverage test at `tests/unit/journals/jss/rules/test_helpers.py` (not per-category, since helpers are shared). Individual rule-module tests assume the helpers are correct and focus on rule logic.

## 3. Rule metadata sourcing: build-time codegen from `catalogue.yaml`

**Decision**: `tools/generate_catalogue_data.py` reads `specs/003-jss-rule-catalogue/catalogue.yaml` and emits `src/texlint/journals/jss/_catalogue_data.py` — a Python module exporting a flat `RULES: Mapping[str, Mapping[str, object]]` keyed by `rule_id` plus `RETIRED_RULE_IDS: frozenset[str]`. The generated file is **committed**; runtime has zero YAML parse cost. A CI test (`test_catalogue_data_fresh.py`) regenerates in-memory and compares to the committed file — drift fails CI.

**Rationale**:
- User's `/speckit.plan` input asked for `Rule.description` to be pulled from the catalogue, not duplicated in code. Codegen gives the single-source-of-truth property without either (a) duplicating descriptions inline or (b) adding PyYAML as a runtime dependency.
- Same pattern as spec 003's `catalogue.md` renderer: YAML is source of truth, generated artefact is committed, CI drift-check refuses stale regenerations.
- Runtime surface stays small: `from texlint.journals.jss._catalogue_data import RULES` is a cheap Python import with no I/O.
- Catalogue-consistency check (FR-004) becomes trivial: iterate `RULES` and verify every entry has a matching registered `Rule` object; iterate `JSSJournal.categories()` and verify every rule appears in `RULES`; verify `Rule.id not in RETIRED_RULE_IDS`. All three checks are O(N) over dicts/sets.

**Generated file shape**:

```python
# AUTO-GENERATED from specs/003-jss-rule-catalogue/catalogue.yaml.
# Do not edit by hand; run `python -m tools.generate_catalogue_data`.

from __future__ import annotations
from types import MappingProxyType
from typing import Mapping

from texlint.api import Severity

# One entry per active rule in catalogue.yaml.
RULES: Mapping[str, Mapping[str, object]] = MappingProxyType({
    "JSS-PRE-001": MappingProxyType({
        "category": "preamble",
        "severity": Severity.ERROR,
        "message_template": "Document class must be jss with a valid class option (article, codesnippet, bookreview, softwarereview)",
        "authority": "jss_cls",
        "authority_ref": "jss.cls:37",
        "inspects": ("tex_files",),
        "auto_fixable": False,
    }),
    # ... 57 more entries ...
})

RETIRED_RULE_IDS: frozenset[str] = frozenset({"JSS-CITE-001", "JSS-ABBR-002"})

# Rollout order (from catalogue.yaml top-level categories field):
ROLLOUT_ORDER: tuple[str, ...] = (
    "citations", "references", "bibtex", "preamble", "structure", "markup",
    "crossrefs", "code_style", "code_width", "naming", "operators",
    "abbreviations", "house_style", "typography", "capitalization",
)
```

Rule modules consume it:

```python
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

_META = _catalogue_data.RULES["JSS-CITE-002"]

def check_jss_cite_002(doc, cfg):
    for tex in doc.tex_files:
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if _condition(node, parent, idx):
                line, col = _helpers._lineno_col(tex, node.pos)
                yield Violation(
                    file=tex.path, line=line, column=col,
                    rule_id="JSS-CITE-002",
                    severity=_META["severity"],
                    message=_META["message_template"],
                    suggestion="Add a citation within the same paragraph.",
                    fix=None,
                )

jss_cite_002 = Rule(
    id="JSS-CITE-002",
    category=_META["category"],
    severity=_META["severity"],
    message_template=_META["message_template"],
    authority=_META["authority"],
    check=check_jss_cite_002,
    formats=None,
)
```

The `Rule` kwargs are redundant-by-design — every field sourced from `_META` guarantees no drift. The CI test in `contracts/catalogue-consistency.md` is belt-and-braces.

**Alternatives considered**:
- **Runtime YAML parse**: adds PyYAML as runtime dep. Rejected — spec 003 FR-003 pinned "no new runtime deps" and this spec inherits that.
- **Hard-code descriptions + CI drift check**: what spec 003's plan originally proposed. Duplicates text; requires reviewer vigilance on every PR. Rejected for the same reason the `/speckit.plan` input asked for the pulled-from-catalogue approach.
- **Codegen at install time (via `hatchling` build hook)**: cleaner in principle but complicates `pip install -e` dev workflow. Current approach (codegen is a manual `python -m tools.generate_catalogue_data` step, CI verifies freshness) is simpler and matches the `render_catalogue.py` pattern already established.

**Consequence**: two new CI tests. `test_catalogue_registration.py` (FR-004: active-set and retired-set disjointness) and `test_catalogue_data_fresh.py` (codegen-drift detection). Both are O(N) over the 58-entry rules dict.

## 4. AI skip-list pre-population (Session 2026-04-23 Q3 answer)

**Decision**: `eval/review-skip-list.toml` ships with **14 rule ids** pre-populated at the first spec-004 category PR.

**Pre-populated entries**:
- **Regex + context masks** (1): `JSS-CITE-004`.
- **English-morphology heuristics** (4): `JSS-CAP-001`, `JSS-CAP-002`, `JSS-CAP-003`, `JSS-CAP-004`.
- **LaTeX-macro substring patterns** (3): `JSS-MARKUP-001`, `JSS-CODE-003`, `JSS-HOUSE-001`.
- **Structural additions** (6, added per Session 2026-04-23 Q3): `JSS-REFS-002`, `JSS-REFS-006`, `JSS-ABBR-001`, `JSS-OPER-001`, `JSS-REFS-005`, `JSS-CAP-004` (already counted).

The CAP-004 entry appears in both the English-morphology and structural-additions lists; the effective set is 14 ids (deduplicated).

**Rationale**: AI labelling (Qwen3) was documented in spec 002 as unreliable on regex-over-English-morphology patterns. Pre-populating skips the known-unreliable AI pass entirely and routes these rules directly to human review, avoiding a discarded-labels round.

**Schema** (covered in `contracts/ai-skip-list.md`):

```toml
# eval/review-skip-list.toml — rules AI-assisted review must skip.
# Maintained across spec 002 (harness) and spec 004 (rule rollout).

[[rules]]
rule_id = "JSS-CITE-004"
reason = "Regex-over-English-morphology; Qwen3 rubber-stamps matches. Reviewed 2026-04-23."
added_in_spec = "004"

[[rules]]
rule_id = "JSS-CAP-001"
reason = "Title-case heuristic; Qwen3 blind spot per spec 002 notes."
added_in_spec = "004"

# ...
```

**Removal policy**: entries MUST NOT be removed without a documented rationale in the removing PR's description (spec 004 Session 2026-04-23 Q3 note). The corresponding unit test (`tests/eval/test_skip_list_entries.py`) asserts the 14 expected entries are present at the close of spec 004.

## 5. Category grouping allowlist (Session 2026-04-23 Q1 answer)

**Decision**: default one PR per category; the allowlist permitting small groups (≤3 categories) of closely-related categories is **documented in `tasks.md`** as the following groups:

| Group | Categories | Rationale |
|---|---|---|
| Solo | `citations` | Retrofits `cite_001_emph.py` (→ DELETE); plus 3 new rules. No sibling shared dependencies. |
| **`bib-content-and-mechanics`** | `references + bibtex` | Both inspect `bib_files` via bibtexparser; share BibTeX-entry iteration patterns. |
| Solo | `preamble` | 8 rules; largest category, justifies its own PR. |
| Solo | `structure` | Section-and-document-shape rules; distinct from markup. |
| **`text-markup-and-canon`** | `markup + naming` | Both consume `terms.py` (languages and package names). Markup wraps `\proglang{}` / `\pkg{}` / `\code{}`; naming checks canonical spellings referenced by those wrappers. |
| Solo | `crossrefs` | \label/\ref rules; standalone AST walker. |
| Solo | `code_style` | Prose-code rules (spacing, comments, quoting). |
| Solo | `code_width` | Retrofits `src_001_width.py`; single rule. |
| Solo | `operators` | Math-notation rules; ties, transpose, jss.cls shortcuts. |
| Solo | `abbreviations` | Single rule (ABBR-001 only; ABBR-002 retired). |
| Solo | `house_style` | Miscellaneous style directives; independent. |
| **`caption-and-case`** | `typography + capitalization` | Both inspect captions (TYPO-001/002/003/004, CAP-003) and share a sentence-style helper. |

Expected total: **12 PRs** (8 solo + 3 grouped + 1 retrofit-cleanup tracker). Order follows the rollout sequence with groups merging at the position of their earliest category.

**Rationale**: grouping is opt-in per concrete shared surface area (bibtex parser patterns, terms.py consumer, caption walker). Not based on arbitrary preferences. Each group's PR satisfies FR-004 (catalogue consistency), FR-012 (precision gate), FR-010 (100% coverage) independently per contained category.

## 6. Severity.INFO enum extension

**Decision**: add `Severity.INFO = "info"` to `texlint.api.Severity`. Land in the first spec-004 foundational PR (Phase 2 setup), before any info-severity rule's category ships.

**Rationale**:
- Catalogue has 4 info-severity rules (JSS-REFS-003, JSS-XREF-002, JSS-XREF-004, JSS-HOUSE-003). Those rules cannot register a `Rule(..., severity=Severity.INFO)` without the enum value existing.
- API-additive: a new enum value doesn't break string-comparison consumers; exhaustive `match` statements on the enum (type-checked) will fail loudly at the consumer side if they don't handle INFO, which is the desired signal (downstream consumers must audit).
- Downstream audit surface: output renderers (`src/texlint/output/`), `eval-jss report`, `eval-jss human-review` (which presents severity alongside violation text). A Phase 2 task sweeps each to confirm INFO is handled — default: treat INFO same as WARNING in reviewer/author terminal output, distinguish in `eval-jss report` as a separate row.

**Alternatives considered**:
- **Map `info` → `warning` in codegen**: the catalogue says `severity: info` but the Rule gets WARNING. Discards a deliberate reviewer judgement. Rejected.
- **Use a string at the Rule level instead of an enum**: breaks type safety. Rejected.

**Consequence**: one foundational task in `tasks.md` titled "Add Severity.INFO and sweep downstream consumers" — estimated ≤30 minutes of work, lands before any category PR.

## 7. `scripts/eval-category.sh` wrapper

**Decision**: a small shell script wraps the per-category precision-gate sequence:

```bash
#!/usr/bin/env bash
# scripts/eval-category.sh — run the per-category precision gate.
# Usage: scripts/eval-category.sh <CATEGORY>
#   e.g., scripts/eval-category.sh citations

set -euo pipefail
CATEGORY="${1:?category required}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
cd "$ROOT"

"$SCRIPT_DIR/vtest.sh" "tests/unit/rules/test_${CATEGORY}.py" \
    "--cov=src/texlint/journals/jss/rules/${CATEGORY}" \
    "--cov-branch" "--cov-fail-under=100"
.venv/bin/eval-jss scan
.venv/bin/eval-jss human-review
.venv/bin/eval-jss report --grep="JSS-$(echo "$CATEGORY" | tr '[:lower:]' '[:upper:]' | tr -d '_' | cut -c1-6)-"
```

**Rationale**: the four-command sequence is part of every category PR's `tasks.md`; wrapping removes ceremony and makes the command memorable. The `--grep` filter keeps the report output focused on the category's rules (the `JSS-<CAT>-` prefix derivation is a best-effort string munge that covers the 15 categories' prefixes; exact prefixes live in `tools/_catalogue_validate.py`'s `CATEGORY_PREFIX` map if the script needs to be exact).

**Alternative considered**: let each category PR author remember the 4-command sequence. Rejected — script is 10 lines, and the user-supplied `/speckit.plan` input explicitly asks for it.

## 8. `terms.py` vs `terms.toml` (deferred)

**Decision**: keep `terms.py` as the Python-source-of-truth form that spec 003 shipped. Do **not** migrate to `terms.toml` in this spec.

**Rationale**:
- Spec 003's `terms.py` has ~30 entries total across `LANGUAGES`, `R_PACKAGES`, and `CANONICAL`. Migration to TOML buys some review-friendliness in diffs but adds a parse step and a second source of truth.
- The user's `/speckit.plan` input mentioned `terms.toml` as a "keep the term data in a separate terms.toml under the package and parse once — easier to review via git diff than a 200-line Python set literal" — but the literal is currently ~50 lines, not 200. Threshold not crossed.
- Migration is cheap to do later if terms grow past ~100 entries. Deferring keeps scope contained.

**Consequence**: `terms.py` remains as-is. New terms added during spec 004 rule implementation land in `terms.py` (via its consuming category's PR per spec 003 FR-022 / open-consumer policy).

## Summary of drift reconciliations carried into `plan.md`

1. Check callable naming: **public** `check_<rule_id_suffix>` (supersedes spec 003's private `_check_jss_<category>_NNN`).
2. Rule metadata sourcing: **build-time codegen** from catalogue (supersedes spec 003's hard-code + CI check).
3. **`Severity.INFO` enum extension**: spec-001 amendment landed in spec 004's Phase 2 (matches the pattern from spec 003's `retired_rule_ids` amendment).

No outstanding `NEEDS CLARIFICATION` items at Phase 0 exit.
