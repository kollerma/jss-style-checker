---
description: "Tasks for reusable GitHub Action"
---

# Tasks: Reusable GitHub Action

## Phase 1: Action manifest

- [ ] T001 `action/action.yml` — composite action with the seven
      inputs from spec.
- [ ] T002 `action/scripts/post-review.js` — review-posting payload.
- [ ] T003 `action/README.md` — marketplace listing copy.

## Phase 2: Release workflow

- [ ] T004 `.github/workflows/release-action.yml` — tag-triggered
      rolling-tag updater.

## Implementation Strategy

**MVP (this PR)**: Action manifest + release workflow, ready for
publication once the underlying CLI features ship to a public
release. No live smoke test; the action's sanity is verified by
the manifest alone in the absence of a publishing token.
