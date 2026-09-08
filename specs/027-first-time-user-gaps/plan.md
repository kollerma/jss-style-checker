# Implementation Plan: Release 1.2.0 — first-time-user gaps

**Feature Branch**: `027-first-time-user-gaps`
**Created**: 2026-09-06 · **Revised**: 2026-09-06, rev 4 (after the third
and final external review round)
**Status**: Draft (not committed, no code written)
**Input**: Release-1.2.0 scope brief (P0-A recall transparency, P0-B
baseline mode, P1-C fix safety, P1-D version and rule-set provenance,
P1-F coloured terminal output, P2-E Overleaf) plus one addition raised in
the planning interview: tell authors which parts of the style guide the
tool does **not** check.

This document is the plan deliverable. The companion artifacts in this
directory (`spec.md`, `research.md`, `data-model.md`, `contracts/`,
`quickstart.md`, `checklists/`) were written after the third review round;
`research.md` §2–§3 carries the WIDTH-001 decision and the item-S
prototype that fixed S's final scope.

### Revision 4 — third review round (final)

| Review point | Outcome |
|---|---|
| `WIDTH-001` keyed on line content + measured width would churn on every edit of a long line — on the highest-volume rule (1 257 of 3 411 audited findings) | **Accepted.** Measured (research.md §2): chunk/environment keying removes 5 of 1 256 duplicates; line-prefix keying re-keyed 2 of 3 persisting findings on jss5342. **WIDTH-001 stays generic**; its masking is accepted and documented (§5.7 limit 1). |
| S's payoff was projected, not measured; prototype the top rules and consider a volume-based cut | **Done by simulation** (identifiers derived from position + source, no code branch; research.md §3). jss5342 initial → resubmission: distinct keys 49 → 80 (predicted ~77), 4 of 44 persisting findings re-keyed (vs 5 for the rejected context variant). Volume cut: **10 rules remove 94 % of the removable masking**; the bib-key tail and two rare rules defer. **S = 4 days** (was 6.5); release ≈ 31.5 days. |

### Revision 3 — second review round

| Review point | Outcome |
|---|---|
| Pull token-specific suggestions into 1.2.0: `suggestion` is now a key component and a fingerprint input, so sharpening those suggestions later invalidates every baseline touching those rules | **Accepted.** New item S (§5A): initially 16–18 rules at +6.5 days, landing **before** any baseline work so `messages.json` is generated once — *superseded by rev 4: 10 rules, 4 days*. A cheaper catalogue-flagged "source-line context" key was measured (§5.7) and rejected by the maintainer in favour of the reviewer's proposal. |
| Raise the aggregate recall floor from 0.70 | **Accepted.** Floor 0.78 now, ratcheted to shipped-snapshot − 0.03 at every release (§7.1). Spec 017 FR-011 explicitly deferred this ratchet to "a future spec"; this is it. |
| A's 8-day estimate not trusted; coverage curation is judgement, not typing; the scope lever is coverage, not colour | **Accepted.** Measured: 146 checklist rows, 15 active rules claimed by no row, 7 rows crediting retired rules. A re-estimated at 11.5 days (recall 6.5, coverage 5). Scope-cut section rewritten around coverage. Maintainer keeps coverage in 1.2.0. |

### Revision 2 — first review round (kept for the record)

| Review point | Outcome |
|---|---|
| Colour mispriced by the "identical escape bytes across engines" requirement | **Accepted.** Plain stream stays byte-identical; the colour *decision* is one identical function in both CLIs; escape bytes are per-engine, documented as a §XIII divergence. 4 → 1.5 days (§8). |
| Baseline key tied to prose that changes; run it empirically | **Run; the premise did not hold** (§5.7). Messages quote no source text. The real risk is keys too coarse, masking new findings. D1 amended to add `suggestion`. |
| Rewording breaks baselines with no version signal | **Accepted.** Message and suggestion text enter the fingerprint via `messages.json`; `docs/versions.md` states a minor bump may require `--update-baseline` (§4). |
| Count-multiset masking overstated in §13 | **Accepted** (§5.7, §13). |
| Split the inline-ignore parity fix into 1.1.1 | **Declined by the maintainer.** Own PR and CHANGELOG entry inside 1.2.0 (§5.2). |
| Author footer on stderr | **Declined by the maintainer** (§7.3). |
| Wire `eval-jss recall --gate` now | **Accepted** (§7.1). |

## 1. Context

1.1.0 ships across seven channels with byte-identical engines, but a
first-time author evaluating it for a real JSS submission hits these gaps:
precision is exposed everywhere (tiers, `--min-confidence`, badges) while
recall (80.7 %) is exposed nowhere actionable, so a clean run reads as an
all-clear it has not earned; nothing tells an author which parts of the
style guide are *not* checked; adopting the tool on an existing manuscript
yields hundreds of findings with no "accept current state, fail only on
new" mode; `--fix` rewrites the manuscript without saying what it did;
distribution versions have diverged (CRAN `1.1.0-2`, CTAN `1.1.0`,
`web/pkg` still `1.0.1`) with no rule-set provenance; terminal output is
uncoloured; and no channel reaches Overleaf.

Decisions (maintainer-confirmed, 2026-09-06):

| # | Decision |
|---|---|
| D1 | Baseline key = `(rule_id, path relative to the baseline file's dir, message, suggestion)` → occurrence count (rev 2). No `Violation`/JSON-violation change. |
| D2 | Rust gets inline `% jss-lint: ignore`; both suppressions share one pre-bookkeeping hook in both engines. Ships inside 1.2.0 as a separately attributed change. |
| D3 | Recall display: three states, threshold 10 plants — `measured` (integer %), `limited (n=K)`, `unmeasured`. Per-category pooled over the category's plants. |
| D4 | Date-stamped `ruleset_version` in catalogue.yaml with a fingerprint guard that also covers message and suggestion wording via `messages.json`. Patch = findings may only disappear; minor = new rules, rewording, severity/tier changes; major = retire/rename/JSON breaks. CI pins the tool minor; a minor bump may require `--update-baseline`. |
| D5 | `--fix`: no git interaction (spec 008 stands). Applied/skipped summary line in both CLIs; documented VCS expectation. |
| D6 | Overleaf: workflow docs + browser zip drop on native `DecompressionStream`; CLI zip deferred. |
| D7 | Scope: everything, three phases. **Rev 3: the scope lever is coverage (5 d), then colour + zip (3 d).** Maintainer keeps all of it in 1.2.0. |
| D8 | Coverage: `guide-coverage.yaml` beside the catalogue; "Not checked" block under the reviewer table (terminal + HTML); `coverage` block in JSON; new `jss-lint coverage` subcommand; one-line pointer in the author footer. |
| D9 | Colour: plain stream byte-identical; decision function identical; escape bytes per-engine best-effort, documented §XIII divergence (rev 2). |
| D10 | Token-specific suggestions ship in 1.2.0, before baseline work. **Rev 4: scope is the 10 rules in §5A (volume cut, 94 % of removable masking); `WIDTH-001` stays generic by decision; the bib-key tail, `TYPO-004`, `XREF-006` defer.** |
| D11 | **Rev 3.** Aggregate recall floor 0.78, ratcheted to shipped-snapshot − 0.03 at each release. |

Resolved by the planner (open to veto): JSON baseline file, no
auto-discovery; baselined findings hidden everywhere with a summary line;
TTY detection at the CLI layer; one `--version` block in both engines
differing only in the engine line; author-mode footer always printed on
stdout; per-rule guide-edition pinning rejected as infeasible (the prose
guide has no edition; see §2).

## 2. Already implemented, already decided, or in conflict

| Scope item | Finding | Effect |
|---|---|---|
| P1-C dry-run | `--fix --dry-run` unified diff exists in both engines (`src/texlint/core/fixer.py:290-295`, `rust/jsslint-core/src/fixer.rs:456-464`), parity-tested (`rust/jsslint-cli/tests/fix_parity.rs:151`); spec 008 FR-004. | P1-C = summary line + docs + git decision. |
| P1-C git | Spec 008 Edge Cases/Assumptions: "`--fix` proceeds as normal (the tool does not check git state)", "does not back up". | Kept (D5). |
| P0-B | Spec 016 reserved `--baseline` for a future spec (`specs/016-revision-diff/spec.md:15`, `quickstart.md:131`); its identity tuple exists in both engines (`src/texlint/diff.py:77-80`, `rust/jsslint-core/src/diff.rs:106-132`). | Honoured: a flag on the lint command, not a three-way diff. |
| P0-B | **Live parity gap**: Rust never implemented inline ignores (`rust/jsslint-core/src/engine.rs:721-723`); Python applies them before bookkeeping (`src/texlint/core/engine.py:342-364`). | Closed in P0-B (D2), own PR. |
| P0-B | **Two latent Python bugs** in `src/texlint/core/suppress.py`: `.Rmd` directives use fragment-relative lines (`rmd_parser.py:348-354` sets `source=fragment.source`) so a directive only works when the prose block starts at line 1; `directive_lines` uses `str.splitlines()` (`suppress.py:78`), which also splits on `\f`, `\v`, `\x85`, ` ` while the parsers count `\n` only. No `.Rmd` case in `tests/unit/core/test_suppress.py`. | Fix in Python first, then port. |
| S (rev 3) | Suggestion audit over 30 corpus papers (3,411 findings): the rules with a single generic suggestion across ≥ 80 % of occurrences are `WIDTH-001` (1 257 findings, 100 %), `CODE-003` (98 %), `OPER-003` (92 %), `XREF-002` (96 %), `TYPO-001` (100 %), `OPER-001` (91 %), `REFS-007` (90 %), `CODE-001` (89 %), `CITE-003` (83 %), `CAP-002` (80 %), `REFS-005` (80 %), `TYPO-004` (100 %); bib rules `REFS-004/006`, `NAME-002`, `BIBTEX-003/004`, `HOUSE-002` quote a word but not the entry key. `MARKUP-001/003`, `OPER-001/004`, `CODE-002` already quote a token that inherently repeats. | Item S (§5A). |
| P0-A | Recall data is already in the checked-in `eval/precision-history.db` (`recall_history`). 53/62 rules measured; 9 unmeasured (`JSS-BIBTEX-001, PRE-001, PRE-002, PRE-008, PROJECT-001, PROJECT-002, REFS-001, TYPO-002, XREF-003`); category `project` has zero plants. `eval/recall.py::partition_by_plants(min_plants=10)` already encodes the thin-rule policy. | Reused. |
| P0-A | Badge pin (`eval/badge.py:42,46`) and paper pin (`tools/generate_paper_stats.py:67-70`) have drifted; the recall gate (`eval/cli.py:598-622`: aggregate ≥ 0.70 hard-coded at `:601`, per-rule regression ≤ 0.05 vs the last recorded run) is not wired into CI. Spec 017 FR-011: "the threshold ratchets up … governed by an explicit decision in a future spec". | Badge pin reads the shipped snapshot; paper pin stays; gate wired at floor 0.78 (D11). |
| Coverage | The directive→rule matrix exists only as markdown (`specs/003-jss-rule-catalogue/checklists/rule-catalogue-review.md` §1.1–1.4). **Measured (rev 3)**: 146 rows (jss.cls 40, article.tex 24, style guide 60, author instructions 22); 7 rows credit the retired `JSS-CITE-001/ABBR-002/REFS-002/CAP-003`; **15 active rules appear in no row** (`BIBTEX-003/004/005, OPER-004, PROJECT-001/002, REFS-001/003/005/006/007, XREF-004/005/006/007`) and need directives written against the guide. | Promoted to validated YAML (D8); curation costed at 2.5 d. |
| P1-D | `--version` already diverges: `jss-lint, version 1.1.0` (click, `cli.py:225`) vs `jss-lint 1.1.0` (clap, `main.rs:80`). No rule-set version exists. Only dated authority: jss.cls 3.3 `\filedate` 2021-05-23 (`source_vendored_at`); the prose guide is undated, checklist records "Fetched 2026-04-23"; `docs/jss-guide/index.json` has no date/hash. | Per-rule pinning rejected; catalogue-level edition + per-source fetch dates. |
| P1-D | CTAN is not in the repo: a manually uploaded doc bundle whose every upload needs a new identifier; next is 1.2.0. CRAN is `1.1.0-2`. `web/pkg/package.json` says `1.0.1` (wasm-pack artifact). No workflow checks tag ↔ `VERSION`; `release-action.yml` needs `RELEASE_TAG_PAT`. | Release checklist + tag guard (§10). |
| P1-F | Nothing exists. Python hard-codes `force_terminal=False` (`src/texlint/output/terminal.py:112-115`) although its markup already carries `[red]`/`[bold]`/`[dim]` styles; Rust reimplements rich's non-TTY layout byte for byte (`rust/jsslint-core/src/terminal.rs:1-18`). No parity test sets `NO_COLOR`/`TERM`. VS Code extension uses `analyze()` (`vscode-extension/src/extension.ts:109`), never the terminal renderer. | Python colour is a constructor flag; Rust adds styles at render time; VS Code unaffected. |
| P2-E | Web app: `webkitdirectory` folder picker + multi-file input, renders `output: "html"` into an iframe (`web/app.js:51-60`, `web/index.html:95-97`). No zip, no drag-drop. | Greenfield, JS only. |
| Action | Composite; pip-installs the **Python** package; always `--output sarif`; discards exit 1 and re-derives failure from SARIF levels; no `--fail-on` passthrough; `comment-mode: pr-comment` advertised but unimplemented (`action/action.yml:104-128`). | Needs a `baseline` input; SARIF omission of baselined results makes the jq gate correct for free. |
| Hazards | `RawOverrides` is built by struct literal without `..Default::default()` in `rust/jsslint-wasm/src/lib.rs:50-69`, `rust/jsslint-py/src/lib.rs:55-71`, `r/jsslintr/src/rust/src/lib.rs:69-80`, `rust/jsslint-cli/src/main.rs:634-650` → adding config fields is a compile error in all four. `tests/integration/test_cli_json.py:35` asserts the exact top-level key set; `tests/integration/test_cli_author_terminal.py:79` asserts empty stdout on a clean run. `jsslint-core/Cargo.toml` has no `include` list. **Rev 3**: the SARIF goldens (`tests/fixtures/sarif/golden_*.sarif`) embed result message/suggestion text and must be regenerated after item S (`JSSLINT_REGEN_GOLDENS=1`); the precision-label restoration in `eval-jss iterate refresh` must be checked for message-keyed matching before suggestions change. | All updated in the same PRs; a `cargo package --list` guard is added. |
| Constitution | §IV smell: renderers lazily import `texlint.journals.jss._catalogue_data` (`terminal.py:30`, `json_output.py:35`, `sarif.py:170`, `html_output.py:45`). §XV: `ruleset_version` is data provenance in catalogue.yaml, not a suite version. **Rev 3**: item S touches rule modules, so §VIII (tests first) and §IX (100 % branch coverage) apply to it. | New metadata flows journal → report; no new lazy imports. Recorded in §14. |

## 3. Phases, ordering, dependencies, effort

| Phase | Items | Why this order | Effort |
|---|---|---|---|
| 1 — Provenance + adoption | **D** (catalogue keys, fingerprint, `--version`, version fns, `docs/versions.md`; `messages.json` generated last) → **S** (token-specific suggestions for 10 rules, both engines) → **B** (Python suppress fixes + Rust inline ignore as its own PR → shared hook → baseline → Action input) → **C** (fix summary + docs) | D is small and B and A stamp/print `ruleset_version`. **S must precede B** so no baseline is ever written against the old suggestions, and `messages.json` is generated once after S. B's first PR closes a live §XIII gap. | D 3.5 · S 4 · B 7.5 · C 1 = 16 d |
| 2 — Transparency | **A-recall** (snapshot, CI gate at 0.78, journal metadata, reviewer column, footer statement, JSON/SARIF/explain, docs) → **A-coverage** (YAML curation + validator, reviewer block, coverage JSON, `coverage` subcommand, footer pointer, catalogue section) | Depends on D's keys; lands on B's footer block. Coverage is the separable, judgement-heavy half. | A-recall 6.5 · A-coverage 5 = 11.5 d |
| 3 — Polish | **F** (colour) → **E** (Overleaf docs + browser zip) | F touches the renderer entry points that A and B finalise. E is independent. | F 1.5 · E 1.5 = 3 d |
| Release | fresh recall run, re-pin snapshot + badge, ratchet the floor, CHANGELOG, `set_version.py`, tag guard, CTAN bundle, CRAN `1.2.0-1` | all | 1 d |

Total ≈ 31.5 developer-days. Every item lands in both engines (§XIII) with
the parity tests named per item; the vendored R crate is refreshed with
`r/jsslintr/tools/vendor-jsslint-core.sh` after every core change.

**Scope-cut recommendation (rev 3, unchanged in rev 4).** If 1.2.0 must be shorter, the lever
is A-coverage (5 days): 1.2.0 then ships a footer that states recall only,
and 1.3.0 headlines the coverage matrix. The next lever is colour + browser
zip (3 days together). Nothing else is separable: D, S, and B form one
dependency chain (S must precede baselines; B stamps D's rule-set version),
and A-recall is the release's reason to exist. The maintainer's decision
for now is to keep everything in 1.2.0.

## 4. Item D — Version and rule-set provenance (P1-D)

- **catalogue.yaml** top level gains `ruleset_version: "YYYY-MM-DD"`,
  `ruleset_fingerprint: "sha256:…"`, `guide_edition: "jss.cls 3.3"`
  (`guide_source = f"{guide_edition} ({source_vendored_at})"` composed in
  codegen). Validator `tools/_catalogue_validate.py` (`REQUIRED_TOP_KEYS`
  :54) + `contracts/catalogue-schema.md` updated; `render_catalogue.py:140`
  prints them.
- **Fingerprint** = sha256 of canonical JSON (`sort_keys`, compact
  separators, `ensure_ascii=False`) of (a) the active rules' `{rule_id,
  category, severity, description, guide_section|"", confidence|"high",
  auto_fixable}` sorted by id, and (b) **`messages.json`**: a generated
  file `specs/003-jss-rule-catalogue/messages.json` mapping each rule id
  to the sorted unique `(message, suggestion)` pairs the Python reference
  engine emits on `tests/fixtures/violations/**/*-bad.*` (61 of 62 rules
  have such a fixture; `JSS-PROJECT-001/002` use the resolver
  cycle/missing-target fixtures already exercised by `cli_parity.rs`).
  New `tools/generate_message_snapshot.py [--check]` + freshness test; any
  rewording changes the file, which changes the fingerprint, which the
  stamp tool turns into a mandatory `ruleset_version` bump. Generated
  **after item S** so 1.2.0's fingerprint reflects the final wording.
  `messages.json` is Python-only (not vendored, not read by `build.rs`);
  Rust embeds the stored fingerprint string and the vendored-sync test
  keeps it equal.
- **Stamping**: `tools/generate_catalogue_data.py --stamp-fingerprint
  --ruleset-version YYYY-MM-DD` rewrites only the two single-line keys by
  regex (PyYAML cannot round-trip the comment header) and **refuses** when
  the computed fingerprint changed but the date did not (the policy gate).
  `--check` fails when stored ≠ computed. Guard test
  `tests/unit/journals/jss/test_ruleset_version.py`: stored == computed;
  date valid, ≤ today, ≥ `source_vendored_at`.
- **`--version`** (stdout, exit 0), byte-identical except line 2:
  ```
  jss-lint 1.2.0
  engine: texlint/python 1.2.0        # Rust: engine: jsslint-core/rust 1.2.0
  rule set: 2026-09-15 (jss.cls 3.3, vendored 2021-05-23)
  journal: jss
  ```
  Stub journal → `rule set: n/a`; unregistered `--journal x` →
  `journal: x (not registered)`, still exit 0. Python: drop
  `click.version_option`, add a plain `--version` flag handled in `main()`
  after the subcommand early-return and before the "at least one FILE"
  check, after `load_config` so `--journal`/TOML are visible. Rust: drop
  `version` from `#[command]`, add `#[arg(long)] version: bool`. Formatter
  `texlint.version.format_version_block` / `jsslint_core::version` in core
  so bindings reuse it.
- **Bindings**: `jsslint-wasm` `version()` export (`{tool, engine,
  rulesetVersion, guideSource}`), `jsslint.version()` + `__version__`,
  `jsslintr::jsslint_version()` (adds the package version `1.2.0-N` — the
  distribution → engine → rule-set mapping in code).
- **`docs/versions.md`**: channel table with version-string constraints —
  crates.io (semver; `-N` reads as pre-release, never used), PyPI ×2 (PEP
  440, plain `X.Y.Z`), npm (semver, stamped from Cargo by wasm-pack), VS
  Code Marketplace/Open VSX (strictly increasing `X.Y.Z`, no pre-release),
  CRAN (`X.Y.Z-N` resubmission suffix, DESCRIPTION only, §XV exception),
  CTAN (new identifier per upload: `1.2.0`, doc-only re-uploads use the
  `YYYY-MM-DD` form), GitHub Action (`vX.Y.Z` + rolling `v1`; tags with
  `-` skip the rolling move). Mapping table, compatibility policy (D4), pin
  advice (`pip install "jss-style-checker~=1.2.0"`, `cargo install
  jsslint-cli --version "^1.2"`, action `version: 1.2.0`, plus a
  baseline), and the explicit statement: **a minor release may reword
  messages or suggestions; the rule-set date bumps; baseline entries for
  reworded rules go stale and `--update-baseline` is expected** (the
  baseline summary line names both rule-set dates when they differ).
  `CHANGELOG.md` header gains the policy in two sentences.
- Tests: `test_ruleset_version.py`; message-snapshot freshness;
  `tests/integration/test_cli_subcommands.py` `--version` cases; parity
  `rust/jsslint-cli/tests/version_parity.rs` (lines 0, 2, 3 compared;
  `--journal jss`; scratch TOML `journal = "nope"`);
  `test_jsslint_parity.py` compares `jsslint.version()["rulesetVersion"]`.
  Contract docs: `contracts/cli.md:23,80`.

## 5A. Item S — Token-specific suggestions (rev 4 scope, precedes B)

**Why now.** `suggestion` is a baseline-key component (D1) and a
fingerprint input (D4). Sharpening a generic suggestion after 1.2.0 would
invalidate every baseline entry of that rule for every user; doing it
before any baseline exists costs only the engineering. The audit in §2
identified the candidates; the prototype in `research.md` §3 (simulated
identifiers replayed on the jss5342 rounds and the 30-paper audit) fixed
the scope by volume: the ten rules below remove 94 % of the masking S can
remove. Each gains a stable identifier that survives sentence edits and
changes only when the violation itself changes.

| Rule | Identifier added to the suggestion | Source | Masking removed (30 papers) |
|---|---|---|---|
| `CODE-003` | the offending fragment: ±8 chars around the matched operator/comma | matched span | 141 |
| `OPER-003` | the equation's `\label` if present, else first 40 chars of its first body line | equation node | 78 |
| `TYPO-001` | first 40 chars of the caption | `\caption{…}` argument | 56 |
| `REFS-004` | the BibTeX entry key: `… in entry 'zeileis2004'` | entry already parsed; `REFS-003` precedent | 47 |
| `CAP-002` | the section title, whitespace-normalised, ≤ 60 chars | `\section{…}` argument | 34 |
| `CODE-001` | first 40 chars of the comment | comment text | 29 |
| `XREF-004` | as `OPER-003` | equation node | 28 |
| `REFS-007` | the BibTeX entry key | entry | 28 |
| `XREF-002` | the referenced label: `… before \ref{eq:loglik}` | `\ref` argument | 25 |
| `CITE-003` | the cite key(s) of the matched `\cite` | `\cite` argument | 17 |

**Generic by decision** — `WIDTH-001`: chunk/environment keying removes 5
of 1 256 duplicates (long lines cluster within one chunk) and line-prefix
keying re-keyed 2 of 3 persisting findings on jss5342; neither is worth
the churn on the highest-volume rule. Its findings within a file stay
interchangeable (§5.7 limit 1).

**Deferred to follow-ups** (≤ 6 % of removable masking combined): entry-key
additions for `REFS-005`, `REFS-006`, `NAME-002`, `HOUSE-002`,
`BIBTEX-003/004/005`; `TYPO-004`; `XREF-006`. Their suggestions are
unchanged in 1.2.0, so a later rewording follows the ordinary rule-set-bump
path and affects only their own entries.

**Unchanged** (already token-specific; repeats are inherent): `MARKUP-001`,
`MARKUP-003`, `OPER-001`, `OPER-004`, `CODE-002`, `REFS-003`.

**Mechanics.** Python rule module first (§VIII: failing test, then the
change; §IX: 100 % branch coverage kept), then the Rust port, then fixture
goldens. Suggestion text is rendered identically in both engines
(byte parity); a shared normalisation helper (collapse whitespace, cap
length, escape nothing) lives beside the existing suggestion helpers in
each engine. `message` text is unchanged. Rule-set consequences: this is
a rewording → `ruleset_version` bump in 1.2.0 (already a minor), and
`messages.json` is generated after S.

**Tests.** Per rule: unit tests in `tests/unit/journals/jss/` (identifier
present, capped, normalised; branch coverage), Rust unit tests mirroring
them; `tests/fixtures/violations/*-bad.*` expectations updated; SARIF
goldens regenerated; `tex_rules_parity.rs` / `bib_rules_parity.rs` /
`engine_parity.rs` pick up the change; the jss5342 replay from §5.7
asserts distinct-key and new/stale counts as the regression test.
Eval: verify `eval-jss iterate refresh` label restoration is keyed by
`(rule, file, line)` not message text before landing (§2 hazard); the
recall corpus annotations are `(rule, file, line)` and unaffected.

**Compatibility.** Users see more specific suggestions; JSON `suggestion`
values change for these rules (string content only, additive-compatible).
Effort 4 days (10 rules × ~0.4 d incl. both engines and fixtures). The
replay test replaces the prototype's simulated identifiers with the real
suggestions and asserts distinct keys ≥ 75 and re-keyed persisting
findings ≤ 4 on the jss5342 initial → resubmission transition.

## 5. Item B — Baseline mode (P0-B) + Rust inline ignores

### 5.1 Pre-work (Python reference)
`ParsedTexFile` gains `line_offset: int = 0` (`api.py:295`), set by
`rmd_parser.py:348` to `prose.line - 1`; `build_index` adds it;
`directive_lines` uses `source.split("\n")`. New cases in
`tests/unit/core/test_suppress.py`: `.Rmd`, `.Rnw`, form feed.

### 5.2 Shared hook (own PR: "inline ignores in the Rust engine")
- Ships as the first PR of Phase 1-B with its own CHANGELOG entry under
  *Fixed* ("the Rust engine and every surface built on it — `jsslint`,
  WASM/web, VS Code, PyO3, R — now honour `% jss-lint: ignore`; `.Rmd`
  directive lines and form-feed handling fixed in the Python engine"), so
  a behaviour regression is attributable independently of the baseline.
- Python `engine.run(config, target, journal, *, suppress: Suppressor | None
  = None)` (`engine.py:226`), `Suppressor = Callable[[Violation], bool]`.
  Inline index stays inside `run` (LSP/init/report paths need it). At
  `:342-347`: sort `rule_violations` by `Violation.sort_key`, then drop
  inline-suppressed first, then `suppress(v)` — so an inline-ignored
  finding never consumes a baseline count. Parse errors bypass the hook
  (`:379-384`); `JSS-PARSE-000` can never be baselined.
- Rust: new `rust/jsslint-core/src/suppress.rs` (port; `regex` has no
  lookbehind → `(?i)(?:^|[^\\])(%+)\s*jss-lint:\s*ignore\b([^\n]*)` using
  group 1's start for the comment-only-line test; ids via
  `\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b` after upper-casing; index over
  `all_tex_like_docs()` with `parsed.source` + `parsed.line_offset`
  (`rmd.rs:361`) and bib sources). `pub trait Suppressor { fn
  suppress(&mut self, v: &Violation) -> bool }`; `engine::run_with(config,
  doc, project_extra, extra: Option<&mut dyn Suppressor>)`; `run` and
  `run_with_project` (`engine.rs:747`) delegate; inside `run_one`
  (`:769`) build the index once, sort, `retain` before the severity remap
  and bookkeeping (`:775-790`). Remove the note at `:721-723`.

### 5.3 Baseline core (pure, both engines)
`src/texlint/core/baseline.py` / `rust/jsslint-core/src/baseline.rs`:
`BaselineDocument{schema_version, tool_version, ruleset_version, journal,
entries}`, `BaselineEntry{rule_id, path, message, suggestion, count}`,
`parse(text)` (error on `schema_version != 1` or bad shape), `build(...)`,
`dumps()` (`json.dumps(indent=2, sort_keys=True) + "\n"`; Rust through
`json_output::write_value` so bytes match CPython), and `BaselineMatcher`
(multiset `remaining: {(rule_id, path, message, suggestion): count}`,
`path_map` `{str(parsed_file.path): baseline-relative posix}`,
`__call__(v) -> bool` decrements, `summary(path, applied_rule_ids) ->
BaselineSummary{path, matched, stale, unevaluated, ruleset_version}`).
**Stale** = unmatched entries whose rule ran; **unevaluated** = unmatched
entries whose rule did not run (ignored, below `--min-confidence`,
format-skipped, unknown) — without it, CI with `--min-confidence high`
against a default baseline would report dozens of false "stale" entries.
`suggestion` is stored as `""` when the violation has none. File shape (no
timestamp, so `--update-baseline` is byte-identical across engines and
runs; entries sorted by `(path, rule_id, message, suggestion)`):
```json
{
  "entries": [{"count": 1, "message": "…", "path": "refs.bib", "rule_id": "JSS-REFS-003",
               "suggestion": "Add a doi field to entry 'koller2023' if one is available."}],
  "journal": "jss",
  "ruleset_version": "2026-09-15",
  "schema_version": 1,
  "tool_version": "1.2.0"
}
```

### 5.4 CLI layer (both)
- Flags `--baseline FILE`, `--update-baseline`; TOML `baseline` (path,
  relative to cwd like `.jss-lint.toml`); `ToolConfig.baseline`,
  `KNOWN_FIELDS`, `RawOverrides.baseline` (+ the four struct-literal
  sites). `--baseline` > TOML; `--update-baseline` with neither →
  `./.jss-lint-baseline.json`. No auto-discovery.
- Relativisation at the CLI: `base = baseline.resolve().parent`; for every
  parsed file `relpath(p.resolve(), base)` as posix (Rust: `canonicalize`
  as `resolver.rs:265,281`, strip `\\?\`, lexical relative join with `/`).
  Auto-resolve (absolute canonical `file`) and `--no-resolve` (literal
  arg) therefore yield the same key; files outside `base` get `../`.
- Flow: load config → parse → read + `parse()` baseline (exit 2 with
  `jss-lint: <msg>` on error or `journal` mismatch) → build `path_map` →
  `run(..., suppress=matcher)` → `report = replace(report,
  baseline=matcher.summary(...))`. `--update-baseline`: run with no
  suppressor, `build()` from `report.violations` minus `JSS-PARSE-000`,
  write via tempfile + `os.replace` (§VII), stderr `jss-lint: wrote N
  baseline entries to <path>`, exit 0 (2 on error-severity parse failure),
  no report rendered.
- Semantics: exit code from the remaining violations; `--fail-on`,
  `--ignore-rules`, `--min-confidence` apply first; `--fix`/`--dry-run`
  operate on the visible report (hidden means hidden; run without
  `--baseline` to fix accepted findings); reviewer compliance % is
  post-suppression; SARIF omits baselined results (`baselineState` noted
  as future work); `diff` unchanged (docs note the baselined-vs-unbaselined
  diff caveat).
- Output: terminal line after the footer in both modes
  `Baseline: 12 findings hidden by .jss-lint-baseline.json (3 stale, 0 unevaluated)`,
  extended with ` — written for rule set 2026-09-15, current 2026-11-02; run --update-baseline`
  when the stamped rule-set date differs; JSON top-level `"baseline": null
  | {"matched", "path", "stale", "unevaluated", "ruleset_version"}` always
  present; HTML `<p class="note">`.
- `ComplianceReport.baseline: BaselineSummary | None` (Python) /
  `Option<BaselineSummary>` (Rust; update literals at `engine.rs:1038`,
  `tests/parity.rs:122,150`). The engine never sees the file.
- Action: input `baseline` (default `''`) → `--baseline` when non-empty;
  needs PyPI 1.2.0 for `version: latest`. Docs: adoption recipe
  (`--baseline .jss-lint-baseline.json --update-baseline` once, commit the
  file, CI fails only on new findings; re-run after renaming files or after
  a rule-set bump).
- Bindings: not exposed in 1.2.0 (bindings already omit `--apply`,
  `--crossref`, TOML discovery on wasm); documented in `rust/README.md`;
  an in-memory variant is a ~1-day follow-up.

### 5.5 Tests
Unit (both): every `suppress` case by name incl. Rmd offset/Rnw/form feed;
baseline parse/build/dumps round-trip, sorted output, consumption in sort
order (3 occurrences vs count 2 hides the two lowest lines), stale vs
unevaluated, journal/schema mismatch, `path_map` miss, rule-set date
mismatch line; engine hook order, parse-error bypass, category PASS when
all findings baselined. Integration `tests/integration/test_cli_baseline.py`:
create → hide → exit 0; a finding of a new `(rule, message, suggestion)`
→ exit 1; TOML key; subdirectory baseline → `../` paths; `--no-resolve`
vs auto-resolve equivalence; summary in terminal/json/html; `--fix` skips
baselined; `test_action_manifest.py` for the input. Parity: new
`rust/jsslint-core/tests/suppress_parity.rs` over fixtures
`tests/fixtures/suppress/{inline.tex, scoped.tex, verbatim.tex,
escaped.tex, entries.bib, chunks.Rnw, prose.Rmd}`; new
`rust/jsslint-cli/tests/baseline_parity.rs` (identical `--update-baseline`
bytes; identical stdout/exit for terminal/json/sarif with `--baseline`;
drift scenario; TOML key; subdirectory; journal-mismatch exit 2);
`wasm_parity` inline-ignore fixture. A regression test replays the
`examples/jss5342-versions` initial → resubmission transition and asserts
the survival/new counts of §5.7 (re-baselined after item S). Divergence to
document: malformed baseline JSON error text (same precedent as `diff`).

### 5.6 Backward compatibility
JSON gains an always-present `baseline` key (null when inactive; matches
`compliance_percentage: null` and the "all keys present" contract);
`diff.validate_payload` checks only required keys, so old and new reports
still diff. Rust surfaces now honour inline ignores (behaviour fix, own
CHANGELOG entry). Older CLIs warn about the unknown TOML key only under
`-v`.

### 5.7 Evidence — key survival on real and simulated revisions

Method: lint with the Python reference (`--output json --no-resolve`),
compute multiset survival of candidate keys between versions.

**Simulated rounds** on five corpus papers (robustlmm, AER, arules, BART,
sandwich; 259 findings): paragraph insertion (line drift), sentence edits
on 25 % of prose lines, and additionally edits on half of the flagged
lines. Key `(rule, path, message)`: 100 % / 100 % / 99.6 % survival. JSS
messages are the rule descriptions and quote no source text (258 of 259
messages invariant across occurrences); the reviewer's "edit the sentence
and the entry goes stale" case does not occur for this rule set.

**Real rounds**, `examples/jss5342-versions` (initial → resubmission →
resubmission2 → final; 100 → 44 → 28 → 19 findings, main file renamed
twice):

| Transition | line-based key | `(rule, path, message)` | `(rule, path, message, suggestion)` | + source-line context on non-prose rules (rejected) |
|---|---|---|---|---|
| initial → resubmission | 1 % survive | 34 survive, 66 stale, **10 new** | 26 survive, 74 stale, **18 new** (49 keys) | 21 / 79 / 23 (77 keys) |
| resubmission → resubmission2 | 16 % | 26 / 18 / 2 | 26 / 18 / 2 (15 keys) | 24 / 20 / 4 (34 keys) |
| resubmission2 → final | 54 % | 19 / 9 / 0 | 19 / 9 / 0 (14 keys) | 19 / 9 / 0 (21 keys) |

Stale entries here are overwhelmingly findings the author really fixed
between rounds (e.g. 16 `REFS-006`, 10 `XREF-002`), which is the intended
outcome and what `--update-baseline` prunes. The eight extra "new"
findings under the suggestion-bearing key are all genuinely new (two `NULL`
sentinels where only `NA` existed before; two new doi-less bib entries;
four code-spacing findings in code chunks the author added) and were
**masked** by the message-only key through the counts of fixed
same-rule findings. No false-new was observed with the suggestion key.
The rejected "source-line context" variant (rev-3 alternative to item S)
would have re-keyed 5 of 44 persisting findings in the first round and 2
of 28 in the second. **Item S, prototyped by simulation (rev 4,
research.md §3)**: with all candidate rules and `WIDTH-001` generic,
distinct keys on the initial version rise 49 → 80 (predicted ~77) and 4 of
44 persisting findings are re-keyed (3 `CITE-003`, an upper bound from
line-level extraction, + 1 `CODE-003`); second round 15 → 33 keys, 3
re-keyed; third round 14 → 25, none. The robustness gain over the context
variant is small on this sample; S's case is specificity plus better
author-facing messages, at 4 days for the ten-rule scope.

**Documented limits** (go into `docs/baseline.md` and the contract):
1. Findings with identical `(rule, path, message, suggestion)` are
   interchangeable: fix one and add another of the same shape in the same
   file and the new one is masked while the count holds. After item S this
   is confined to `WIDTH-001` (generic by decision: "the file still has N
   over-wide lines"), rules whose token inherently repeats
   (`MARKUP-001/003`, `OPER-001/004`, `CODE-002`), e.g. two unwrapped `R`
   in one file, and the deferred tail (`REFS-005/006`, `NAME-002`,
   `HOUSE-002`, `BIBTEX-003/004/005`, `TYPO-004`, `XREF-006`).
2. Renaming or moving a file invalidates all its entries (path is in the
   key): re-run `--update-baseline` after renames.
3. A rule-set bump that rewords a rule invalidates that rule's entries;
   the summary line names both dates; `--update-baseline` is expected.

## 6. Item C — Fix safety (P1-C)

- Summary line at the end of `apply_fixes` in both engines (stdout, before
  the report render), wording aligned with `r/jsslintr/R/jsslint.R:344-372`:
  `Applied 3 fixes to 1 file (2 skipped: conflict 1, rule-not-selected 1).`
  / `Dry run: 3 fixes would be applied to 1 file. Re-run without --dry-run to write.`
  Rejections keep their stderr line. `fix_parity.rs` covers all modes.
- Docs: README "Before `--fix`" (commit or `--dry-run` first; the tool
  never touches git; fixes are atomic and re-verified, §VII); same in
  `rust/README.md` and the R vignette. No git detection (D5). Rationale:
  fixes are already atomic and re-verified; `--dry-run` is the preview
  path; many manuscripts live outside git (Overleaf, Dropbox); the R,
  PyO3, and WASM bindings could not honour a git check, so it would be a
  CLI-only behaviour; a `git status` subprocess adds environment-dependent
  output the parity and eval harnesses would have to mask.

## 7. Item A — Recall and coverage transparency (P0-A + coverage)

### 7.1 Data (journal-owned, vendored) and the CI gate
- `specs/003-jss-rule-catalogue/recall.json` — **generated** (generated
  files in that directory are JSON, hand-authored ones YAML) by new
  `tools/generate_recall_snapshot.py --run-timestamp TS [--check]` from
  `recall_history`, filtered to active catalogue rules. Shape:
  `{"corpus_hash", "generated_by", "min_plants": 10, "run_timestamp",
  "rules": {"JSS-…": {"fn", "tp"}}}` (`sort_keys`, indent 2). Freshness
  test `tests/unit/eval/test_recall_snapshot_fresh.py`. Badge:
  `eval/badge.py` reads `run_timestamp` and sums tp/fn from the snapshot
  (constant at `:46` removed); the paper pin is untouched.
- **Recall gate in CI, floor raised (D11).** `eval/cli.py:601` becomes a
  named constant `RECALL_FLOOR = 0.78` (help text at `:326` updated);
  spec 017 FR-011's "explicit decision in a future spec" is recorded here:
  0.78 leaves ~50 false negatives of slack below the shipped 0.807 so
  adding a paper with a weak rule does not fail CI, while the per-rule
  ≤ 0.05 regression check keeps catching the sharp case. The release
  checklist ratchets the floor to `floor(snapshot − 0.03, 2 dp)` at each
  release, and a unit test asserts `RECALL_FLOOR ≥ snapshot − 0.03`. CI:
  `.venv/bin/eval-jss recall --gate --no-record` in the `parity` job right
  after the corpus is materialised (`.github/workflows/ci.yml:177-178`);
  `--no-record` keeps the checked-in DB unchanged; the gate's per-rule
  reference is the last *recorded* run, which the release checklist
  refreshes before regenerating the snapshot.
- `specs/003-jss-rule-catalogue/guide-coverage.yaml` — **hand-curated**,
  migrated from checklist §1.1–1.4 (which gets a "YAML is authoritative"
  note). `sources:` block carries the editions/fetch dates (`jss_cls`
  3.3/2021-05-23, `article_tex` 2021-12-10, `style_guide` fetched
  2026-04-23, `author_instructions` fetched 2026-04-23) — this is the
  honest "dated edition" pin. `directives:` entries `{id, source, section
  (anchor or index.json key), provision, status: checked|partial|
  not_checked|out_of_scope, rules: [...], reason}` with id prefixes `CLS-`,
  `TEX-`, `SG-`, `AI-`. Validator `tools/_coverage_validate.py` + contract
  test: unique ids; prefix ↔ source; `rules` non-empty iff status ∈
  {checked, partial}; every listed rule **active** (retirement flips the
  test red — fixes the seven stale credits); `reason` required unless
  checked; **every active non-internal rule appears in ≥1 directive** (§V).
  **Curation plan (2.5 d)**: (1) script the migration of the 146 rows
  (0.5 d); (2) write directives for the 15 unclaimed rules by reading the
  guide sections they cite — most attach to existing rows (`REFS-003/005/
  006/007`, `BIBTEX-003/004/005` under SG-006/008/017; `XREF-004/005/006/
  007` under SG-011; `OPER-004` under SG-057's neighbourhood; `REFS-001`
  under SG-006), `PROJECT-001/002` get `internal` rows (1 d); (3) re-judge
  the 7 retired-credit rows and any `partial` (0.5 d); (4) validator +
  contract test (0.5 d).
- Vendoring: add both files to the `cp` line in
  `r/jsslintr/tools/vendor-jsslint-core.sh:63`, `_FILES` in
  `tests/unit/test_vendored_catalogue_in_sync.py:24`, `build.rs`
  `rerun-if-changed`; new `rust/jsslint-core/tests/package_contents.rs`
  runs `cargo package --list` and asserts all five catalogue files ship.

### 7.2 Model and codegen (both engines)
- Do **not** stamp recall on `Rule` (no engine decision reads it). Instead
  `api.py`: `RecallStat{tp, fn}` with `state(min_plants)`, `percent()` =
  `(200*tp + n) // (2*n)` (integer half-up; no float rounding parity risk),
  `label()` → `"81%" | "limited (n=4)" | "unmeasured"`; `RecallRun`,
  `CoverageDirective`, `RuleSetInfo{version, fingerprint, guide_source,
  recall}`, `JournalMetadata{rule_set, recall_by_rule, coverage}`;
  `JournalRuleModule.metadata()` non-abstract default → empty (stub journal
  keeps working, §IV). `JSSJournal.metadata()` reads `_catalogue_data`.
  `engine.run` stamps `CategorySummary.recall` (pooled over the category's
  rule ids; `None` without data), `ComplianceReport.rule_set`,
  `ComplianceReport.coverage`. Renderers read the report only.
- Codegen: `tools/generate_catalogue_data.py` additionally reads
  `recall.json` + `guide-coverage.yaml` and emits `RULESET_VERSION`,
  `RULESET_FINGERPRINT`, `GUIDE_SOURCE`, `RECALL_RUN`, `RECALL`, `COVERAGE`
  (one generator, existing freshness test). `build.rs` parses both and
  emits the equivalent statics into `catalogue_data.rs`; `catalogue.rs`
  adds structs/accessors; `report.rs` mirrors the dataclasses;
  `engine.rs:1038` fills them.

### 7.3 Surfaces (byte-identical in both engines)
- **Reviewer table**: fifth column `Recall` (`no_wrap`, left-justified;
  widest cell `limited (n=9)` keeps the table ≈ 66/120 columns, so
  `collapse_widths` never triggers). After `Overall:` one line
  `Measured recall: 81% (1967 annotated instances, 17 papers, run 2026-07-19)`,
  then `console.rule("Not checked by jss-lint")` + a table `Directive` |
  `Status` (`partial`/`not checked`) | `Provision` (wraps), groups
  partial-then-not_checked sorted by id, then
  `Run jss-lint coverage for the full matrix (N checked, P partial, K not checked, O out of scope).`
- **Author mode**: footer always printed on **stdout**, also on a clean
  run (ASCII only, each line < 120 columns):
  `No findings does not mean compliant. Measured recall: 81% (1967 annotated instances, 17 papers).`
  `jss-lint checks N of M guide directives (K not checked, P partial). Run jss-lint coverage for the list.`
  A journal without data prints `jss-lint has no recall or coverage data for journal <id>.`
  Rationale for stdout (maintainer decision): the terminal author report
  is the report; a saved text report of a clean run must not be empty; the
  CLI contract's CI signal is the exit code, not empty output; JSON/HTML
  carry the same statement in-band. `cli.md` §Streams and
  `test_cli_author_terminal.py:79` are updated.
- **`jss-lint coverage [--format terminal|markdown|json]`** in both CLIs
  (`REGISTERED_SUBCOMMANDS`, `main.rs:147`; click subcommand beside
  `explain`; rendering in core `coverage.py`/`coverage.rs`). Terminal:
  `Guide coverage — jss (rule set 2026-09-15)`, counts line, per-status
  groups with `reason:`/`rules:` lines; JSON: full directive list with
  provisions + counts; Markdown: one table per source.
- **`explain RULE`**: always prints `Recall: …` (three states) and
  `Covers: SG-027, SG-028`.
- **JSON** (additive; all keys always present; integers only):
  per-category `recall: {"state", "tp", "fn", "percent": int|null}`;
  top-level `rule_set: {"version", "fingerprint", "guide_source", "recall":
  {"run_timestamp", "corpus_hash", "min_plants", "tp", "fn", "percent"}}`;
  top-level `coverage: {"counts": {"checked", "partial", "not_checked",
  "out_of_scope"}, "items": [only partial/not_checked, without provision
  text]}`. Stub journal: nulls / `coverage: null` / category
  `{"state": "unmeasured", "tp": 0, "fn": 0, "percent": null}`.
  `contracts/json-output.md` rewritten (it is also stale on
  `guide_section`, `guide_url`, `confidence`, `skipped_rules`).
- **SARIF**: rule descriptors gain `properties.confidence` and
  `properties.recall` (goldens mask the rule list; `sarif_parity.rs`
  covers bytes).
- **HTML**: author `<p class="note">` with the two footer sentences
  (replacing/after `No violations found.`, `author.html.j2:52-54`,
  `html_output.rs:58-60`); reviewer `<th>Recall</th>`, footer line,
  `<table class="coverage">`. The web app shows it with no change.
- **Catalogue page**: `render_catalogue.py` adds `Confidence` and `Recall`
  columns, a `Coverage` section, and the rule-set/edition header lines.
  Docs: `docs/recall-and-coverage.md` (how measured; the source-only
  lower-bound caveat from `eval/recall-corpus/README.md:53-69`; the
  three states; how to read the coverage matrix).

### 7.4 Tests
Unit: `RecallStat` boundaries (n = 0, 1, 9, 10; half-up 78.5 → 79;
1587/1967 → 81) in both engines; coverage validator matrix incl. the
retired ids; snapshot freshness; floor-vs-snapshot assertion;
`test_badge.py` on the snapshot source; engine pooled recall +
stub-journal `None`. Integration: reviewer column + block, author footer
always present (update `test_cli_author_terminal.py:79`), JSON key set
(`test_cli_json.py:35`), HTML, `coverage` three formats, plugin discovery
(stub → unmeasured/n-a). Parity: existing `terminal_parity.rs`/
`html_parity.rs`/`cli_parity.rs`/`sarif_parity.rs` pick up the changes;
new `coverage_parity.rs`; `explain_parity.rs`. Contract: every active rule
in `guide-coverage.yaml`; `package_contents.rs`; `generate_paper_stats
--check` unaffected (reads `categories` only). CI: the recall gate step.

### 7.5 Backward compatibility
JSON: +2 top-level keys, +1 per-category key (additive within the major;
CHANGELOG). Terminal: author mode is never empty; reviewer has a fifth
column (`paper/generated/tab-demo-reviewer.tex` is built from JSON
`categories` and unaffected). SARIF property-bag keys are ignored by
consumers. Exit codes unchanged.

## 8. Item F — Colour (P1-F)

**Invariant.** The plain stream stays the canonical artifact and stays
byte-identical across engines: parity suites, snapshot tests, and the eval
harness keep comparing it (`eval/scan.py` parses JSON anyway). Coloured
output is **not** a byte-parity target: the escape bytes are per-engine
best-effort, recorded in `rust/README.md` as a documented §XIII
divergence. What *is* identical across engines: the decision of whether to
colour, and the guarantee that colour never changes layout.

**Python.** `terminal.py` already carries the styles as rich markup
(`[red]`, `[yellow]`, `[bold]`, `[dim]`, `_SEVERITY_STYLE`,
`_STATUS_STYLE`); `_console()` (`:112-115`) gains a `color: bool` argument
→ `Console(file=sys.stdout, force_terminal=color, color_system="standard"
if color else None, no_color=not color, width=120)`. `color_system=
"standard"` limits rich to the 16-colour SGR set; `width=120` keeps the
layout unchanged. Confidence suffix stays `[dim]`; add `[bold]` to rule
ids and header cells if not already styled. Windows console handling is
rich's own (legacy console via its win32 layer); no FFI.

**Rust.** `terminal::render(report, config, color: bool)` (or a `Styles`
table selected once): cell text is wrapped in SGR at render time where the
cell is built (severity word, status word, rule id, confidence suffix,
banner title, header cells, `Overall:` value). Measurement uses the
unstyled text so widths are unchanged. Palette: `31` red (error/FAIL),
`33` yellow (warning), `36` cyan (info; blue is unreadable on dark
backgrounds), `32` green (PASS), `1` bold, `2` dim, `0` reset — 16-colour
only, no 256-colour or truecolor assumption. Output goes through
`anstream::AutoStream::new(stdout, choice)` in `jsslint-cli` with the
choice **we** computed (never `AutoStream::auto`, whose own env heuristics
would diverge from Python); anstream converts SGR for legacy Windows
consoles and strips it when told `Never`. `anstream` is already in the
lockfile via clap; it becomes a direct dependency of the CLI crate only
(not core, not WASM; `isolation.rs` unaffected).

**Decision** (one pure function of `(flag, toml, env, isatty)` in both
CLIs, unit-tested as a matrix): `--color always|never` > `NO_COLOR`
non-empty → off > `CLICOLOR_FORCE` non-empty and ≠ `0` → on > TOML
`color` > auto (= stdout is a TTY and `TERM != dumb`). The flag beats both
env vars; `NO_COLOR` beats `CLICOLOR_FORCE` (anstream/ripgrep/cargo
order). `--output json|sarif|html` and non-terminal subcommand formats
never colourise; `diff`/`explain`/`coverage` terminal formats use the same
switch. `ToolConfig.color: "auto"|"always"|"never"` (TOML key `color`;
Rust `ColorChoice`; the four `RawOverrides` literals); the CLI resolves to
a bool and passes it to the renderer rather than mutating the config.

**Colour is redundant by construction**: severity, status, and rule id
words stay in the plain text; confidence keeps its `(medium conf.)`
marker; nothing is encoded in hue alone. Reviewer PASS/FAIL/SKIPPED are
coloured. VS Code is unaffected (it never renders terminal text). WASM/
PyO3/R never colourise (documented).

**Tests.** Unit (both engines): `strip_sgr(render(color=True)) ==
render(color=False)` on the author, reviewer, and skipped-rules fixtures;
per-line visible width unchanged; the decision matrix (flag × NO_COLOR ×
CLICOLOR_FORCE × TOML × isatty). Cross-engine: `terminal_parity.rs` gains
`--color always` cases where **both** sides are SGR-stripped before the
byte comparison (colour must never change layout in either engine); new
`rust/jsslint-cli/tests/color_parity.rs` via `run_with_env` checks the
*decision* only: for `NO_COLOR=1`, `CLICOLOR_FORCE=1`, `NO_COLOR=1 --color
always`, TOML `color = "always"`, `--color never` + `CLICOLOR_FORCE=1`,
`--output json --color always`, both CLIs agree on whether any `\x1b[`
appears, and stripped bytes are identical. `CliRunner` is never a TTY, so
existing Python terminal tests stay plain. Windows: manual verification
(no CI job). Docs: README, `contracts/cli.md`, `rust/README.md`.

Effort 1.5 days.

## 9. Item E — Overleaf (P2-E)

- `docs/overleaf.md`: (1) Menu → Download → Source (zip) → drop onto the
  browser app (nothing uploaded); (2) unzip → `jsslint main.tex` /
  `jss-lint main.tex` (auto-resolve follows `\input`); (3) Overleaf GitHub
  Sync (premium) → the GitHub Action on every sync, with a baseline for
  existing projects; (4) re-upload `--fix` output. Linked from README and
  the `web/index.html` footer.
- Browser zip drop (`web/app.js`, `web/index.html`): drag-and-drop zone +
  `.zip` in the file input; a ~120-line zip reader (End-of-Central-
  Directory → central directory → local headers; method 0 copied, method 8
  through `new DecompressionStream("deflate-raw")` — Chrome 103+, Firefox
  113+, Safari 16.4+); skip `__MACOSX/`, `._*`, non-lintable suffixes;
  keys are entry paths so multi-file resolution works; unsupported browser
  → message pointing at the folder picker. No WASM change; JS +~4 KB.
- CLI zip cost estimate (deferred to follow-ups): Python 0.5 d (stdlib
  `zipfile`), Rust 1 d (`zip` crate at the CLI layer, isolation-safe),
  parity 0.5 d.

## 10. Cross-cutting

- **WASM bundle**: A embeds ≈ 30 KB of directive strings + recall table;
  B adds inline suppression (~5 KB); S changes suggestion formatting
  (negligible); baseline/version formatting are unreferenced by the wasm
  crate and stripped; colour adds a `bool` branch in the renderer.
  Expected < +50 KB on 1.96 MB. Add a size line to the job summary in
  `publish-web.yml`/`ci.yml` and a soft gate (2.2 MB) in
  `rust/jsslint-wasm/tests/`. No new runtime dependency in core, WASM,
  PyO3, or R; `anstream` becomes a direct dependency of `jsslint-cli`
  only; `isolation.rs` unaffected.
- **Divergences to record in `rust/README.md`**: engine line of
  `--version`; coloured terminal bytes (per-engine; plain bytes identical);
  baseline and colour not exposed by bindings; malformed baseline JSON
  error text; rich's ASCII box substitution on non-UTF-8 Windows stdout
  (pre-existing).
- **Release surfaces**: crates.io `v1.2.0-cli`, PyPI `v1.2.0-py` +
  `v1.2.0-pypkg`, npm `v1.2.0-wasm`, VS Code/Open VSX `v1.2.0-vscode`,
  Action `v1.2.0`, CRAN manual `1.2.0-1`, CTAN manual `1.2.0`.
- **Release checklist** (new `docs/releasing.md`): fresh `eval-jss recall`
  run (recorded) → `generate_recall_snapshot.py` → badge JSON → ratchet
  `RECALL_FLOOR` to `floor(snapshot − 0.03, 2 dp)`;
  `generate_message_snapshot.py --check` and `generate_catalogue_data
  --check` incl. fingerprint; SARIF goldens regenerated once after S;
  `set_version.py` (note: resets DESCRIPTION to bare `1.2.0`, sets
  `CITATION.cff` date to today); tag guard step in every `release-*.yml`
  (`[ "$(cat VERSION)" = "${GITHUB_REF_NAME#v}" ]` after stripping the
  channel suffix); `RELEASE_TAG_PAT` present; `web/pkg` is a build
  artifact (documented, not fixed); CTAN bundle with the corrected README;
  CHANGELOG with the JSON additions, the suggestion rewording (rule-set
  bump), and a separate *Fixed* entry for inline ignores.

## 11. Follow-ups to record in `roadmap/follow-ups.md`
Item-S tail: entry-key suggestions for `REFS-005/006`, `NAME-002`,
`HOUSE-002`, `BIBTEX-003/004/005`, and identifiers for `TYPO-004`,
`XREF-006` (each is a rule-set bump; users of a baseline re-run
`--update-baseline`); CLI zip input; baseline in the R/PyO3/WASM bindings
(in-memory variant);
SARIF `baselineState`; Action `comment-mode: pr-comment`; confidence-tier
auto-derivation from the precision DB (same pipeline as the recall
snapshot); Windows CI job for the colour path; second-annotator recall
corpus so the ratcheted floor rests on more than one annotator (spec 017
Clarifications §3).

## 12. Remaining spec-kit artifacts for this directory (after review)

`spec.md` (user stories per item A–F, S, and coverage; FRs; SCs),
`research.md` (D1–D11 with rejected alternatives: snippet-hash key,
message-only key, catalogue-flagged source-line context, SARIF
baselineState, `Rule.recall`, YAML snapshot, byte-identical coloured
output, git-dirty refusal, stderr footer, 1.1.1 split, CLI zip, floor
kept at 0.70; plus the §5.7 evidence and the 30-paper suggestion audit),
`data-model.md` (baseline file, `recall.json`, `messages.json`,
`guide-coverage.yaml`, `JournalMetadata`, report fields), `contracts/`
(`cli.md`: flags, `coverage`, `--version`; `json-output-1.2.md`;
`baseline-file.md`; `coverage-file.md`; `suggestions.md`: the identifier
table of §5A with normalisation rules; `color.md`: palette intent,
decision precedence, the strip-SGR invariant; `version-output.md`),
`quickstart.md` (adopt on an existing manuscript in five commands),
`checklists/requirements.md`.

## 13. Verification

1. `python -m pytest tests/ -q`, `ruff check .`; the §IX coverage gate
   (`--cov-fail-under=100` on `src/texlint/journals/jss/rules`) passes
   with the item-S changes.
2. `(cd rust && cargo test --workspace)` with the recall corpus
   materialised: all parity suites incl. new `suppress_parity.rs`,
   `baseline_parity.rs`, `coverage_parity.rs`, `version_parity.rs`,
   `color_parity.rs`, `package_contents.rs`; `eval-jss recall --gate
   --no-record` exits 0 at floor 0.78.
3. Manual: `jss-lint --mode reviewer paper.tex` shows the Recall column,
   footer, Not-checked block; `jss-lint paper.tex` on a clean file prints
   the footer; suggestions for the §5A rules name the entry key / title /
   fragment; `--baseline b.json --update-baseline paper.tex`, then edit
   sentences and insert paragraphs → exit 0; introduce a violation whose
   `(rule, message, suggestion)` is not already accepted in that file →
   exit 1 (a same-shape violation replacing a fixed one is masked — the
   documented limit, now confined to inherently repeating tokens);
   `--fix` prints the summary; `--version` identical modulo line 2;
   `--color=always | cat` shows SGR, `NO_COLOR=1` plain; drop an Overleaf
   zip on the web app.
4. `R CMD INSTALL r/jsslintr` after vendoring; `jsslint_version()`;
   `jsslint.version()`; wasm `version()`.
5. Bundle size reported; fingerprint `--check`; `generate_paper_stats
   --check`; badge JSON regenerated from the snapshot; jss5342 replay test
   numbers recorded in the spec.

## 14. Constitution Check

| Principle | Status |
|---|---|
| I Deterministic engine | Untouched — no rule *detection* changes (item S changes suggestion text only); all new logic is pure functions of in-memory input. |
| III Parse errors non-fatal | `JSS-PARSE-000` bypasses suppression; `--update-baseline` exits 2 only on error-severity parse failure. |
| IV Zero core edits per journal | New metadata flows through `JournalRuleModule.metadata()` → `ComplianceReport`; stub journal degrades to unmeasured / n/a / no coverage. No new `journals.jss` imports in output code. Rust remains single-journal (documented deviation). |
| V Every rule cites an authority | Every active rule must appear in ≥1 `guide-coverage.yaml` directive (contract test). |
| VI ≥ 90 % precision per rule | Item S does not change detection, so measured precision is unchanged; the eval label restoration is verified before landing. |
| VII Auto-fix verified/atomic | `--update-baseline` writes via tempfile + `os.replace`; `--fix` unchanged. |
| VIII TDD on rule modules | **Applies to item S**: each rule's new suggestion test is committed failing before the change (Python reference), Rust follows by parity. |
| IX 100 % branch coverage on rule modules | **Applies to item S**: the gate stays at 100 % for every touched module. |
| X Small surface | One subcommand (`coverage`), three flags (`--baseline`, `--update-baseline`, `--color`), one suppression hook, two generators (recall, messages); no `Rule.recall`, no timestamp field, no float shims, no colour post-parser, no per-rule key policy table. |
| XI Spec-kit for cross-cutting work | This directory. |
| XIII Engine parity | Every item lands in both engines; parity files named per item; divergences listed in §10, including the coloured-bytes divergence (plain bytes remain identical). |
| XIV Portable-core isolation | Baseline I/O, TTY detection, `anstream`, zip reading at CLI/web layer; core additions are pure; `isolation.rs` unaffected. |
| XV Single-source version | Untouched; `ruleset_version` is data provenance in catalogue.yaml (see Complexity Tracking). |

**Complexity Tracking**

| Deviation | Why needed | Simpler alternative rejected because |
|---|---|---|
| A second version-like string (`ruleset_version`) beside `VERSION` | Distributions (CRAN `-N`, CTAN identifiers) and baselines need to name the rule set independently of the tool release. | "Rule set = tool MAJOR.MINOR" gives nothing to guard a rule-set change slipping into a patch; an independent semver invites two-semver confusion. It is not a manifest version, so §XV's single-source rule is not violated. |
| Author-mode stdout is never empty any more | The "no findings ≠ compliant" statement is the point of P0-A. | Printing it only with `--verbose` would hide it from exactly the first-time user it targets; printing it on stderr would leave a saved text report of a clean run empty, which is the unearned all-clear. Exit codes remain the CI contract. |
| Coloured terminal bytes excluded from the byte-parity claim | Identical escape bytes across engines would cost a post-render parser, shared goldens, and Windows FFI for a stream nobody diffs. | §XIII allows documented divergences; the plain stream stays identical and both engines prove colour never changes layout. |
| 10 rule modules reworded in the same release as the baseline (item S) | `suggestion` is a baseline-key and fingerprint input; rewording later invalidates users' baselines. | A catalogue-flagged source-line context key (1.5 d) was measured and rejected by the maintainer: whole-line context re-keys 5 of 44 persisting findings on a heavy revision, and leaves the generic messages in place. The prototype (research.md §3) confirmed S's predicted key gain (49 → 80) and set the volume cut; `WIDTH-001` is excluded because no stable identifier exists for it. |

## 15. Deviations found during implementation

Recorded per the implementation brief: the smallest correct thing was
done and the plan detail is noted here. Nothing below changes a decision
recorded in `research.md`.

### Item D — version and rule-set provenance

| # | Plan said | Reality | What was done |
|---|---|---|---|
| D-1 | "`messages.json` is generated exactly once, after S" | The fingerprint covers `messages.json`, so item D's own `--check` and guard tests cannot pass without the file existing. D lands before S by the fixed phase order. | The generator ships in D and is run there against the pre-S wording so D's PR is internally consistent; item S regenerates it once and re-stamps the date. The **shipped** 1.2.0 `messages.json` and fingerprint are the post-S ones, which is what the constraint protects. This is also the documented user-facing workflow (quickstart "Common pitfalls"). |
| D-2 | The stamp tool "refuses when the computed fingerprint changed but the date did not" | Taken literally, a second rule-set change on the same day is unstampable: the stored date already *is* today's, so the tool would refuse forever and `--check` would stay red. | The gate is: an explicit `--ruleset-version` is **required** once the fingerprint moved, and a date may never move backwards. Re-stamping the same date is possible but never the default — the deliberate act, not the silent one, is what the policy is for. |
| D-3 | `RuleSetInfo{version, fingerprint, guide_source, recall}` | `--version` line 3 renders `2026-09-06 (jss.cls 3.3, vendored 2021-05-23)` while JSON's `guide_source` is `jss.cls 3.3 (2021-05-23)`. Storing only the joined form would mean parsing our own string back apart. | `RuleSetInfo` stores `guide_edition` and `source_vendored_at`; `guide_source` is a derived property/method in both engines. `recall` is added in item A, where it has a producer. |
| D-4 | Codegen emits `GUIDE_SOURCE` | The version line needs the two parts (D-3). | Codegen emits `RULESET_VERSION`, `RULESET_FINGERPRINT`, `GUIDE_EDITION`, `SOURCE_VENDORED_AT`, and the derived `GUIDE_SOURCE` — one generator, so no drift. |
| D-5 | (not anticipated) | `JSS-PROJECT-001`'s message quotes the *resolved* (absolute) paths of the cycle, so a raw fixture snapshot would be host-specific and the fingerprint would differ per checkout. | `generate_message_snapshot.py` strips the repository prefix; what remains is the fixture-relative path, i.e. exactly the varying part of the wording. |
| D-6 | "`JournalRuleModule.metadata()` … (item A)" | Item D needs the journal seam for `--version` line 3, and §14 forbids new lazy `journals.jss` imports in output/CLI code. | `metadata()` and `JournalMetadata` land in D carrying `rule_set` only; item A adds `recall_by_rule` and `coverage` to the same object. No shim, no temporary field. |
| D-7 | `bash r/jsslintr/tools/vendor-jsslint-core.sh` after every core change | That script refreshes the **R package's** vendored copy only. `rust/jsslint-core/specs/003-jss-rule-catalogue/` (the crate's own copy, which `build.rs` reads from a crates.io tarball and which `tests/unit/test_vendored_catalogue_in_sync.py` guards) has no script and must be copied by hand. | Both copies are refreshed; the sync test catches the omission. Worth a follow-up: fold the crate copy into the same script. |

### Item S — token-specific suggestions

| # | Plan said | Reality | What was done |
|---|---|---|---|
| S-1 | `JSS-XREF-004` gains the equation identifier | Three of its five emission sites already quote the label they are about (`_orphan_label_suggestion`, and the "label(s) … never referenced" wording). | Only the three *missing-label* sites gained the identifier; the orphan-label ones were already token-specific and were left byte-identical. The same applies to `JSS-XREF-002`, where the identifier is spliced into the existing template (`Replace '(\ref{eq:mean})' with 'Equation~\ref{eq:mean}'`) rather than appended. |
| S-2 | `JSS-CAP-002` uses the `[plain]` form when given | The rule inspects the **mandatory** `{…}` argument; quoting the optional `[plain]` variant would name a string the finding is not about. | The quoted title is the one the rule inspected. Recorded in the rule's test. |
| S-3 | `CODE-003`'s identifier is "±8 chars around the matched operator/comma" | The detection scans run on *masked* text (comments, string literals, scientific notation removed), and the old masking changed the string's length, so a match offset did not map back to the source the author wrote. | Masking is now length-preserving in both engines (same-length fill, `"S"` for string literals so `col="red"` still exposes the missing space). Detection was verified unchanged finding-for-finding — same `(rule, line, column)` set on **1 259 files / 5 081 CODE-003 findings** in `examples/` and 237 in the recall corpus (§I, §VI). |
| S-4 | `equation_identifier` rebuilds the body from nodes | pylatexenc's macro nodes swallow trailing whitespace, so a node-rebuilt body reads `X\beta+ 1`, and the Rust node model has no equivalent of `macro_post_space` to mirror it with. | Both engines slice the body out of the **source** between the first and last child node's span, which is also what the author will search for. |
| S-5 | The replay test runs against `examples/jss5342-versions/` (committed) | That directory is **gitignored** (`.gitignore:202`) — the manuscript is not redistributable. | `tests/integration/test_baseline_replay.py` skips cleanly when it is absent, exactly like the recall-corpus parity suites, and asserts counts only (no manuscript text in a committed artifact). |
| S-6 | "distinct keys ≥ 75, re-keyed ≤ 4" | The re-keyed figure in research.md §3 is measured against the **pre-item-S** key, which cannot be recomputed once the old wording is gone. | The pre-S survivor count (26) is recorded as a constant in the test, measured by running the same code against the commit before item S. Replay results: distinct keys **49 → 79** (research predicted ~80), matched `26 → 22`, i.e. **4 re-keyed** — research.md's number exactly. |

### Item B — baseline mode

| # | Plan said | Reality | What was done |
|---|---|---|---|
| B-1 | The terminal summary names both rule-set dates when they differ | The renderer had no way to know the *current* date without importing the journal, which §14 forbids. | `ComplianceReport.rule_set` is stamped by the engine in **both** engines already in item B, from the `JournalRuleModule.metadata()` seam item D built. Item A extends the same object with `recall`/`coverage` rather than introducing it. |
| B-2 | Baseline surfaces in HTML | The Jinja `{% if %}` block added a newline to *every* author/reviewer page, including runs with no baseline — caught by `config_parity.rs`, not by any Python test. | Whitespace-controlled tags (`{%- if %}` / `{%- endif %}`) so a run without a baseline is byte-identical to 1.1.0, and the Rust `baseline_note` matches the active case exactly. Verified across mode × baseline (4 combinations). |
| B-3 | `path_map` built from `document.all_files()` | `ParsedProject` has no `all_files`; it holds `documents`. | The CLI iterates `project.documents` (or the single document) — the same set the engine lints. |
| B-4 | (not anticipated) | The PyO3 wheel is built from the workspace and is *stale* after any core change, so `tests/unit/test_jsslint_parity.py` fails misleadingly until `maturin develop --release` is re-run. | Noted here for the next session: rebuild the wheel after touching `jsslint-core`, exactly as the R package needs re-vendoring. |

### Item A-recall — recall transparency

| # | Plan said | Reality | What was done |
|---|---|---|---|
| A-1 | `recall.json` holds `{corpus_hash, generated_by, min_plants, run_timestamp, rules}` | The footer wording the plan itself specifies quotes a **paper count** (`1967 annotated instances, 17 papers`), which neither `recall_history` nor the plan's snapshot shape carries. | The snapshot gains `papers`, counted from `eval/recall-corpus/*/annotations.toml` at generation time — the same way `eval-jss recall` reports it. `--papers` overrides it, and `--check` falls back to the committed value, so a machine without the gitignored corpus can still verify freshness. |
| A-2 | Codegen emits `RECALL_RUN` / `RECALL` (Python) and `build.rs` the equivalents | — | Done. The recall snapshot is deliberately **not** a fingerprint input: re-measuring recall changes what the tool *reports*, not which findings it produces, so it must not force a rule-set date bump and invalidate users' baselines. |
| A-3 | `explain` and SARIF read per-rule recall | The report carries pooled per-category recall, not per-rule; adding 53 per-rule entries to every report to serve two renderers would be the `Rule.recall` field research.md already rejected. | `explain.py`/`sarif.py` read `RECALL` from the generated catalogue module they already import. No *new* journal import (§14's actual constraint); the pre-existing lazy-import smell is unchanged. |
| A-4 | `eval/badge.py` reads `run_timestamp` and sums from the snapshot | The badge's own `PINNED_RECALL_TIMESTAMP` had already drifted from the paper's pin — the failure mode this item exists to end. | `pinned_recall_aggregate()` now reads the shipped snapshot and needs no database at all; the constant is gone. Badge and author footer cannot disagree. |
| A-5 | (not anticipated) | Two integration tests asserted a compliant run prints **nothing**. | Updated with the reason in the test itself: the findings table is still empty, and what follows it is the caveat FR-A-004 exists to add. `test_cli_json.py`'s exact key-set assertion gained `rule_set`. |

### Item A-coverage — guide coverage

| # | Plan said | Reality | What was done |
|---|---|---|---|
| AC-1 | 146 checklist rows migrate | Two of them (`CLS-039`, `CLS-040`) assert the **absence** of a macro (`\\dfn{}`, `\\file{}` are not defined in jss.cls 3.3) — reviewer findings, not provisions: nothing to check or to declare unchecked. | Dropped from the coverage file; they remain in the checklist record. 144 migrated + 5 new = **149 directives**. |
| AC-2 | "7 rows credit retired rules" | Six §1.x rows credit them (`SG-008/010/013/017/018/022`); the seventh mention is `SG-020`'s *reason*, which cites `JSS-ABBR-002`'s retirement rather than crediting it. | All six re-judged: two are now `checked` or `partial` under surviving rules, `SG-010` became the release's one honest `not_checked` caption gap, and each carries the retirement date and evidence in its reason. |
| AC-3 | The 15 unclaimed rules "mostly attach to existing rows" | They did, once each rule's own `authority_ref` was used as the map: `SG-006` (REFS-001), `SG-011` (XREF-004/005/006), `SG-017` (BIBTEX-003/005, REFS-001), plus two `jss.cls` rows that were marked out-of-scope *before* the rule enforcing them existed (`jss.cls:45` → BIBTEX-004, `jss.cls:484-487` → OPER-004). | Five provisions the checklist genuinely lacked were added: `TEX-025` (doi), `TEX-026` (journal titles), `SG-061` (spelled-out cross-reference nouns), and `AI-023`/`AI-024` (the two `internal` project rules). |
| AC-4 | Author footer prints `checks N of M` | `M` had to be defined. Counting all 149 would report "80 of 149" and read as 46 % coverage of a guide two thirds of which no source-level linter can check. | The ratio counts **checkable** provisions only (`checked + partial + not_checked` = 83); out-of-scope rows are listed by the subcommand but excluded. Documented in `docs/recall-and-coverage.md` and in the footer helper. |
| AC-6 | `vendor-jsslint-core.sh` copies the catalogue data | The script's `cp` list is hand-maintained and was missed for `guide-coverage.yaml`, so the **R package failed to build** while everything else was green. | Fixed, with a comment naming the two other lists that must stay in step (`_FILES` in the sync test, `REQUIRED` in `package_contents.rs`). The new `package_contents.rs` catches the crates.io half of the same failure mode. |
| AC-5 | `coverage --format json` includes the `sources` block | The Rust CLI must work from a crates.io install with no repository around it, so it cannot read the YAML at runtime. | Python reads the file; Rust compiles the same four entries in. Both outputs are byte-identical (`coverage_parity.rs`), and the pair is small and dated — if it drifts, the parity test says so. |

### Environment

- `.venv-host` is the **macOS host's** venv (`/workspace` is a bind mount
  of the host checkout, so the two share one directory): its interpreter
  symlinks to `/opt/homebrew/opt/python@3.14` and cannot execute in a
  Linux container. Rebuilding it from a container would destroy the
  host's. **Fixed** by making the consumers pick an interpreter that
  runs: `paper/Makefile` and `paper/regenerate.sh` prefer `.venv-host`
  only when it is executable and fall back to `.venv`, and `CLAUDE.md`
  states which venv belongs to which environment. `.venv` (CPython
  3.11.2) is what every gate below was run with.
- **`--version` consumers found and fixed in the same pass**:
  `paper/regenerate.sh` parsed the old one-liner with
  `sed 's/.*version //'` and `paper/replicate.sh` took the last token of
  the whole output — both broke on the new four-line block (the latter
  would have compared against `jss`, from `journal: jss`). Both now take
  the last token of **line 1**, which is correct for the pre-1.2.0
  `jss-lint, version X.Y.Z` form and the new `jss-lint X.Y.Z` alike —
  `replicate.sh` needs that, since it validates a released tool that may
  still print the old format.
- The §IX coverage command measured 17 % because the rule unit tests
  lived in `tests/unit/rules/` while two of them
  (`test_helpers.py`, `test_project.py`) already sat under
  `tests/unit/journals/jss/rules/`. **Fixed** by moving the other 16
  there, so the test tree mirrors `src/texlint/journals/jss/rules/` and
  the documented command measures the right thing;
  `scripts/eval-category.sh` and `CLAUDE.md` follow. Specs 003–005 still
  name the old path as a historical record.
- Even measured correctly, the gate does **not** pass: branch coverage
  on the rule modules is **90.2 %** (`tests/unit/journals/jss/`) /
  93.3 % (whole suite), and every one of the 16 modules is below 100 %
  — on the untouched branch, before any 1.2.0 code, and no CI job runs
  it. Agreed reading for item S (maintainer, 2026-09-07): every branch
  item S *adds* must be covered and no module's coverage may regress;
  each touched module's before/after number is reported with the item.
  Item S's outcome, `tests/unit/journals/jss/` before → after:
  `_helpers` 98 → 98, `capitalization` 85 → 86, `citations` 92 → 92,
  `code_style` 94 → 94, `crossrefs` 86 → 88, `operators` 87 → 88,
  `references` 91 → 94, `typography` 96 → 96; total 90 → 91 %. No
  module regressed and the only new uncovered branches found
  (`equation_identifier`'s label fall-throughs) were covered before the
  item closed.
