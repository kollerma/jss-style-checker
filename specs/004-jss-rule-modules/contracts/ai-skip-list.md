# Contract: `eval/review-skip-list.toml`

**File**: `eval/review-skip-list.toml` (shipped in spec 002, extended here per spec 004 FR-023).
**Owner**: jointly maintained by spec 002 (AI-review harness) and spec 004 (rule rollout).
**Consumed by**: `eval/review.py` (spec 002 `eval-jss review` subcommand).

## Schema

```toml
# eval/review-skip-list.toml — AI-assisted review skips these rule ids.
#
# Entries here bypass Qwen3 labelling and route directly to
# `eval-jss human-review`. Used for rules where AI labelling is known
# unreliable (regex-over-English-morphology, macro-substring heuristics,
# context-mask-sensitive patterns).
#
# Schema pinned by specs/004-jss-rule-modules/contracts/ai-skip-list.md.
# Removal policy: entries MUST NOT be removed without a rationale in the
# removing PR's description (spec 004 Session 2026-04-23 Q3).

[[rules]]
rule_id       = "<JSS-CAT-NNN>"
reason        = "<one-line rationale for AI unreliability>"
added_in_spec = "<NNN>"       # e.g., "004"; historical tracking
```

### Per-entry fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `rule_id` | str | yes | Must match `^JSS-[A-Z]+-\d{3}$` and appear in `_catalogue_data.RULES` (not retired). |
| `reason` | str | yes | One-line rationale. Future readers should understand why AI review is unreliable for this rule without reading the rule's implementation. |
| `added_in_spec` | str | yes | Spec number (`"002"`, `"004"`, ...) that first added this entry. Enables history at a glance. |

## Invariants (enforced by `tests/eval/test_skip_list_entries.py`)

| # | Invariant | Rationale |
|---|---|---|
| S-1 | Every `rule_id` appears in `_catalogue_data.RULES` (active set). | A skip-list entry for a nonexistent or retired rule is dead configuration. |
| S-2 | `rule_id`s are unique within the file (no duplicates). | The skip-list is a set, not a multiset. |
| S-3 | Every entry has non-empty `reason` and `added_in_spec`. | Audit trail is mandatory, not decorative. |
| S-4 | At the close of spec 004, the file contains **at least** the 14 pre-populated entries listed in §Spec-004 pre-population. | Spec 004 FR-023. |

## Spec-004 pre-population (14 rules)

At the end of spec 004's rollout, the following entries MUST be present in `eval/review-skip-list.toml`. Each entry lands in the PR of the category that owns the rule (so, e.g., `JSS-CITE-004` is added in the `citations`-category PR).

```toml
[[rules]]
rule_id       = "JSS-CITE-004"
reason        = "Regex-over-prose with code/verbatim masking; AI labeller rubber-stamps matches."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-MARKUP-001"
reason        = "Language-name substring match; AI labeller lacks context for math-mode / Pascal / initials."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-REFS-002"
reason        = "BibTeX title-case tight heuristic; Qwen3 rubber-stamps 'looks-like-a-title' cases (spec 002 note)."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-REFS-005"
reason        = "Journal-abbreviation heuristic over English morphology; AI labeller unreliable."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-REFS-006"
reason        = "BibTeX title-case loose heuristic; same Qwen3 blind spot as REFS-002."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-CAP-001"
reason        = "Title-style heuristic; AI labeller lacks principal-word dictionary."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-CAP-002"
reason        = "Sentence-style heuristic on section titles; Qwen3 blind spot."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-CAP-003"
reason        = "Sentence-style heuristic on captions; Qwen3 blind spot."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-CAP-004"
reason        = "Keyword sentence-case heuristic; short fields with limited context — AI unreliable."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-ABBR-001"
reason        = "Uppercase-abbreviation pattern; regex-over-morphology, AI rubber-stamps."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-CODE-003"
reason        = "Spacing-around-operators regex; LaTeX macro substring heuristic; Qwen3 blind spot."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-OPER-001"
reason        = "Symbol-tie regex ($p$~value); character-class match, AI labeller unreliable."
added_in_spec = "004"

[[rules]]
rule_id       = "JSS-HOUSE-001"
reason        = "e.g./i.e.-comma regex; LaTeX macro substring heuristic."
added_in_spec = "004"
```

That's 13 entries. The 14th (per `research.md` §4's "14 rules total") is `JSS-CAP-004` — already listed above; the enumeration included it twice (English-morphology bucket and structural-additions bucket); dedup to 13 **unique** entries. Rehecking against `research.md`:

> FR-023 minimum 8: CITE-004, CAP-001, CAP-002, CAP-003, MARKUP-001, CODE-003, HOUSE-001, *and one more…*

Actually recounting the FR-023 minimum: `CITE-004, CAP-001, CAP-002, CAP-003, MARKUP-001, CODE-003, HOUSE-001` = 7, not 8. Plus the 6 structural additions (`REFS-002, REFS-006, ABBR-001, OPER-001, CAP-004, REFS-005`) = 13 total. The original "14" count in research.md double-counted CAP-004 (it's both English-morphology and structural-addition). **Corrected total: 13 unique entries**.

This contract pins the list at **13 entries**; update spec.md's FR-023 and research.md's §4 accordingly if the discrepancy matters (it's an off-by-one in the count, not in the listing).

## Adding an entry

During a category PR, if a new rule's violations prove AI-unreliable on the corpus:

1. Add a `[[rules]]` block to `eval/review-skip-list.toml` with `rule_id`, `reason`, and `added_in_spec = "004"`.
2. Reference the entry in the PR description's precision-gate report: "Added to skip-list because corpus AI-labelling accuracy was <60% after first pass".
3. Proceed with `eval-jss human-review` for those violations.

## Removing an entry

Removal MUST include in the removing PR's description:

- Which rule id is being removed from the skip-list.
- Why (e.g., "rule refinement narrowed the match scope; AI labelling is now reliable").
- Evidence (e.g., "corpus pass of 50 labelled violations shows AI agreement with human labels ≥95%").

Without this rationale the CI test `test_skip_list_entries.py` may not fail (the test just checks the minimum-set presence), but reviewer discipline is the enforcement.
