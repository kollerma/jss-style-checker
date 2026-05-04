# Contract: Action Manifest

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

## C-1 Composite

`action.yml` MUST declare `runs.using: composite`. Docker and
JavaScript Actions are forbidden.

## C-2 Inputs

The Action MUST declare exactly the seven inputs from
data-model §1: `paths`, `journal`, `fail-on-severity`,
`comment-mode`, `upload-sarif`, `python-version`, `version`.
Defaults match data-model §1.

## C-3 Outputs

Two outputs:
- `sarif-path`: filesystem path to the generated SARIF.
- `violation-count`: integer total of violations across
  all input files.

## C-4 Step set

The composite step list MUST be:
1. `actions/setup-python@v5` — pinned MAJOR.
2. Install `jss-lint` (PyPI; pinned or latest per `version`).
3. Run `jss-lint --output sarif <paths>` and capture the
   output to `./jss-lint.sarif`.
4. Conditional: `github/codeql-action/upload-sarif@v3` when
   `upload-sarif == 'true'`.
5. Conditional: `actions/github-script@v7` running
   `post-review.js` when `comment-mode == 'pr-review'` AND
   `github.event_name == 'pull_request'`.

No other steps may run inside the composite.

## C-5 Exit code semantics

Per data-model §5 / spec FR-009:

- `0` if every violation's severity is below
  `fail-on-severity`.
- `1` if any violation's severity is at-or-above
  `fail-on-severity`.
- `2` on usage errors (unknown input value, invalid
  `paths`).

Note: `fail-on-severity: never` always returns 0 unless
the linter itself crashes (which surfaces as exit 2).

## C-6 SARIF artefact path

`steps.lint.outputs.sarif-path` MUST equal
`jss-lint.sarif` (relative to the runner's workspace).
The artefact is uploaded to GitHub via
`actions/upload-artifact` (transitive) by
`upload-sarif@v3`.

## C-7 Permissions documented

The Action's `README.md` MUST prominently document the
three required permissions: `contents: read`,
`pull-requests: write`, `security-events: write`.
Workflows that omit any are documented to fail with a
clear error message.

## C-8 No state mutation

The Action MUST NOT:
- Commit to the repo.
- Force-push.
- Create or delete branches.
- Modify any file outside the runner's workspace.
- Make outbound network calls beyond the documented
  GitHub-API surface and PyPI.
