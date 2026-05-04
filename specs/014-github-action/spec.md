# Feature Specification: Reusable GitHub Action

**Feature Branch**: `014-github-action`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Ship a reusable composite GitHub Action and publish it as `kollerma/jss-style-checker-action@v1`. Inputs: `paths` (default: auto-detected `.tex` / `.rnw` / `.rmd`), `journal` (default `jss`), `fail-on-severity` (default `error`), `comment-mode` (`pr-review` | `pr-comment` | `none`), `upload-sarif` (default `true`), `python-version`. Behaviour: pip-install the latest release (or a pinned `version` input), run `jss-lint --output sarif` on `paths`, upload SARIF via `github/codeql-action/upload-sarif@v3`, and for `comment-mode=pr-review` post a single review with one comment per violation grouped by file. Action exits with `fail-on-severity` honoured. Publish docs as a `README.md` next to `action.yml`."

## Clarifications

### Session 2026-05-03

- Q: Do we own a separate `kollerma/jss-style-checker-action` repo (Marketplace canonical) or vendor it inside the main repo? → A: Inside the main repo at `action/action.yml`. The Marketplace accepts both repo layouts; co-locating with the Python package keeps the Action's smoke-test workflow in lock-step with the linter's changes. The Marketplace listing's "uses" string remains `kollerma/jss-style-checker-action@v1` — handled by publishing the Action under that org/name via a release workflow, even though the source lives in the main repo.
- Q: `fail-on-severity` semantics — `error` blocks merge; what about `warning` — configurable threshold count? → A: No threshold count in v1. `fail-on-severity: warning` causes ANY warning to fail the run; `fail-on-severity: error` causes ANY error to fail. Threshold-by-count is a feature with thin demand and would multiply the input surface; if a real user asks, a follow-up spec adds `fail-on-count: <n>`.
- Q: Does PR-review-mode dedupe violations across runs (resolves stale comments) or always create fresh? → A: Dedupe. The Action lists prior reviews authored by the workflow's bot user (typically `github-actions[bot]`); for each, it dismisses the review with a `dismissalReason: "outdated"` before posting the new review. This keeps the PR conversation history clean across many force-pushes.
- Q: Tag/release strategy — a `v1` rolling tag + immutable `v1.0.0` semver, or only semver? → A: Both. Rolling `v<MAJOR>` for "I always want the latest stable v1.x"; immutable `vX.Y.Z` for pinning. The release workflow updates the rolling tag automatically on every semver release that is itself a v1.x.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Drop-in PR linting (Priority: P1)

A JSS author maintains their manuscript on GitHub. They add the
following job to `.github/workflows/jss-lint.yml`:

```yaml
- uses: kollerma/jss-style-checker-action@v1
```

On every PR, the Action installs the linter, runs it on
auto-detected `.tex` / `.Rnw` / `.Rmd` files, uploads SARIF to
the Security tab, and posts a single review with one inline
comment per violation. The author and reviewers see the
findings directly on the PR diff.

**Why this priority**: P1 because the GitHub-side review surface
is what makes the linter visible to JSS desk editors and
co-authors. Without the Action, every contributor must install
the linter locally.

**Independent Test**: Open a PR in a test repo using the Action.
Confirm: the workflow runs to completion, the Security tab shows
the SARIF artefact, and the PR has one review with one comment
per violation.

**Acceptance Scenarios**:

1. **Given** a manuscript repo with the Action wired in,
   **When** a PR introduces one new style violation, **Then**
   the workflow run posts exactly one review comment on the
   violating line with the rule id and message.
2. **Given** the same setup, **When** the workflow uploads
   SARIF, **Then** the Security tab's code-scanning view
   shows the violation under "jss-lint".
3. **Given** the workflow re-runs on the same PR (e.g.,
   second push), **When** the review-creation step executes,
   **Then** prior `jss-lint` review comments are dismissed (or
   updated — see Clarifications §3).

---

### User Story 2 - Configurable failure threshold (Priority: P1)

The author wants the Action to fail the PR check only on
`error`-severity violations; `warning` and `info` should
surface but not block merge. They set
`fail-on-severity: error` (the default).

**Why this priority**: P1 because every team has different
strictness norms. A blocking failure on every warning is
hostile; a never-fails action is invisible. Configurability
gates adoption.

**Independent Test**: Two test runs, one with
`fail-on-severity: error` and one violation of severity
`warning`; the first should pass (exit 0), the second should
fail (exit 1) when the severity is bumped to `error`.

**Acceptance Scenarios**:

1. **Given** `fail-on-severity: error` and zero error
   violations (warnings only), **When** the Action runs,
   **Then** exit code is 0 and the PR check passes.
2. **Given** `fail-on-severity: error` and one error
   violation, **When** the Action runs, **Then** exit code
   is 1 and the PR check fails.
3. **Given** `fail-on-severity: warning`, **When** the
   Action runs against a buffer with one warning, **Then**
   exit code is 1.

---

### User Story 3 - SARIF upload to the Security tab (Priority: P1)

Every run of the Action uploads its SARIF artefact via the
official `github/codeql-action/upload-sarif@v3` action. The
violations appear in the Security tab's code-scanning view,
where editors can browse them across all PRs in the repo.

**Why this priority**: P1 because the Security tab is the
canonical GitHub surface for static-analysis results; it's
what reviewers and editors will look at when triaging a
submission.

**Independent Test**: After a workflow run, the SARIF
artefact appears in the run's artefact list, AND the
Security tab's code-scanning view shows the violation.

**Acceptance Scenarios**:

1. **Given** `upload-sarif: true` (the default), **When**
   the Action runs, **Then** an artefact named
   `jss-lint.sarif` is attached to the workflow run.
2. **Given** `upload-sarif: false`, **When** the Action
   runs, **Then** no SARIF artefact is uploaded; the
   inline comments still appear (if `comment-mode` is
   `pr-review`).

---

### User Story 4 - Suppress comments via `comment-mode: none` (Priority: P2)

A maintainer using the Action only for the SARIF surface
sets `comment-mode: none`. The PR has no review comments;
the Security tab still shows the violations.

**Why this priority**: P2 because review comments can be
noisy on large PRs; some teams prefer the Security tab as
the single triage view.

**Independent Test**: A run with `comment-mode: none`
produces no review comments and (when
`upload-sarif: true`) still uploads SARIF.

**Acceptance Scenarios**:

1. **Given** `comment-mode: none`, **When** the Action
   runs against a PR with violations, **Then** no review
   is created, no per-file comments are added.
2. **Given** the same setting and `upload-sarif: true`,
   **When** the Action runs, **Then** the SARIF
   artefact is still produced and uploaded.

---

### User Story 5 - Pin a version (Priority: P2)

A reproducibility-conscious author pins
`uses:
kollerma/jss-style-checker-action@v1.5.0` to lock to an
immutable semver. They also pin
`with: { version: 0.5.0 }` to lock the underlying Python
package.

**Why this priority**: P2 because pinning is best practice
for production CI; the rolling `@v1` tag is fine for most
users but explicit pinning prevents surprise regressions.

**Independent Test**: A workflow pinned to
`@v1.5.0` and `version: 0.5.0` runs deterministically; a
re-run hours later uses the same Action code and the same
linter version.

**Acceptance Scenarios**:

1. **Given** `kollerma/jss-style-checker-action@v1.5.0`
   and `with: { version: 0.5.0 }`, **When** the Action
   runs, **Then** it installs `jss-lint==0.5.0` from PyPI
   and uses it.
2. **Given** `with: { version: latest }` (the default),
   **When** the Action runs, **Then** the most recent PyPI
   release is installed.

---

### Edge Cases

- A PR with no `.tex` / `.Rnw` / `.Rmd` files: the Action
  skips the lint step (no violations, exit 0); no SARIF
  upload; no comments.
- The PR comes from a fork (no write permission to the head
  repo): review comments still post (the Action runs in the
  base repo's context for `pull_request_target`); SARIF
  upload still works.
- `paths` is set explicitly to a non-existent path: the
  Action exits 2 (usage error) with a clear log line.
- `python-version` not set: the Action defaults to a pinned
  recent stable (`3.12`).
- `version` is set to a yanked PyPI version: pip raises;
  the Action exits 2.
- The user provides BOTH `paths` and a `paths-from`
  pattern: the explicit `paths` wins.
- The repo has nested workspaces (`papers/jss-2026-foo/`,
  `papers/jss-2026-bar/`): the user passes
  `paths: papers/jss-2026-foo` to scope to one.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A reusable GitHub Action MUST be published as
  `kollerma/jss-style-checker-action@v1` (the rolling tag) and
  semver tags `vX.Y.Z`.
- **FR-002**: The Action MUST be a *composite* action defined
  in `action.yml`. It MUST install Python (via
  `actions/setup-python@v5`), pip-install `jss-lint`
  (default: latest; `version` input pins), run
  `jss-lint --output sarif <paths>`, and conditionally
  upload SARIF + post review comments.
- **FR-003**: Inputs:
  - `paths` (default: `''` → auto-detect by glob).
  - `journal` (default: `jss`).
  - `fail-on-severity` (default: `error`; values: `error`
    | `warning` | `info` | `never`).
  - `comment-mode` (default: `pr-review`; values:
    `pr-review` | `pr-comment` | `none`).
  - `upload-sarif` (default: `true`).
  - `python-version` (default: `3.12`).
  - `version` (default: `latest`; otherwise a PyPI version).
- **FR-004**: Auto-detection: when `paths` is empty, glob
  for `**/*.tex`, `**/*.Rnw`, `**/*.Rmd`. Excluding
  `node_modules/`, `.git/`, `_build/`, common LaTeX
  build dirs.
- **FR-005**: SARIF: when `upload-sarif: true`, the
  Action invokes `github/codeql-action/upload-sarif@v3`
  with the artefact path `jss-lint.sarif`.
- **FR-006**: PR review comments: when
  `comment-mode: pr-review`, the Action calls the GitHub
  REST API `POST /repos/{owner}/{repo}/pulls/{n}/reviews`
  with one review event of type `COMMENT` containing one
  comment per violation grouped by file. The review is a
  single batch (one API call per workflow run).
- **FR-007**: PR-comment mode: when
  `comment-mode: pr-comment`, the Action posts a single
  PR comment summarising violations (no inline review
  comments). This is the lightweight option for repos
  where reviews look heavy-handed.
- **FR-008**: Stale-comment dedupe: when
  `comment-mode: pr-review` and a previous run by the
  same Action posted comments, the Action MUST dismiss
  those reviews (or mark them as outdated) before
  creating the new one. Detection key: review author
  matches the workflow's GITHUB_ACTOR (typically
  `github-actions[bot]`).
- **FR-009**: Exit code: the Action exits 0 if every
  violation's severity is below `fail-on-severity`; 1
  otherwise; 2 on usage error (unknown input value,
  invalid `paths`, etc.).
- **FR-010**: An end-to-end smoke-test workflow MUST
  exist in this repo at
  `.github/workflows/test-action.yml`. It runs the
  Action against `docs/jss-template/` (or equivalent
  fixture) and asserts the SARIF artefact appears AND
  the violation count matches the fixture's known
  violation list.
- **FR-011**: The Action's `README.md` MUST live next to
  `action.yml` and document every input + every
  output, with at least three example workflow snippets.
- **FR-012**: Release workflow: tags of the form `v*`
  trigger a workflow that updates the rolling `v<MAJOR>`
  tag (e.g., `v1`) and verifies the Action's smoke test
  passes.

### Key Entities

- **Action manifest** (`action.yml`): declares inputs,
  outputs, runs.using = "composite", and the
  step list.
- **Composite step list**: install Python → pip-install
  jss-lint → run lint → upload SARIF → post comments.
  Each step is opt-in via inputs.
- **PR review batch**: one API call per workflow run
  containing all comments; respects GitHub's review
  size limits.
- **Stale-comment heuristic**: previously-authored
  reviews by the workflow's bot user, dismissed on
  re-run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A clean fork that adds a one-line workflow
  invocation gets PR-side feedback within 60 seconds of
  pushing a commit (under typical GitHub-Actions
  scheduling latency).
- **SC-002**: Inline review comments appear at the exact
  line of each violation; the comment text contains the
  rule id, the violation message, and a link to the JSS
  guide section (from spec 007).
- **SC-003**: `fail-on-severity: error` correctly blocks
  merge on an error-severity violation and lets a
  warning-only run pass.
- **SC-004**: SARIF appears in the Security tab within 2
  minutes of workflow completion (subject to
  GitHub's processing latency).
- **SC-005**: Re-running on the same PR does not
  duplicate inline comments; previous runs' comments are
  dismissed or marked outdated.
- **SC-006**: The Action's installed footprint is
  zero (composite Action; no Docker image).

## Assumptions

- The Action runs on `ubuntu-latest`. Other runners (macOS,
  Windows) are out of scope but should not be actively
  blocked.
- The latest PyPI release of `jss-lint` is the default;
  pinning via `version` is the explicit override.
- GitHub-Actions REST API access uses the workflow's
  `GITHUB_TOKEN`; no PAT is needed for the comment-posting
  steps.
- `pull_request_target` events from forks ARE supported
  for the comment-posting step; the Action runs in the
  base repo's context with the fork's HEAD checked out.
- The smoke-test workflow uses
  `docs/jss-template/` (or a similar fixture) that ships
  in this repo; the test asserts SARIF presence + a
  known violation count.
- The rolling `v1` tag and immutable semver tags coexist
  per Clarifications §4.
- The Action repository is the same repo as the linter
  (Clarifications §1) — `kollerma/jss-style-checker` —
  with the Action manifest at `action/action.yml`. The
  marketplace listing is published from this repo.
