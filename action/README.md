# JSS Style Checker — GitHub Action

[![marketplace](https://img.shields.io/badge/marketplace-jss--style--checker--action-blue)](https://github.com/marketplace/actions/jss-style-checker)

Lint LaTeX / Sweave / R Markdown manuscripts on every PR. Inline review comments + SARIF upload to the Security tab + a one-line PR check.

The action invokes `jss-lint --source-root "$GITHUB_WORKSPACE"`, so SARIF
`artifactLocation.uri` values are always relative to the repo checkout root.
GitHub code-scanning resolves these URIs against the repo root, which keeps
inline annotations correct even when the calling workflow `cd`s into a
sub-directory before invoking the action.

## Usage

```yaml
# .github/workflows/jss-lint.yml
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

## Inputs

| Input              | Default      | Description                                                |
| ------------------ | ------------ | ---------------------------------------------------------- |
| `paths`            | (auto)       | Files / directories to lint. Empty = auto-detect tracked `.tex/.Rnw/.Rmd`. |
| `journal`          | `jss`        | Journal id.                                                |
| `fail-on-severity` | `error`      | `error` / `warning` / `info` / `never`.                    |
| `comment-mode`     | `pr-review`  | `pr-review` / `pr-comment` / `none`.                       |
| `upload-sarif`     | `true`       | Upload to Security tab.                                    |
| `python-version`   | `3.12`       | Python interpreter version.                                |
| `version`          | `latest`     | jss-lint PyPI version (or pinned semver).                  |

## Outputs

| Output            | Description                          |
| ----------------- | ------------------------------------ |
| `sarif-path`      | Filesystem path of the SARIF file.   |
| `violation-count` | Total violation count.               |

## Permissions

The calling workflow must grant:

- `contents: read`
- `pull-requests: write`
- `security-events: write`

## Examples

```yaml
# Pin everything for reproducible CI.
- uses: kollerma/jss-style-checker-action@v1.5.0
  with:
    version: '0.5.0'
    fail-on-severity: 'warning'

# SARIF only, no inline comments.
- uses: kollerma/jss-style-checker-action@v1
  with:
    comment-mode: 'none'
```

## License

MIT.
