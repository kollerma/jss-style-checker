# Feature Specification: Auto-fix (`--fix` / `--dry-run` / `--apply`)

**Feature Branch**: `008-auto-fix`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Add three CLI flags to `jss-lint`: `--fix` (apply all available fixes in place, atomic write), `--dry-run` (print proposed fixes as a unified diff but do not write — requires `--fix`), and `--apply` (interactive hunk-by-hunk walk-through, `y/n/all/quit` per fix). Introduce a `Fix` dataclass on `Violation` (text edit, fix description, confidence level). Each rule module that supports auto-fix populates `fix=Fix(...)` on the violations it yields; rules without a deterministic fix yield `fix=None`. The engine groups fixes per file, applies them in reverse-position order, validates the rewritten file no longer re-triggers the same rule, and rolls back atomically on failure. Add `--fix-rule RULE-ID` (repeatable) to scope fixes to specific rules. Default behaviour with no flag is unchanged (read-only)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Apply all available fixes with one flag (Priority: P1)

A JSS author has a manuscript with two dozen mechanical violations
— missing `\pkg{}` wrappers, mis-cased package names, citation
style errors. Instead of fixing each by hand, the author runs
`jss-lint --fix manuscript.tex`. Every fix that the linter has
classified as `safe` is applied to the file; the result is
re-linted automatically; the author sees a short summary
(`12 fixes applied, 8 remaining`).

**Why this priority**: P1 because mechanical-violation cleanup is
the single highest-value author UX. Without `--fix`, the linter
is an inspection tool; with it, it's a copy-editor.

**Independent Test**: Given a fixture `.tex` file with three
violations whose rules ship `Fix` payloads, `jss-lint --fix
fixture.tex` rewrites the file with all three fixes applied and
exits 0; the rewritten file lints clean for those three rules.

**Acceptance Scenarios**:

1. **Given** a fixture with one `JSS-CITE-003` violation that has
   `fix=Fix(...)`, **When** `jss-lint --fix fixture.tex` runs,
   **Then** the file content matches a stored "after" golden
   byte-for-byte.
2. **Given** a fixture with three violations across three rules,
   all with `Fix` payloads, **When** `jss-lint --fix fixture.tex`
   runs, **Then** all three fixes are applied and the post-fix
   re-lint reports zero `(rule_id, line)` regressions for those
   three rules.
3. **Given** a fixture with one violation whose `fix is None`,
   **When** `jss-lint --fix` runs, **Then** that violation is
   left in the source and the exit summary mentions `1
   remaining` (un-fixed).
4. **Given** a fixture with no fixable violations, **When**
   `--fix` runs, **Then** the file is not rewritten (no temp file
   replacement) and exit code is 0.

---

### User Story 2 - Preview fixes as a diff before applying (Priority: P1)

The same author wants to see what `--fix` would change without
touching the file. They run `jss-lint --fix --dry-run
manuscript.tex` and get a unified-diff preview on stdout. They
review, decide the fixes look right, and re-run without
`--dry-run` to apply.

**Why this priority**: P1 because trust gates adoption. An
author who can preview the diff is far more likely to enable
`--fix` in their workflow than one who must apply blind.

**Independent Test**: `jss-lint --fix --dry-run fixture.tex`
prints a unified diff to stdout and does NOT modify
`fixture.tex` on disk.

**Acceptance Scenarios**:

1. **Given** a fixture with one fixable violation, **When**
   `jss-lint --fix --dry-run fixture.tex` runs, **Then** stdout
   contains a unified-diff hunk reflecting the proposed edit AND
   `fixture.tex` content on disk is byte-identical before and
   after the run.
2. **Given** the same fixture, **When** the dry-run output is
   piped to `patch`, **Then** the patched file matches the
   golden "after" file byte-for-byte.
3. **Given** `--dry-run` without `--fix`, **When** the user runs
   the linter, **Then** the CLI exits with code 2 and stderr
   contains `--dry-run requires --fix`.

---

### User Story 3 - Interactive walk-through with per-fix consent (Priority: P2)

A cautious author runs `jss-lint --fix --apply manuscript.tex`.
The linter steps through fixes one at a time, showing the
unified-diff hunk for each, and prompts `[y]es / [n]o /
[a]ll / [q]uit`. The author skips two fixes that look wrong
and accepts the rest.

**Why this priority**: P2 because the dry-run + bulk-apply path
covers most workflows, but interactive review is the right tool
for the first-time `--fix` user who doesn't yet trust the
tool. Important enough to ship in this spec but not gating.

**Independent Test**: A scripted interaction with stdin feeding
`y\nn\na\n` accepts the first, skips the second, and bulk-
accepts the remaining fixes; the resulting file matches a
golden "after-with-skip" fixture.

**Acceptance Scenarios**:

1. **Given** a fixture with three fixable violations, **When**
   `jss-lint --fix --apply` runs with stdin `y\ny\ny\n`,
   **Then** the file matches the golden "all-applied" fixture.
2. **Given** the same fixture with stdin `y\nn\na\n`, **When**
   the user runs the command, **Then** fix 1 is applied, fix 2
   is skipped, fix 3 is applied (the `a`/all takes effect for
   remaining), and the file matches a "skip-second" golden.
3. **Given** stdin `q\n` at the first prompt, **When** the user
   runs the command, **Then** no edits are applied and exit
   code is 0.

---

### User Story 4 - Scope `--fix` to a single rule (Priority: P2)

A maintainer is reviewing a PR and only trusts auto-fix for one
specific rule today. They run `jss-lint --fix --fix-rule
JSS-CITE-003 manuscript.tex` to apply only `JSS-CITE-003`
fixes; everything else is untouched.

**Why this priority**: P2 because per-rule scoping is the
pragmatic on-ramp for "I trust this one fix, not all of them".
Without it, adoption is binary.

**Independent Test**: Given a fixture with violations from
three different rules each carrying `Fix`, running `--fix
--fix-rule JSS-CITE-003` modifies only `JSS-CITE-003`-related
text and leaves the other two violations in place.

**Acceptance Scenarios**:

1. **Given** the fixture above and `--fix-rule JSS-CITE-003`,
   **When** the linter runs, **Then** the resulting file matches
   a "cite-003-only" golden.
2. **Given** `--fix-rule JSS-CITE-003 --fix-rule JSS-NAME-001`,
   **When** the linter runs, **Then** both rules' fixes are
   applied (the flag is repeatable).
3. **Given** a `--fix-rule` value that does not match any
   catalogue rule, **When** the linter runs, **Then** the CLI
   exits with code 2 and stderr names the unknown rule.

---

### User Story 5 - Atomic write and rollback on regression (Priority: P1)

A fix is buggy: applying it triggers another violation of the
same rule (the rewriter introduces the violation it was supposed
to fix). The engine detects the regression by re-linting the
rewritten content, rolls the file back to its original state,
and surfaces the offending fix in the exit summary.

**Why this priority**: P1 because a corrupting auto-fix is worse
than no auto-fix. The repository is the user's truth; we must
not damage it.

**Independent Test**: A test fixture with a deliberately-buggy
`Fix` whose `replacement` text re-trips its own rule. Running
`--fix` results in (a) the file unchanged on disk byte-for-
byte, (b) a non-zero exit code, (c) a stderr message naming the
rule and the rejected fix.

**Acceptance Scenarios**:

1. **Given** a buggy `Fix` that re-triggers its own rule when
   applied, **When** `--fix` runs, **Then** the file content on
   disk is byte-identical before and after.
2. **Given** the same fixture, **When** the linter exits,
   **Then** the exit code is non-zero (rejected fixes are an
   error condition) AND stderr contains the rule id and the
   word `rejected`.
3. **Given** a write that fails partway (simulated permission
   error), **When** the engine writes via tempfile + os.replace,
   **Then** the original file is intact and the temp file is
   cleaned up.

---

### Edge Cases

- Two rules propose edits whose byte ranges overlap: the engine
  picks deterministic winners by `(confidence, rule_id, line,
  column)`, applies the winner, and records the loser as
  `skipped` in the exit summary (per Clarifications, see
  research.md `§1`).
- A fix's `replacement` text is identical to the existing
  text (no-op): the engine elides it (no rewrite).
- Two fixes within the same line, non-overlapping: both apply
  (reverse-position order).
- A file is read-only: `--fix` exits with code 2; `--dry-run`
  succeeds (it doesn't write).
- A file is in a working tree with uncommitted git state:
  `--fix` proceeds as normal (the tool does not check git
  state).
- The user's editor has an unsaved buffer for the file:
  out-of-scope; we trust on-disk state.
- An interactive prompt receives EOF before a fix is decided:
  treat as `q` (quit, no edits applied).
- `--fix` with `--output sarif`: the SARIF document still
  reflects the *pre-fix* state; the renderer is read-only.
  (Spec 008's SARIF integration is `runs[0].results[].fixes[]`,
  see FR-009.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new `Fix` dataclass MUST be added with fields
  `(start: int, end: int, replacement: str, description: str,
  confidence: Literal["safe", "review"])`. `start` / `end` are
  byte offsets into the source file (0-based, half-open).
  `replacement` is the literal string to substitute. The fix is
  language-agnostic at this layer — rules describe text edits.
- **FR-002**: `Violation` MUST gain an additional optional
  field `fix: Fix | None = None`. Existing rules continue to
  yield `fix=None` until they are individually upgraded.
- **FR-003**: `--fix` MUST apply every available `Fix` (subject
  to `--fix-rule` scoping and confidence policy) atomically to
  the source file: a single `tempfile` write followed by
  `os.replace()`. Partial writes MUST be impossible.
- **FR-004**: `--dry-run` MUST require `--fix`. Without
  `--fix`, the CLI MUST exit with code 2 and a stderr error
  message. With `--fix --dry-run`, the linter MUST print a
  unified diff to stdout and MUST NOT write to disk.
- **FR-005**: `--apply` MUST require `--fix`. With both flags,
  the linter MUST step through fixes one at a time, showing
  the unified-diff hunk and prompting `[y/n/a/q]`. `y` accepts
  this fix; `n` skips it; `a` accepts this and all remaining;
  `q` quits without applying further fixes (already-accepted
  fixes are still applied at exit).
- **FR-006**: `--fix-rule RULE-ID` MUST be repeatable. When
  one or more `--fix-rule` values are provided, only fixes for
  those rules are eligible to apply; other fixes are left in
  place. An unknown rule id MUST cause exit code 2 with a
  stderr error.
- **FR-007**: The engine MUST group fixes per file and apply
  them in reverse-position order (largest `start` first) so
  earlier offsets are not shifted by later edits. Fixes for
  different files are independent.
- **FR-008**: After applying fixes for a file, the engine MUST
  re-parse and re-lint the rewritten content. If any
  `(rule_id, line)` that was supposed to be fixed re-appears in
  the post-fix report, the engine MUST roll back the file to
  the pre-fix state via the original tempfile mechanism (the
  rewrite is reverted by replacing with the originally-cached
  bytes), MUST log the rejected fix to stderr, and MUST exit
  with code non-zero.
- **FR-009**: When `--fix` is combined with `--output sarif`,
  the SARIF document MUST emit `runs[0].results[].fixes[]` for
  every applicable fix (whether or not it was actually
  written). This activates the deferral noted in spec 006
  FR-015.
- **FR-010**: Default behaviour (no fix flags) MUST be
  unchanged: read-only lint, no on-disk modifications. The
  presence of a `Fix` payload on a violation is not visible in
  the existing terminal / JSON / HTML output unless an explicit
  flag enables it.
- **FR-011**: Conflict resolution: when two fixes propose
  overlapping byte ranges in the same file, the engine MUST
  pick a single winner by ordering on
  `(confidence, rule_id, start, end)` ascending — `safe`
  beats `review`; among same-confidence, the lexicographically
  smallest `rule_id` wins; ties further break on byte range.
  The losing fix MUST be skipped, listed in the exit summary,
  and recorded as `skipped` (not `rejected` — that is reserved
  for FR-008 regression failures).
- **FR-012**: Re-prompting policy: `--apply` re-prompts after
  every accepted fix until `a` is pressed. There is no
  per-rule batch mode in this spec.
- **FR-013**: Rules opt into auto-fix incrementally; there is
  no requirement for every rule to ship a `Fix`. The catalogue
  contract test from spec 007 is unchanged. A rule has
  auto-fix support iff its emitted violations carry
  `fix is not None`; this is observable from the catalogue
  introspection only at runtime.
- **FR-014**: Exit codes:
  - `0`: clean run OR `--dry-run` produced suggestions OR
    `--fix` applied N fixes successfully.
  - `1`: violations remain after `--fix` (or no fix flag was
    used and violations exist).
  - `2`: usage error, including
    `--dry-run` without `--fix`, unknown `--fix-rule`,
    permission errors writing the file, and FR-008 regression
    failures.
- **FR-015**: User-input fixes (rules where the correct
  replacement requires human judgement, e.g., "expand this
  abbreviation") MUST set `fix=None`. The catalogue's
  `description` field for the rule MAY include guidance for
  the human author. There is no "interactive fix authoring" UX
  in this spec.

### Key Entities

- **Fix**: A self-contained text edit: byte range + replacement
  string + human-readable description + confidence level. The
  rule's contribution to auto-fix.
- **Violation (extended)**: Existing dataclass; gains
  `fix: Fix | None = None`. No other fields change.
- **Apply mode**: Tri-valued runtime mode: `"write"` (default
  with `--fix`), `"dry-run"`, `"interactive"`. The CLI parses
  flags into this mode and passes it to
  `core/fixer.py::apply_fixes`.
- **Confidence**: Two-valued enum-like literal:
  - `safe` — the fix is mechanical and verified by re-lint;
    e.g., wrap a known package name in `\pkg{}`.
  - `review` — the fix is plausible but the rule's authors
    flagged it for human review; the engine still applies it
    in `--fix` mode unless the user filters by confidence in a
    future spec.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `--fix` on a fixture with N safe-confidence
  fixes results in N applied edits and zero on-disk corruption
  (the file is byte-identical to the golden "after" file).
- **SC-002**: Running `--dry-run` on the same fixture leaves
  the file byte-identical on disk and prints a unified diff
  whose application via `patch` produces the golden "after"
  file.
- **SC-003**: A buggy fix (one that re-triggers its own rule
  when applied) results in zero corruption: the file is
  byte-identical before and after the run.
- **SC-004**: When two rules propose overlapping fixes, exactly
  one fix is applied (the deterministic winner per FR-011) and
  the loser is reported in the exit summary.
- **SC-005**: Default no-flag behaviour is unchanged: every
  pre-spec-008 test for terminal / JSON / HTML / SARIF output
  passes (modulo the spec-006 SARIF `fixes[]` activation).
- **SC-006**: At least three catalogue rules ship with `Fix`
  payloads in this spec (per the plan input: `JSS-CITE-003`,
  `JSS-NAME-001`, `JSS-CAP-002` or equivalents); each has a
  golden-fixture pair (`before.tex`, `after.tex`).

## Assumptions

- The `confidence` literal has two values in this spec.
  `--fix` applies both; a hypothetical `--fix-only safe` flag
  is out of scope (revisit if `review` confidence proves noisy
  in practice).
- The interactive prompt reads from stdin and writes to
  stderr. Tests inject stdin via `subprocess.PIPE` or pytest's
  `monkeypatch`. There is no curses / readline integration.
- `os.replace()` is atomic on POSIX and on Windows for files
  on the same volume. The tempfile lives in the same parent
  directory as the target file, so cross-volume moves do not
  occur.
- The pre-fix bytes are cached in memory before the rewrite,
  so rollback is a second `tempfile + os.replace` write of
  the original bytes. Files large enough to be a memory
  concern are out of scope (JSS manuscripts are KB-scale).
- A rule's `Fix` is computed once at violation-emission time;
  the engine does not call back into the rule. If the
  rewritten file's surrounding context invalidates the fix,
  re-lint catches it (FR-008).
- Fixes are byte-range based, not AST-position based. Rules
  compute byte offsets from pylatexenc node positions; this
  conversion is the rule author's responsibility.
- `--apply` is single-key prompts (`y/n/a/q`). Multi-character
  responses are rejected with a re-prompt; EOF is treated as
  `q` (per Edge Cases).
- `--fix` does not commit to git, does not stash, does not
  back up to `.bak`. The user's working copy is the user's
  truth; we offer dry-run as the preview path.
