# Contract: Token-specific suggestions (item S)

**Plan**: [../plan.md](../plan.md) §5A, §5.7
**Research**: [../research.md](../research.md) (prototype results)

## C-1 Purpose

`suggestion` is a baseline-key component (`baseline-file.md` C-2) and,
through `messages.json`, a fingerprint input (`data-model.md` §4.4). A
suggestion that reads the same for every occurrence of a rule in a file
makes those findings interchangeable to the baseline. The rules below
gain a stable identifier so that a finding's key changes only when the
violation itself changes. This lands **before** any baseline can be
written and before `messages.json` is generated.

## C-2 Scope — exactly ten rules

| Rule | Identifier appended to the suggestion | Source of the identifier |
|---|---|---|
| `JSS-CODE-003` | the offending fragment: 8 characters either side of the matched operator or comma | matched span in the code line |
| `JSS-OPER-003` | the equation's `\label{…}` argument if present, else the first 40 characters of the equation's first body line | enclosing display-math environment |
| `JSS-XREF-004` | same rule as `OPER-003` | enclosing display-math environment |
| `JSS-TYPO-001` | first 40 characters of the caption text | `\caption{…}` argument |
| `JSS-REFS-004` | the BibTeX entry key | parsed entry |
| `JSS-REFS-007` | the BibTeX entry key | parsed entry |
| `JSS-CAP-002` | the section title, at most 60 characters | `\section`/`\subsection`/`\subsubsection` argument (plain form when `[plain]` is given) |
| `JSS-CODE-001` | first 40 characters of the comment text (after the comment marker) | the code comment |
| `JSS-XREF-002` | the referenced label | `\ref{…}`/`\eqref{…}` argument |
| `JSS-CITE-003` | the cite key(s) of the matched `\cite…{…}` | citation argument |

Wording pattern: the existing sentence, then the identifier in single
quotes introduced by a fixed preposition, e.g.
`Use sentence style in 'Robust Methods For Mixed Models'.`,
`Add a \label{} inside the equation 'y = X\beta + \epsilon'.`,
`Capitalize the principal words of the journal title in entry 'koller2023'.`
The exact template per rule is fixed in the rule's unit test and mirrored
in Rust.

## C-3 Normalisation (identical in both engines)

- Collapse runs of whitespace (including newlines) to one space; trim.
- Truncate to the stated length **after** collapsing; no ellipsis is
  appended (a fixed length keeps keys stable under trailing edits).
- No escaping and no case folding: the identifier is the source text as
  written, so `\beta` stays `\beta` and `MATLAB` stays `MATLAB`.
- Empty identifier (e.g. an empty caption) → the suggestion is emitted
  without the appended clause (falls back to the generic wording).

## C-4 Out of scope by decision

| Rule(s) | Decision | Reason |
|---|---|---|
| `JSS-WIDTH-001` | stays generic | Line content and the measured width change on every edit to a long line; the enclosing chunk/environment key gave no measurable benefit on the real revision rounds (plan §5A, research.md). Same-shape masking on this rule is accepted and documented (`baseline-file.md` C-8). |
| `REFS-005`, `REFS-006`, `NAME-002`, `HOUSE-002`, `BIBTEX-003/004/005` (entry key), `TYPO-004`, `XREF-006` | deferred | Together they remove < 5 % of the masking-prone findings in the 30-paper audit; landing them later is a documented rule-set bump. |
| `MARKUP-001`, `MARKUP-003`, `OPER-001`, `OPER-004`, `CODE-002`, `REFS-003` | unchanged | Already quote the token; repeats of the same token are inherent. |

## C-5 Engine parity and gates

- Python reference first (Constitution §VIII: the new suggestion test is
  committed failing), Rust port second; suggestion bytes identical
  (`tex_rules_parity.rs`, `bib_rules_parity.rs`, `engine_parity.rs`).
- Every touched Python rule module keeps 100 % branch coverage (§IX).
- `message` text is unchanged; only `suggestion` changes.
- Detection is unchanged (§I, §VI): no finding appears or disappears.

## C-6 Consequences

- Rule-set bump: item S is a rewording under D4, so 1.2.0 carries a new
  `ruleset_version`; `messages.json` is generated after S so the
  fingerprint reflects the final wording.
- SARIF goldens (`tests/fixtures/sarif/golden_*.sarif`) embed message and
  suggestion text and are regenerated once after S.
- `eval-jss iterate refresh` label restoration must be verified to key on
  `(rule, file, line)` before S lands, so precision history is not
  orphaned.
- Users see more specific suggestions; JSON `suggestion` strings change
  for these ten rules only.

## C-7 Regression test

`tests/integration/test_baseline_replay.py` replays
`examples/jss5342-versions` initial → resubmission with a baseline built
on the initial version and asserts the matched/stale/new counts and the
distinct-key count recorded in `research.md` for the final S scope.
