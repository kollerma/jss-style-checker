# Research: Reusable GitHub Action

**Phase**: 0
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. Composite vs. Docker vs. JavaScript Action

**Decision**: Composite Action.

**Rationale**:
- Docker actions add ~30–60 s of startup overhead per run
  for image pull. The lint job is already <60 s; doubling
  that for image pull is hostile.
- JavaScript actions require a `node_modules` to be
  committed and bundled — the surface is larger than what
  we need.
- Composite actions are YAML; they orchestrate other
  pre-built actions and shell commands.

**Alternatives considered**:
- Docker action: rejected per startup cost + footprint.
- Pure-JS action: rejected — all the heavy lifting is in
  Python; the Action would still need to install Python.

---

## 2. PR-review API: single review with comments vs. one comment per call

**Decision**: One `POST /repos/{o}/{r}/pulls/{n}/reviews`
call carrying every comment in `comments[]`. The review
event is `COMMENT` (not `APPROVE` / `REQUEST_CHANGES`).

**Rationale**:
- One API call ⇒ one PR conversation entry; clean history.
- Per-comment posts (`POST /pulls/{n}/comments`) accumulate
  N entries and make stale-dedupe harder.
- The "review" surface is also the canonical place for
  bot-authored review comments.

**Alternatives considered**:
- `POST /pulls/{n}/comments` per violation: rejected per
  rationale.
- `COMMENT` review with `body` summary + per-comment
  inline: out of scope; we leave the review body empty.

---

## 3. Stale-comment dedupe

**Decision**: Before posting, list reviews on the PR and
dismiss those authored by the workflow's bot user
(`github-actions[bot]` by default) with
`dismissalReason: "outdated"`. Use the GraphQL
`dismissPullRequestReview` mutation.

**Rationale**:
- Dismissal is the supported "this review is no longer
  relevant" surface.
- Filtering by bot author avoids dismissing human reviews.
- Past-run filter limits to OUR Action's reviews
  (other bots — e.g., a security scanner — are
  untouched).

**Alternatives considered**:
- Delete instead of dismiss: rejected — `DELETE
  /pulls/{n}/reviews/{id}` requires the review to be
  PENDING, which it isn't post-COMMENT.
- Edit the previous review (PATCH): rejected — the API
  permits editing only the body, not adding/removing
  inline comments.
- Always create fresh: rejected per Clarifications §3.

---

## 4. Tag strategy

**Decision**: Both rolling `v<MAJOR>` and immutable
`vX.Y.Z` semver tags. The release workflow updates
`v1` (etc.) to point at the latest `v1.x.y` semver tag.

**Rationale**:
- Rolling tag is the GitHub-Actions convention; users
  put `@v1` in their workflows and get patches
  automatically.
- Immutable semver is the production-pinning surface for
  reproducibility-conscious users.

**Alternatives considered**:
- Only semver: rejected per Clarifications §4.
- Only rolling: rejected — would prevent pinning for
  reproducibility.

---

## 5. Marketplace publishing

**Decision**: The Action source lives at `action/` in this
repo. The Marketplace listing's "uses" string is
`kollerma/jss-style-checker-action@v1`; this is satisfied
by a release workflow that pushes the `action/`
contents to a separate `kollerma/jss-style-checker-action`
repo on each `v*` tag.

**Rationale**:
- Co-locating source with the Python package keeps the
  Action's smoke test in lock-step with linter changes.
- The published surface stays at the conventional
  `kollerma/jss-style-checker-action` org/name; users
  don't see the source-repo split.

**Alternatives considered**:
- Sibling repo for the Action source: rejected per
  Clarifications §1 (coordination cost).
- Source in main repo with Marketplace pointed at the
  monorepo: rejected — Marketplace listings prefer a
  dedicated repo as the "uses" target for tag-based
  immutability.

---

## 6. Auto-detection of paths

**Decision**: When `paths` is empty, glob for
`**/*.tex`, `**/*.Rnw`, `**/*.Rmd`, with excludes for
`**/{.git,node_modules,_build,build,dist,_minted-*}`.

**Rationale**:
- Authors with multi-file projects (spec 013) pass a
  single root file or directory; auto-detection covers
  the "I have one big paper" case.
- The exclude list is the well-known LaTeX build-output
  pattern.

**Alternatives considered**:
- Required `paths` input: rejected — too friction-heavy
  for the headline UX.
- Glob without excludes: rejected — would lint
  build-tree files that are not author-authored.

---

## 7. `fail-on-severity` surface

**Decision**: Four values: `error` (default), `warning`,
`info`, `never`. The Action exits 1 if any violation has
severity at-or-above the input value. `never` always
exits 0 (used by reporting-only workflows).

**Rationale**:
- The simple level-threshold model matches every other
  CI tool's "fail on level".
- `never` is the explicit opt-out for "always succeed,
  use the SARIF tab".

**Alternatives considered**:
- `fail-on-count: <n>`: rejected per Clarifications §2
  (deferred).
- `fail-on-rule: <id>`: rejected — `--ignore-rules`
  already covers the inverse; an inclusion list is
  superfluous.

---

## 8. Secrets and permissions

**Decision**: The Action requires:
- `permissions: { contents: read, pull-requests: write,
  security-events: write }` in the calling workflow.

The `GITHUB_TOKEN` provided by GitHub is sufficient; no
PAT is needed.

**Rationale**:
- `pull-requests: write` is needed to post review
  comments.
- `security-events: write` is needed for SARIF upload.
- `contents: read` is needed for checkout (which the
  caller runs).

**Alternatives considered**:
- Require a PAT: rejected — adds friction; only needed
  if posting to a different repo, which we don't do.
- `permissions: { write-all }`: rejected — overscoped.

---

## Summary

All eight decisions follow from spec Clarifications and
Constitution §X. No remaining `NEEDS CLARIFICATION`.
Ready for Phase 1.
