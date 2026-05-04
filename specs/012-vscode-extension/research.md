# Research: VS Code Extension

**Phase**: 0
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. Source location: monorepo vs. sibling repo

**Decision**: `vscode-extension/` in this repo.

**Rationale**:
- Spec 011's LSP server contract is the seam between Python
  and TypeScript. Putting both sides in the same repo means
  every protocol-level breaking change is one PR with
  matched updates.
- A sibling repo would require coordinated tagging and
  separate CI; that overhead exceeds the cost of a Node-based
  job in the main matrix.

**Alternatives considered**:
- Sibling repo `kollerma/jss-style-checker-vscode`: rejected
  — coordination cost.
- Submodule under `vscode-extension/`: rejected — submodules
  are notoriously easy to mishandle in `git clone`.

---

## 2. Python interpreter discovery

**Decision**: Layered discovery:
1. The VS Code Python extension's selected interpreter (when
   the Python extension is installed and active).
2. The user's `jssStyleChecker.python.path` setting.
3. `python` on the user's PATH.

When none of the above resolves to an interpreter that has
`jss-lint[lsp]` installed, surface a notification with two
buttons: "Set Python path" (opens the setting) and "Install
jss-lint" (opens an integrated terminal with `pip install
--user "jss-lint[lsp]"`).

**Rationale**:
- VS Code Python users almost always have the Python
  extension; piggy-backing on its interpreter selection is
  zero-config for them.
- The `python.path` setting is the explicit override path.
- PATH `python` is the last-resort default that almost
  always exists when LaTeX-on-VS-Code does.
- The "install jss-lint" button is the lowest-friction
  recovery path.

**Alternatives considered**:
- Bundle a Python interpreter: rejected per Clarifications
  §2 (size, platform-specific publishing).
- Require `python.path` always: rejected — too hostile.
- Auto-install `jss-lint[lsp]` silently on first activation:
  rejected — running `pip install` without consent is a
  surprise.

---

## 3. Overleaf / browser path

**Decision**: Out of scope for spec 012.

**Rationale**:
- Overleaf does not run VS Code extensions. A web-based
  integration would need a browser extension (Chrome /
  Firefox) that sniffs the Overleaf editor DOM, OR an
  Overleaf cloud-side plugin.
- Both paths require their own design (security model,
  permission model, packaging surface). Each is its own
  spec.

**Alternatives considered**:
- A browser extension that calls a hosted lint API:
  rejected — would require the project to host an API
  endpoint, which it does not today.
- A user-level userscript: rejected — out of scope and
  fragile.

---

## 4. Marketplaces

**Decision**: Publish to BOTH the VS Code marketplace and
Open VSX. Same `.vsix` artefact on both.

**Rationale**:
- The VS Code marketplace is closed to non-VS-Code
  consumers; Cursor, Codium, and Theia draw from Open VSX.
- Publishing both gates marketplace coverage; not doing so
  cuts off ~10–20 % of users (Open VSX consumers).
- The two marketplaces accept identical `.vsix` files; the
  workflow runs `vsce publish` once and `ovsx publish`
  once.

**Alternatives considered**:
- VS Code marketplace only: rejected — excludes Open VSX
  consumers.
- Open VSX only: rejected — excludes mainstream VS Code
  users.

---

## 5. Tag scheme

**Decision**: Trigger the publish workflow on git tags
matching `v*-vscode` (e.g., `v0.5.0-vscode`). Python
package release tags (`v*` without the suffix) do NOT
trigger the extension publish.

**Rationale**:
- The two artefacts (Python package + VS Code extension)
  do not necessarily release in lockstep. Decoupling tag
  schemes lets each release on its own cadence.
- `v0.5.0-vscode` is unambiguous; `v0.5.0` continues to
  drive only the Python release path.

**Alternatives considered**:
- Single tag scheme `v*` for both: rejected — would
  publish the extension on every Python release, even
  when the extension code did not change.
- Separate workflows on push to `main` (no tags):
  rejected — a release should be deliberate.

---

## 6. Settings → LSP propagation

**Decision**: The extension reads its five settings on
startup AND on every `vscode.workspace.onDidChangeConfiguration`
event. Changes are pushed to the LSP server via the standard
LSP `workspace/configuration` reverse request and the
`workspace/didChangeConfiguration` notification.

**Rationale**:
- LSP defines the round-trip; we follow it.
- The reverse request lets the server pull settings on
  demand (e.g., after restart).
- The notification keeps the server's in-memory view fresh
  on user-triggered changes.

**Alternatives considered**:
- Restart the LSP server on every config change: rejected
  — would invalidate the cache and regress SC-001.
- Settings persisted in `.jss-lint.toml` only: rejected —
  VS Code users expect a settings UI.

---

## 7. Status-bar implementation

**Decision**: A single `vscode.StatusBarItem` in the right
group, positioned with priority `100`. Updates fire on each
`vscode.languages.onDidChangeDiagnostics` event for the
active editor. The text is `jss-lint: <count>`; clicking
runs the `workbench.actions.view.problems` built-in
command.

**Rationale**:
- VS Code provides the Diagnostic Collection API; we
  observe it directly. No need to dig into LSP wire
  messages.
- The right group is the conventional location for
  language-status items.

**Alternatives considered**:
- A separate icon in the activity bar: rejected — too
  prominent for a per-file count.
- A tree view in the explorer: rejected — duplicates
  Problems.

---

## 8. Test strategy

**Decision**: `@vscode/test-electron` runs the extension
inside a headless VS Code instance. Smoke tests:
1. Activate the extension on a fixture `.tex` and assert
   the LSP server starts.
2. Open a fixture with a known violation and assert the
   diagnostic count.
3. Trigger the apply-all command and assert the buffer
   content changes.

The Python side of the integration (`jss-lint lsp`
behaviour) is NOT re-tested; spec 011's test suite owns
it.

**Rationale**:
- The headless test runner is the canonical VS Code
  extension test path.
- Re-testing the LSP server here would duplicate spec
  011's coverage.

**Alternatives considered**:
- Mock the LSP server in TypeScript: rejected — would not
  exercise the real wire.
- Skip extension tests entirely: rejected — extension
  bugs (activation, status-bar) need their own coverage.

---

## Summary

All eight decisions follow from spec Clarifications and
Constitution §IV, §X, §XI. No remaining `NEEDS
CLARIFICATION`. Ready for Phase 1.
