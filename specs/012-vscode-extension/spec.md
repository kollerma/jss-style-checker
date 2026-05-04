# Feature Specification: VS Code Extension

**Feature Branch**: `012-vscode-extension`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Ship a VS Code extension `kollerma.jss-style-checker` published to the marketplace. The extension activates on `.tex`, `.ltx`, `.rnw`, `.rmd` files; spawns the spec-011 LSP server (`jss-lint lsp`) using the user's configured Python interpreter; exposes the standard LSP UX (squiggles, hover, code-action lightbulb, Problems pane). Settings: `jssStyleChecker.python.path`, `jssStyleChecker.severityOverrides`, `jssStyleChecker.ignoreRules`, `jssStyleChecker.codeWidth`, `jssStyleChecker.runOn` (`save` | `change`). Status-bar item shows violation count and links to the Problems pane. Bundle a \"Run jss-lint init\" command (spec 010)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the extension and lint a manuscript (Priority: P1)

A JSS author opens VS Code, installs `kollerma.jss-style-checker`
from the marketplace, opens `manuscript.tex`, and immediately sees
inline squiggles for every style violation. No terminal commands;
no manual configuration.

**Why this priority**: P1 because the marketplace install path is
the headline reason VS Code is the editor of choice for many
authors. The extension is the single distribution channel that
makes this real.

**Independent Test**: Install the packaged `.vsix` in a clean VS
Code instance, open a fixture `.tex` with a known violation, and
confirm the editor's "Problems" pane shows the violation within 5
seconds of file open.

**Acceptance Scenarios**:

1. **Given** a clean VS Code with the extension installed and a
   `python` interpreter that has `jss-lint[lsp]` installed,
   **When** the user opens a `.tex` file with one known
   violation, **Then** the Problems pane lists exactly one
   problem with the rule id, message, and source `jss-lint`.
2. **Given** the same setup, **When** the user hovers the
   squiggle, **Then** the tooltip shows the rule message and a
   clickable link (the `guide_url` from spec 007).
3. **Given** a violation whose rule ships a `Fix` (spec 008),
   **When** the user clicks the lightbulb and selects the
   quick-fix, **Then** the edit applies and the squiggle
   disappears.

---

### User Story 2 - Status bar shows the violation count (Priority: P1)

The author has the file open. The status bar at the bottom of
VS Code shows `jss-lint: 12` (12 violations). Clicking the item
opens the Problems pane scrolled to the first violation.

**Why this priority**: P1 because the Problems pane is hidden by
default; without an at-a-glance count in the status bar, authors
forget the linter is running.

**Independent Test**: Open a fixture with 12 violations; assert
that the status-bar item displays the literal text `jss-lint: 12`.

**Acceptance Scenarios**:

1. **Given** a buffer with 12 violations, **When** the
   diagnostics are published, **Then** the status-bar item shows
   `jss-lint: 12`.
2. **Given** a buffer with 0 violations, **When** the diagnostics
   are published, **Then** the status-bar item shows `jss-lint:
   0` (in a muted style).
3. **Given** the user clicks the status-bar item, **When** the
   click is handled, **Then** the Problems pane opens and the
   first violation is selected.

---

### User Story 3 - Run init from the command palette (Priority: P2)

The author opens the command palette (`Cmd-Shift-P`) and selects
`jss-lint: Run init`. The extension spawns `jss-lint init` against
the workspace folder; the generated `.jss-lint.toml` appears in
the file tree; the LSP server picks up the new config
automatically.

**Why this priority**: P2 because authors who reach for the
command palette are already engaged. The bigger adoption barrier
is the first install (Story 1); init is a follow-on convenience.

**Independent Test**: Trigger the command in a fresh workspace;
the `.jss-lint.toml` file is created at the workspace root; the
LSP server's diagnostics refresh after the file is written.

**Acceptance Scenarios**:

1. **Given** a workspace with no `.jss-lint.toml`, **When** the
   user runs the command, **Then** `.jss-lint.toml` appears at
   the root and the diagnostic count refreshes within 5 seconds.
2. **Given** a workspace with an existing `.jss-lint.toml`,
   **When** the user runs the command, **Then** an information
   message offers `--force`; the file is unchanged on
   "Cancel".

---

### User Story 4 - Settings UI for runOn / ignoreRules (Priority: P2)

The author opens VS Code's settings UI, types "jss-lint", and sees
five settings: `python.path`, `severityOverrides`, `ignoreRules`,
`codeWidth`, `runOn`. They flip `runOn` from `change` to `save`
and the LSP server starts linting only on save.

**Why this priority**: P2 because every VS Code user expects a
settings UI. Without it, configuration is invisible.

**Independent Test**: Set `jssStyleChecker.runOn = "save"`;
confirm that diagnostics no longer refresh on `didChange` but do
refresh on `didSave`.

**Acceptance Scenarios**:

1. **Given** `jssStyleChecker.runOn = "save"`, **When** the user
   types into the buffer, **Then** the diagnostic count does not
   change.
2. **Given** the same setting, **When** the user saves the
   buffer, **Then** diagnostics refresh.
3. **Given** the user adds a rule id to `jssStyleChecker.
   ignoreRules`, **When** the change is committed, **Then** the
   server suppresses violations of that rule (verified via the
   Problems-pane count).

---

### User Story 5 - Marketplace publish on git tag (Priority: P3)

A maintainer pushes a git tag of the form `v0.5.0-vscode`. A
GitHub Actions workflow runs `vsce package` and `vsce publish`,
uploading the `.vsix` to the VS Code marketplace and Open VSX
(Clarifications §4).

**Why this priority**: P3 because manual publish covers the
first release; automation pays off only after several releases.
The workflow file ships in this spec for the maintainer's
benefit, but the headline value is the extension itself.

**Independent Test**: A test git tag triggers the workflow on a
fork; the workflow's dry-run mode reports the version it would
publish.

**Acceptance Scenarios**:

1. **Given** a tag `v0.5.0-vscode`, **When** the workflow runs,
   **Then** it publishes the extension at version `0.5.0` to the
   VS Code marketplace and Open VSX.
2. **Given** a tag with non-matching prefix (e.g., `v0.5.0`),
   **When** the workflow is checked, **Then** it does not run.

---

### Edge Cases

- The configured Python interpreter is not on PATH: the
  extension surfaces a notification with a "Set Python path"
  button.
- The Python interpreter exists but `jss-lint[lsp]` is not
  installed: the extension surfaces a "Install jss-lint" button
  that runs `pip install --user "jss-lint[lsp]"` in a terminal.
- The user's workspace has no `.tex` files: the extension does
  not activate; no resource cost.
- Two workspace folders are open with different
  `.jss-lint.toml` files: the LSP server uses the first folder
  per spec 011 Clarifications §2.
- The user uses a remote workspace (SSH, WSL, devcontainer):
  the extension installs in the remote context and spawns the
  remote `jss-lint`.
- The user uses Cursor / Codium / Theia (Open VSX consumers):
  the extension is published to Open VSX in addition to the
  VS Code marketplace (Clarifications §4).
- The marketplace publish workflow runs without a `VSCE_PAT`
  secret: the workflow exits with a clear error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The extension MUST be published to the VS Code
  marketplace as `kollerma.jss-style-checker` and to Open VSX
  under the same identifier.
- **FR-002**: The extension MUST activate on document languages
  `latex`, `tex`, `rnoweb`, `rmd` (the VS Code language ids for
  `.tex` / `.ltx`, `.Rnw`, `.Rmd`).
- **FR-003**: On activation, the extension MUST spawn the
  spec-011 LSP server using `<python.path> -m texlint.cli lsp`
  (or equivalent — research §2). Default: `python` on PATH.
- **FR-004**: The extension MUST expose five settings under the
  `jssStyleChecker` namespace:
  - `python.path: string` (default `"python"`).
  - `severityOverrides: { [ruleId: string]: "error" | "warning"
    | "info" }`.
  - `ignoreRules: string[]`.
  - `codeWidth: number` (default 80).
  - `runOn: "save" | "change"` (default `"change"`).
- **FR-005**: All five settings MUST be propagated to the LSP
  server via `workspace/configuration` and applied to the
  in-memory config used for linting.
- **FR-006**: A status-bar item MUST display the current
  violation count for the active editor's file. Clicking opens
  the Problems pane.
- **FR-007**: A command `jss-lint: Run init` MUST be registered
  in the command palette. The command spawns `jss-lint init` in
  the workspace root and surfaces the result.
- **FR-008**: A command `jss-lint: Apply all fixes` MUST be
  registered. It invokes the LSP server's
  `workspace/executeCommand` with `jss-lint.applyAllFixes`.
- **FR-009**: When the configured Python interpreter is missing
  or `jss-lint[lsp]` is not installed, the extension MUST
  surface a clear, actionable notification with a button to fix
  the situation.
- **FR-010**: The extension's source MUST live under
  `vscode-extension/` in this repository (Clarifications §1).
- **FR-011**: A GitHub Actions workflow at
  `.github/workflows/vscode-publish.yml` MUST publish the
  extension to both marketplaces on `v*-vscode` git tags.
- **FR-012**: The extension MUST NOT bundle a Python interpreter
  (Clarifications §2). Users provide their own; the
  extension's Python-discovery story uses the existing VS Code
  Python extension's interpreter selection where present.
- **FR-013**: README MUST gain a marketplace badge linking to
  the listing.

### Key Entities

- **Extension manifest** (`package.json`): the VS Code
  package descriptor including `activationEvents`,
  `contributes.configuration`, `contributes.commands`.
- **LanguageClient**: the `vscode-languageclient` instance
  that wires VS Code to the LSP server.
- **Status-bar item**: a `vscode.StatusBarItem` updated on
  every `publishDiagnostics`.
- **Settings document**: the JSON shape of the five
  `jssStyleChecker` settings.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A clean VS Code install + extension install +
  `jss-lint[lsp]` install yields visible squiggles within 30
  seconds of opening a `.tex` fixture (network bandwidth not
  counted).
- **SC-002**: The status-bar item updates within 1 second of
  every diagnostic refresh.
- **SC-003**: Settings changes propagate to the running LSP
  server without a VS Code reload.
- **SC-004**: The extension publishes successfully to BOTH
  the VS Code marketplace and Open VSX from a single tag-
  triggered workflow run.
- **SC-005**: The extension's installed footprint (excluding
  Python deps) is below 1 MB.

## Assumptions

- The user installs Python and `jss-lint[lsp]` themselves;
  the extension does not bundle either (research §2).
- The VS Code Python extension's "selected interpreter" is the
  preferred Python source when present; fallback is the
  `python.path` setting; fallback to `python` on PATH.
- Open VSX accepts the same `.vsix` as the VS Code
  marketplace; we publish identical artefacts to both.
- The Overleaf integration is OUT OF SCOPE for spec 012;
  Overleaf does not run extensions in the same model and
  needs its own approach (research §3).
- The TypeScript extension code is small (<500 LOC) and
  pure-JS — no native modules.
