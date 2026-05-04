# 006 — SARIF output

**Phase:** Foundations
**Depends on:** —
**Unblocks:** 011 (Language Server), 014 (GitHub Action)

## Why

GitHub code-scanning, CodeQL, VS Code's Problems pane, and most CI
platforms speak SARIF 2.1.0 natively. Adding SARIF as a fourth output
format alongside `terminal` / `json` / `html` lets the linter plug
into all of them with zero glue code on the consumer side.

## /speckit.specify prompt

Add SARIF 2.1.0 as a fourth value for `--output` in `jss-lint`
(alongside `terminal`, `json`, `html`). The renderer maps each
`Violation` to a SARIF `result` and each `Rule` in the active journal
to an entry under `runs[0].tool.driver.rules`. Severity translates as
`error -> error`, `warning -> warning`, `info -> note`. Each result
carries `ruleId`, `message.text`, `level`, and a `locations[0]` with a
`physicalLocation.artifactLocation.uri` (relative to CWD or to a
new `--source-root` flag) and a `region` with `startLine`,
`startColumn`, and (when known) `endLine` / `endColumn`. Parse
failures (`JSS-PARSE-000`) emit `notification` objects under
`runs[0].invocations[0].toolExecutionNotifications`. Output is
deterministic byte-for-byte for identical inputs; a JSON-schema
contract test asserts conformance to SARIF 2.1.0. The existing
`--output json` shape is unchanged.

## /speckit.clarify prompt

Probe these seams: (a) what is the canonical mapping from internal
`category` to SARIF `tags` / `taxonomies`? (b) when a fix is
available (spec 008), do we emit `fixes[]` in the same SARIF result
or hold it for a later spec? (c) `--source-root` default — CWD or
the directory of the first input file? (d) do we suppress
`JSS-PARSE-000` notifications when the user passes
`--ignore-rules JSS-PARSE-000`, or always emit under `notifications`?
(e) does the SARIF renderer respect `ignore_rules` filtering or
include suppressed results with `suppressions[]`? Also confirm
whether GitHub code-scanning's per-file size cap requires a
paginated / multi-run output for the 172-paper corpus.

## /speckit.plan prompt

Implement the renderer in a new module `src/texlint/output/sarif.py`
exporting `render(report, cfg)` consistent with the existing
`json_output.py` / `html_output.py` signature. Pull rule metadata
from `_catalogue_data.RULES` so every rule definition appears in
`tool.driver.rules`, not only rules with hits. Use the standard
library `json` module with `sort_keys=True` and `indent=2`. Add a
golden-file test under `tests/unit/output/test_sarif.py` covering
clean run, single error, multi-file run, and parse-error case.
Update `cli.py:_dispatch_renderer` to wire the new value. Update
the JSON output contract document under
`specs/001-linter-foundation/contracts/` to note SARIF as a peer
format. No new runtime dependencies; SARIF is plain JSON.
