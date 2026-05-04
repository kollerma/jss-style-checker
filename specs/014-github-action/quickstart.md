# Quickstart: GitHub Action

## For an end user

### Add to your repo

Create `.github/workflows/jss-lint.yml`:

```yaml
name: JSS Style
on:
  pull_request:
    paths:
      - '**/*.tex'
      - '**/*.Rnw'
      - '**/*.Rmd'
permissions:
  contents: read
  pull-requests: write
  security-events: write
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kollerma/jss-style-checker-action@v1
```

That's it. Open a PR; you should see review comments and
SARIF in the Security tab.

### Customise

```yaml
- uses: kollerma/jss-style-checker-action@v1
  with:
    paths: 'papers/jss-2026-foo'    # scope to a sub-directory
    journal: 'jss'                   # default
    fail-on-severity: 'warning'      # block merge on warnings too
    comment-mode: 'pr-comment'       # single PR comment, not a review
    upload-sarif: 'true'             # default
    python-version: '3.12'           # default
    version: '0.5.0'                 # pin the linter; default 'latest'
```

### Pin to an immutable version

```yaml
- uses: kollerma/jss-style-checker-action@v1.5.0
  with:
    version: '0.5.0'
```

This locks both the Action code and the linter version.
Reproducible across re-runs.

### Disable comments (SARIF only)

```yaml
- uses: kollerma/jss-style-checker-action@v1
  with:
    comment-mode: 'none'
```

The Security tab still shows the violations.

## For a contributor

### Where things live

```text
action/action.yml                         # composite manifest
action/README.md                          # marketplace listing copy
action/scripts/post-review.js             # PR-review payload
.github/workflows/release-action.yml      # rolling-tag updater
.github/workflows/test-action.yml         # smoke test
docs/jss-template/                        # smoke-test fixture
tests/integration/test_action_smoke.py    # Python-side assertions
```

### Develop locally

The Action is YAML + a small JS file. The fastest dev
loop is:

1. Edit `action/action.yml` or `action/scripts/post-review.js`.
2. Push to a branch in this repo.
3. Open a PR.
4. The smoke-test workflow runs on every PR; check its
   logs.

For local PR-review payload testing, use the GitHub CLI:

```sh
gh api -X POST /repos/{owner}/{repo}/pulls/{n}/reviews \
  -f event=COMMENT \
  -f body='' \
  -f comments[][path]=foo.tex \
  -f comments[][line]=1 \
  -f comments[][body]='test'
```

### Release

To cut a release:

1. Bump the linter to its new PyPI version (e.g.,
   `0.5.0`).
2. Tag the linter release: `git tag v0.5.0 && git push
   origin v0.5.0`.
3. Tag the Action release: `git tag v1.5.0 && git push
   origin v1.5.0`.
4. The release-action workflow:
   - Pushes `action/` contents to the
     `kollerma/jss-style-checker-action` repo.
   - Updates the rolling `v1` tag to point at the new
     release.

### Common pitfalls

- **Forgetting `permissions:`**: the Action will exit
  non-zero with a 403 from the GitHub API. The README
  prominently documents the three required permissions.
- **Triggering on `push` instead of `pull_request`**: the
  comment-posting step requires a PR context. On `push`
  events, the step is silently skipped (no error); SARIF
  upload still works.
- **Forks without `pull_request_target`**: regular
  `pull_request` triggered by a fork PR gets a read-only
  `GITHUB_TOKEN`. The comment step then fails. Use
  `pull_request_target` for fork PRs (with the fork's
  HEAD checked out via `actions/checkout` `ref:`).
- **Rolling-tag pin is desync'd**: when a user pins
  `@v1` and the Action changes behaviour in a v1.x
  patch, that's by design. If you want a frozen
  reference, use the immutable `vX.Y.Z` tag.
