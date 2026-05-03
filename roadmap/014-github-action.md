# 014 — Reusable GitHub Action

**Phase:** CI / journal workflow
**Depends on:** 006 (SARIF)
**Unblocks:** —

## Why

The Action puts the linter inside every PR opened against a
manuscript repo: review comments inline, SARIF uploaded to the
Security tab, and a one-line PR-summary status. Authors and editors
both consume the output without ever installing the tool locally.

## /speckit.specify prompt

Ship a reusable composite GitHub Action and publish it as
`kollerma/jss-style-checker-action@v1`. Inputs: `paths` (default:
auto-detected `.tex` / `.rnw` / `.rmd`), `journal` (default `jss`),
`fail-on-severity` (default `error`), `comment-mode`
(`pr-review` | `pr-comment` | `none`), `upload-sarif` (default
`true`), `python-version`. Behaviour: pip-install the latest release
(or a pinned `version` input), run `jss-lint --output sarif` on
`paths`, upload SARIF via `github/codeql-action/upload-sarif@v3`,
and for `comment-mode=pr-review` post a single review with one
comment per violation grouped by file. Action exits with
`fail-on-severity` honoured. Publish docs as a `README.md` next to
`action.yml`.

## /speckit.clarify prompt

Probe: (a) do we own a separate `kollerma/jss-style-checker-action`
repo (Marketplace canonical) or vendor it inside the main repo?
(b) fail-on-severity semantics: `error` blocks merge; what about
`warning` — configurable threshold count? (c) does PR-review-mode
dedupe violations across runs (resolves stale comments) or always
create fresh? (d) tag/release strategy: a `v1` rolling tag +
immutable `v1.0.0` semver, or only semver?

## /speckit.plan prompt

Create `action/action.yml` at the repo root. Implement the
`pr-review` comment mode using `actions/github-script@v7` and the
GitHub REST `pulls/{n}/reviews` endpoint, batching comments to one
review. Workflow `.github/workflows/release-action.yml` tags `v1`
on each major release. Add an end-to-end smoke-test workflow that
runs the Action against `docs/jss-template/` and asserts the SARIF
artifact appears. Document in
`specs/014-github-action/quickstart.md`.
