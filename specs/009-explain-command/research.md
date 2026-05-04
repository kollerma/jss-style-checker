# Research: `jss-lint explain` Subcommand

**Phase**: 0
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

---

## 1. CLI shape — Click group default action vs. `lint` subcommand

**Decision**: Migrate `jss-lint` to a `click.Group` with the
existing read-only lint as the **default group action** (the
`@cli.command()` registered without an explicit invocation
name, or via `invoke_without_command=True` plus a
`pass_through` handler). The new `explain` subcommand is a
peer; existing `jss-lint <PATHS>` calls continue to work
verbatim.

**Rationale**:
- Spec Clarifications resolved this: a `lint` explicit
  subcommand would force every CI script and editor
  integration to update its invocation.
- Click supports default-action groups. The migration is a
  ~30-line edit in `cli.py`.

**Alternatives considered**:
- `lint` explicit subcommand: rejected per Clarifications.
- Two separate binaries (`jss-lint`, `jss-lint-explain`):
  rejected — packaging surface inflation, and the explain
  binary would still need access to the catalogue.

---

## 2. Renderer — `rich` vs. plain string

**Decision**: Use `rich` (already a dep) for the terminal
format. Markdown format is a plain `str.format`-based template
in `src/texlint/explain.py`. No new template engine.

**Rationale**:
- `rich` is already used by `output/terminal.py`; reusing it
  keeps the styling coherent.
- Markdown does not need styling, just structure; a plain
  template is the smaller surface.

**Alternatives considered**:
- `jinja2` for both formats: rejected — overkill for a small
  static template.
- `colorama`: rejected — already covered by `rich`.

---

## 3. Listing view paging

**Decision**: No paging. Output goes directly to stdout. Users
who want paging pipe through `less`.

**Rationale**:
- Spec Clarifications resolved this. The catalogue is ~58
  lines today; paging overhead is larger than the rendered
  text.
- The existing `jss-lint <PATHS>` does not page; consistency
  matters.

**Alternatives considered**:
- Auto-page when stdout is a TTY (like `git log`): rejected
  per Clarifications. Also breaks `jss-lint explain | grep`
  workflows by default.
- Add `--pager` / `--no-pager` flags: rejected — feature
  bloat for a small output.

---

## 4. `did-you-mean?` for unknown rule id

**Decision**: Use `difflib.get_close_matches(unknown_id,
catalogue_ids, n=5, cutoff=0.6)`. If the result is empty,
fall back to listing rule ids in the same category prefix
(e.g., for `JSS-CITE-999`, suggest all `JSS-CITE-*` rules).

**Rationale**:
- `difflib` is stdlib; no new dep.
- `cutoff=0.6` matches "a typo or two" but rejects
  unrelated guesses.
- The category-prefix fallback covers the case where the
  user remembers the category but not the number.

**Alternatives considered**:
- Levenshtein library (`python-Levenshtein`): rejected —
  new dep for a stdlib-equivalent capability.
- Soundex / metaphone: rejected — rule ids are alphanumeric
  with hyphens, phonetic matching is poor.
- BK-tree from scratch: rejected — Constitution §X.

---

## 5. Fixture pull-through path resolution

**Decision**: For `--example`, look up
`tests/fixtures/violations/<RULE-ID>-bad.tex` first; if
absent, try `.Rnw` then `.Rmd` (in that order). If none
exists, emit the literal `(no in-corpus fixture)`.

**Rationale**:
- `.tex` is the dominant format; checking it first is the
  common path.
- `.Rnw` / `.Rmd` (spec 005) extend the corpus; Rmd-only
  rules need their fixture pulled through.
- The sentinel literal matches the spec's edge-case
  contract.

**Alternatives considered**:
- Glob across all suffixes and pick the first match:
  rejected — non-deterministic if multiple exist.
- Require a sidecar `.example.tex` per rule: rejected —
  doubles fixture maintenance.

---

## 6. Backfill strategy for `explanation`

**Decision**: One mechanical PR-author pass over the
catalogue at spec-009 implementation time. Each rule's
`explanation` is a single paragraph (≤120 words) referencing
the JSS-guide section from spec 007. The PR author writes
each by hand; no automation generates them.

**Rationale**:
- 58 rules × ~80 words each ≈ 4-5 hours of writing — within
  one focused work session for a contributor familiar with
  the JSS guide.
- Generated explanations would risk hallucinated content;
  hand-written is the correct level of effort for prose
  shipped to authors.

**Alternatives considered**:
- LLM-generated drafts for human review: out of scope; the
  spec is about the explainer infrastructure, not about
  prose generation.
- Per-rule incremental rollout with a TODO sentinel:
  rejected per Clarifications.

---

## 7. Markdown format — fenced code block language

**Decision**: Use `tex` as the language tag for code
fences in markdown output. For Rmd rules, use `rmarkdown`.
For Rnw rules, use `tex` (the surrounding LaTeX).

**Rationale**:
- GitHub's CommonMark renderer recognises `tex` and
  `rmarkdown`; both syntax-highlight reasonably.
- Picking one language per rule (rather than per fragment)
  keeps the output simple.

**Alternatives considered**:
- No language tag (raw fence): rejected — loses syntax
  highlighting on GitHub.
- Per-fragment auto-detect: rejected — overhead for
  marginal value.

---

## 8. ASCII vs. Unicode in terminal output

**Decision**: Allow Unicode in the terminal format
(`§`, `→`, en-dashes). The fallback for non-Unicode
terminals is the user's responsibility (set `PYTHONIOENCODING=utf-8`
or pipe to a saner pager); the existing
`output/terminal.py` already emits Unicode without
issue.

**Rationale**:
- The JSS guide section labels include `§`; ASCII-fying
  them would lose information.
- All major modern terminals are UTF-8 capable.

**Alternatives considered**:
- ASCII-only mode: rejected — information loss.
- Auto-detect terminal encoding: rejected — overhead for
  a rare case.

---

## Summary

All eight decisions follow from spec Clarifications and
Constitution §I, §III, §IV, §X. No remaining `NEEDS
CLARIFICATION`. Ready for Phase 1.
