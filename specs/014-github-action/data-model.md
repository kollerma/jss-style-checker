# Data Model: Reusable GitHub Action

**Phase**: 1
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. `action.yml` shape

```yaml
name: 'JSS Style Checker'
description: 'Lint LaTeX/BibTeX manuscripts against the JSS style guide.'
author: 'kollerma'
branding:
  icon: 'check-circle'
  color: 'blue'

inputs:
  paths:
    description: 'Files or directories to lint (default: auto-detect).'
    required: false
    default: ''
  journal:
    description: 'Journal id.'
    required: false
    default: 'jss'
  fail-on-severity:
    description: 'error | warning | info | never'
    required: false
    default: 'error'
  comment-mode:
    description: 'pr-review | pr-comment | none'
    required: false
    default: 'pr-review'
  upload-sarif:
    description: 'Upload SARIF to the Security tab.'
    required: false
    default: 'true'
  python-version:
    description: 'Python version to install.'
    required: false
    default: '3.12'
  version:
    description: 'jss-lint PyPI version (default: latest).'
    required: false
    default: 'latest'

outputs:
  sarif-path:
    description: 'Path to the generated SARIF file.'
    value: ${{ steps.lint.outputs.sarif-path }}
  violation-count:
    description: 'Total violation count.'
    value: ${{ steps.lint.outputs.violation-count }}

runs:
  using: 'composite'
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
    - name: Install jss-lint
      shell: bash
      run: |
        if [ "${{ inputs.version }}" = "latest" ]; then
          pip install jss-lint
        else
          pip install "jss-lint==${{ inputs.version }}"
        fi
    - id: lint
      name: Run jss-lint
      shell: bash
      run: |
        # Resolve paths input (auto-detect when empty); run linter; capture
        # violation-count and sarif-path; pipe SARIF to ./jss-lint.sarif.
        # Exit 1 when fail-on-severity matches; 0 otherwise.
        ...
    - if: ${{ inputs.upload-sarif == 'true' }}
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: ${{ steps.lint.outputs.sarif-path }}
    - if: ${{ inputs.comment-mode == 'pr-review' && github.event_name == 'pull_request' }}
      uses: actions/github-script@v7
      with:
        script: |
          const { postReview } = require('${{ github.action_path }}/scripts/post-review.js');
          await postReview({ github, context, sarifPath: '${{ steps.lint.outputs.sarif-path }}' });
```

## 2. `post-review.js` shape

The JS module exports `postReview({ github, context,
sarifPath })` which:

1. Reads the SARIF file from disk.
2. Maps each `result` to a `comment` object with
   `path`, `line`, `body`. Body includes rule id +
   message + a link to the spec-007 `guide_url`.
3. Lists prior reviews on the PR; dismisses those
   authored by the workflow's bot user (per research §3).
4. Posts a single `POST /pulls/{n}/reviews` with
   `event: COMMENT` and the comments array.

The module is plain CommonJS, no transpilation, no
build step. It runs inside `github-script@v7` which
provides `github`, `context`, and `require` for files
under the action's checkout path.

## 3. SARIF → review-comment projection

| SARIF source                                      | Review comment field                            |
| ------------------------------------------------- | ----------------------------------------------- |
| `result.locations[0].physicalLocation.artifactLocation.uri` | `path`                                          |
| `result.locations[0].physicalLocation.region.startLine` | `line`                                          |
| `result.ruleId`, `result.message.text`            | concatenated into `body`                         |
| (rule's `helpUri` from `tool.driver.rules[]`)     | appended as a markdown link in `body`           |

`body` example:

```markdown
**JSS-CITE-002**: prefer `\citet{}` over `\cite{}`.
[(see §3.2 Citations)](https://www.jstatsoft.org/.../section-3-2)
```

## 4. Auto-detection algorithm

When `paths` is empty:

```bash
git ls-files \
  | grep -E '\.(tex|Rnw|Rmd)$' \
  | grep -v -E '^(\.git|node_modules|_build|build|dist|_minted-)/'
```

Tracked files only (no `git`-untracked) — the Action runs
in CI against a checked-out commit; untracked artefacts
should not appear there anyway.

## 5. Exit code computation

```bash
SEVERITY_LEVEL = { error: 0, warning: 1, info: 2, never: 3 }
threshold = SEVERITY_LEVEL[fail-on-severity]
worst_severity = min(SEVERITY_LEVEL[v.severity] for v in violations)
exit 1 if worst_severity <= threshold else 0
```

(Inverted scale because `error < warning < info` in
"how serious".)

## 6. Permissions required

The calling workflow MUST grant:

```yaml
permissions:
  contents: read
  pull-requests: write
  security-events: write
```

The Action documents this prominently in its README.

## 7. Workflow triggers

Recommended caller trigger:

```yaml
on:
  pull_request:
    paths:
      - '**/*.tex'
      - '**/*.Rnw'
      - '**/*.Rmd'
```

Documented in the Action README; users may choose
different triggers.

## 8. Out of scope

| Item                                            | Reason                                                                  |
| ----------------------------------------------- | ----------------------------------------------------------------------- |
| Docker action                                   | Out per research §1.                                                     |
| `fail-on-count: <n>`                            | Out per Clarifications §2.                                               |
| Editing existing reviews (no dismissal)         | Out per research §3.                                                     |
| Posting to non-PR contexts (push events)        | The Action no-ops the comment step on non-PR contexts.                   |
| macOS / Windows runners                         | Out — `ubuntu-latest` only.                                              |
| Custom badges / status checks                   | Out — the workflow's own status check is the canonical signal.           |
