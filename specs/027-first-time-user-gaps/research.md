# Research: Release 1.2.0 — first-time-user gaps

**Phase**: 0 · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)
**Written**: 2026-09-06, after three external review rounds. Records every
decision with the alternatives that were measured or argued and rejected.
Numbers come from read-only experiments run against the Python reference
engine (`.venv-host/bin/jss-lint --output json --no-resolve`); the scripts
are reproducible from the descriptions in §5.

## 1. Decisions

### D1 — Baseline key: `(rule_id, path, message, suggestion)` → count

**Chosen** because it needs no change to `Violation` or the JSON
violation shape (both engines, plus the vendored R crate), it is portable
(paths relative to the baseline file), and it measured best (§5.1–5.2).

**Rejected**
- *Line-based key* `(rule_id, path, line)`: survives 1 %, 16 %, 54 % across
  the three real jss5342 revision rounds. Useless under drift.
- *Message-only key* `(rule_id, path, message)` (the interview's first
  choice): same survival for persisting findings, but JSS messages are the
  rule descriptions and quote nothing, so 80 findings collapse to 12 keys;
  on the first real round it masked 8 of 18 genuinely new findings behind
  the counts of same-rule findings the author had fixed elsewhere in the
  same file.
- *Source-line hash on `Violation`* (interview alternative): a new field in
  both engines and the vendored crate, and it dies on any edit of the line.
- *Catalogue-flagged source-line context for non-prose rules* (rev-3
  alternative to item S, 1.5 d): raised distinct keys 49 → 77 on jss5342
  but re-keyed 5 of 44 persisting findings in the heaviest round; leaves
  the generic messages in place. Rejected by the maintainer in favour of
  item S (D10).

### D2 — One suppression hook; Rust inline ignores inside 1.2.0

The Rust engine never implemented `% jss-lint: ignore`
(`rust/jsslint-core/src/engine.rs:721-723`), a live §XIII violation, and
the baseline needs the same pre-bookkeeping seam. The reviewer proposed
shipping the port as 1.1.1; the maintainer chose to keep it in 1.2.0 as
its own PR with its own CHANGELOG *Fixed* entry so regressions stay
attributable. Two latent Python bugs are fixed first (`.Rmd` directive
lines are fragment-relative; `str.splitlines()` splits on `\f`/`\v`/`\x85`).

### D3 — Recall display: three states, threshold 10

`eval/recall.py::partition_by_plants(min_plants=10)` and the paper already
pool rules with fewer than 10 plants; showing 0.50 on n = 2 would read as a
measurement. Rejected: two states (percentage for any n ≥ 1); category-only
display in the tool.

### D4 — Date-stamped `ruleset_version`, fingerprint incl. wording

Rejected: "rule set = tool MAJOR.MINOR" (nothing guards a rule-set change
slipping into a patch); an independent semver (two semvers side by side).
The reviewer noted that excluding message wording from the fingerprint
lets a minor reword rules with no version signal while baselines key on
that wording; hence `messages.json`, generated from the per-rule
violation fixtures (61 of 62 rules have one), enters the fingerprint.

### D5 — `--fix` never touches git

Spec 008 decided this explicitly. Kept because fixes are atomic and
re-verified (§VII), `--dry-run` already exists as the preview path, many
manuscripts live outside git (Overleaf, Dropbox), the R/PyO3/WASM bindings
could not honour a git check, and a `git status` subprocess would add
environment-dependent output to streams the parity harness compares.
Rejected: stderr warning when dirty; refuse unless `--force`.

### D6 — Overleaf: docs + browser zip drop; CLI zip deferred

`DecompressionStream("deflate-raw")` is native in current browsers, so the
zip reader is ~120 lines of JS with no dependency and no WASM change. CLI
zip (Python `zipfile`, Rust `zip` crate at the CLI layer) is ~2 days for
"one `unzip` command" and is deferred.

### D7 — Scope: everything in 1.2.0; lever is coverage

After rev 2 the colour + zip cut saves only 3 days; the separable, judgement
-heavy item is coverage (5 d). The maintainer keeps it in.

### D8 — Coverage surfaces

Reviewer block + JSON block + `coverage` subcommand + author-footer pointer.
Rejected: no subcommand (list only in reviewer mode and docs); docs only.

### D9 — Colour: plain-stream parity only

The brief asked for identical escape bytes across engines. The reviewer
argued, and the maintainer agreed, that nobody diffs coloured output
between engines; the invariant that matters is the plain stream. Python
lets rich emit the styles already in its markup; Rust styles cells at
render time and writes through `anstream` with a choice *we* compute.
Cross-engine tests strip SGR and compare, and both CLIs share one decision
function (`--color` > `NO_COLOR` > `CLICOLOR_FORCE` > TOML > auto). The
rejected design (post-render line parser with cell-position heuristics,
shared golden fixtures, hand-rolled kernel32 VT enabling in both engines)
cost 4 days and broke on every table-layout change.

### D10 — Item S: token-specific suggestions, 10 rules, before baselines

`suggestion` is a baseline-key component (D1) and a fingerprint input
(D4), so sharpening generic suggestions after 1.2.0 would invalidate every
baseline entry of those rules. The reviewer asked for the change before
baselines exist and for a prototype before committing the effort. Scope
and evidence in §3–§5.

### D11 — Aggregate recall floor 0.78, ratcheted

Spec 017 FR-011 set 0.70 for the 10-paper corpus and deferred the ratchet
to "an explicit decision in a future spec". Shipped recall is 0.807 on
1 967 plants; 0.78 leaves ~50 false negatives of slack so adding a paper
with a weak rule does not fail CI, while the per-rule ≤ 0.05 regression
check keeps catching the sharp case. The release checklist ratchets the
floor to `floor(snapshot − 0.03, 2 dp)`.

### Maintainer decisions that overrode reviewer suggestions

- Inline-ignore fix stays in 1.2.0 (not 1.1.1).
- Author footer stays on stdout: the text report is the report; an empty
  saved report on a clean run is the unearned all-clear P0-A removes; the
  CLI contract's CI signal is the exit code.

## 2. WIDTH-001 decision (rev 4)

`JSS-WIDTH-001` is the highest-volume rule (1 257 of 3 411 findings in the
30-paper audit) and every finding carries the same suggestion. Three keys
were measured:

| WIDTH-001 key | 30-paper audit: duplicate findings remaining of 1 256 | jss5342 initial → resubmission: persisting findings re-keyed |
|---|---|---|
| generic (rev-2 key) | 1 256 | 0 of 3 |
| enclosing chunk name / code environment | 1 251 | 2 of 3 |
| first 30 chars of the line (rev-3 recipe) | not measured on audit | 2 of 3 |

Long lines cluster inside one chunk or environment, so chunk keying buys
almost no specificity (5 of 1 256 duplicates removed) and still churned on
the real rounds because the chunks themselves were reorganised. Line-prefix
keying is the reviewer's original objection made concrete: it changes on
any edit of the line. **Decision: WIDTH-001 stays generic.** Its findings
within a file are interchangeable, masking on this rule is accepted and
documented as limit 1 of the baseline contract, and the practical reading
is "the file still has N over-wide lines" — which is how authors fix them
anyway (reflow a chunk, re-run).

## 3. Item S — prototype and final scope (rev 4)

### Method

Instead of a throwaway code branch, each proposed identifier was derived
from `(file, line, column)` plus the source text — the same information
the rule has at emission time — and appended to the current suggestion.
This reproduces the *key behaviour* of item S without touching a rule
module. Identifiers: BibTeX entry key (scan back to `@type{key,`), code
fragment (±8 chars around the reported column), comment text, equation
`\label` or first-body-line head, caption or section-title argument,
referenced label, cite key. Limitation: for `CITE-003` the cite key was
taken from the line rather than the matched node, so its re-key count is
an upper bound.

### jss5342 real rounds (matched / stale / new; distinct keys on the older version; re-keyed persisting findings)

| Transition | rev-2 key | S, all candidate rules, WIDTH generic |
|---|---|---|
| initial → resubmission | 26 / 74 / 18 · 49 keys · 0 | 23 / 77 / 21 · **80 keys** · **4** (3 CITE-003, 1 CODE-003) |
| resubmission → resubmission2 | 26 / 18 / 2 · 15 keys · 0 | 24 / 20 / 4 · 33 keys · 3 (2 CITE-003, 1 CODE-001) |
| resubmission2 → final | 19 / 9 / 0 · 14 keys · 0 | 19 / 9 / 0 · 25 keys · 0 |

Prediction check: distinct keys were predicted to rise "from 49 towards
~77 with fewer false-new" than the rejected context variant (77 keys, 5
re-keyed). Measured: 80 keys, 4 re-keyed. The prediction holds; the
robustness advantage over the context variant is small on this sample,
and S's remaining case is specificity plus better author-facing messages.

### 30-paper audit — masking S can remove, by rule (duplicate findings, rev-2 key → S key)

| Rule | findings | dup rev-2 | dup S | removed | cumulative |
|---|---|---|---|---|---|
| CODE-003 | 396 | 388 | 247 | 141 | 27 % |
| OPER-003 | 91 | 84 | 6 | 78 | 43 % |
| TYPO-001 | 58 | 58 | 2 | 56 | 54 % |
| REFS-004 | 86 | 47 | 0 | 47 | 63 % |
| CAP-002 | 45 | 36 | 2 | 34 | 69 % |
| CODE-001 | 38 | 34 | 5 | 29 | 75 % |
| XREF-004 | 88 | 32 | 4 | 28 | 80 % |
| REFS-007 | 31 | 28 | 0 | 28 | 86 % |
| XREF-002 | 80 | 77 | 52 | 25 | 91 % |
| CITE-003 | 30 | 25 | 8 | 17 | 94 % |
| REFS-006 | 117 | 11 | 0 | 11 | 96 % |
| NAME-002 | 19 | 7 | 0 | 7 | 97 % |
| WIDTH-001 | 1 257 | 1 256 | 1 251 | 5 | 98 % |
| REFS-005, HOUSE-002, TYPO-004, XREF-006, BIBTEX-003/004 | ≤ 6 each | ≤ 4 each | — | ≤ 4 each | 100 % |

### Final scope

**In 1.2.0 (10 rules, 4 days)**: `CODE-003`, `OPER-003`, `TYPO-001`,
`REFS-004`, `CAP-002`, `CODE-001`, `XREF-004`, `REFS-007`, `XREF-002`,
`CITE-003` — 94 % of the removable masking. **Deferred** (follow-ups, ≤ 6 %
combined): entry-key additions for `REFS-005`, `REFS-006`, `NAME-002`,
`HOUSE-002`, `BIBTEX-003/004/005`; `TYPO-004`; `XREF-006`. **Generic by
decision**: `WIDTH-001` (§2). **Unchanged, inherently repeating token**:
`MARKUP-001/003`, `OPER-001/004`, `CODE-002`, `REFS-003`.

The ≥ 80 %-generic threshold was the wrong cut; the volume cut is the
right one, exactly as the reviewer suspected. Deferring the tail has no
sequencing cost: those rules' suggestions are unchanged in 1.2.0, so a
later rewording follows the ordinary rule-set-bump path (D4) and affects
only their own entries.

## 4. Coverage curation — measured gap

`specs/003-jss-rule-catalogue/checklists/rule-catalogue-review.md` §1.1–1.4
holds 146 rows (jss.cls 40, article.tex 24, style guide 60, author
instructions 22). Seven rows still credit the retired `JSS-CITE-001`,
`JSS-ABBR-002`, `JSS-REFS-002`, `JSS-CAP-003`. Fifteen active rules appear
in no row: `BIBTEX-003/004/005`, `OPER-004`, `PROJECT-001/002`,
`REFS-001/003/005/006/007`, `XREF-004/005/006/007`. Curation is therefore
2.5 days (scripted migration 0.5; directives for the 15 unclaimed rules
1; re-judging retired credits and partials 0.5; validator 0.5), and item A
is 11.5 days (recall 6.5, coverage 5), not 8.

## 5. Baseline-key evidence (rev 2) — reproduction notes

- **Simulated rounds** (five corpus papers, 259 findings): copy each
  paper's lintable files to a scratch directory; lint; apply three
  deterministic edits (insert a paragraph after half the `\section`
  lines; append a clause and swap one word on 25 % of prose lines outside
  code environments; the same plus edits on half of the flagged prose
  lines); lint again; multiset survival of the key. Results: 100 % / 100 %
  / 99.6 % for `(rule, path, message)`; 258 of 259 messages contain no
  quoted source text.
- **Real rounds** (`examples/jss5342-versions`, four versions, main file
  renamed twice): copy each version's `.Rnw` as `main.Rnw` beside
  `refs.bib` so the path component is comparable; lint; multiset survival
  between consecutive versions for three keys. Results in §3 above and in
  plan.md §5.7. Renames invalidate every entry of the renamed file — hence
  limit 2 of the baseline contract.

## 6. Other rejected alternatives (with reasons)

| Alternative | Rejected because |
|---|---|
| SARIF `baselineState` for baselined results | Marking rather than omitting would post baselined findings as PR review comments through the Action and require jq changes; omission makes the existing gate correct for free. Recorded as future work. |
| `Rule.recall` field stamped like `confidence` | No engine decision reads it; a §X field consumed only by renderers. Journal-level `metadata()` → report instead. |
| YAML recall snapshot | Generated files in the catalogue directory are JSON (`terms.json`, `latex-macro-specs.json`); `serde_json` is already a build dependency. |
| `created` timestamp in the baseline file | Makes `--update-baseline` non-byte-identical across engines and runs; git records the date. |
| Auto-discovery of `.jss-lint-baseline.json` | Surprising in CI; WASM has no filesystem; explicit flag or TOML key only. |
| Per-rule guide-edition pinning in catalogue.yaml | The prose guide has no edition; the only dated authority is jss.cls 3.3 (2021-05-23). Catalogue-level edition plus per-source fetch dates in `guide-coverage.yaml` `sources:` is the honest equivalent. |
| Recall floor left at 0.70 | Ten points of slack under a number printed in every author footer. |
| Colour with identical escape bytes | See D9. |
| 1.1.1 patch release for inline ignores | Maintainer decision: one release cycle across seven channels for a fix that ships weeks later anyway; attributed by its own PR/CHANGELOG entry instead. |
| Author footer on stderr | Maintainer decision: see above. |
