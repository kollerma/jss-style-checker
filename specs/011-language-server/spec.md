# Feature Specification: Language Server (LSP)

**Feature Branch**: `011-language-server`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Implement an LSP server exposed as `jss-lint lsp` (stdio transport; `--socket PORT` for TCP). The server speaks LSP 3.17 and supports: `initialize`, `initialized`, `shutdown`, `exit`, `textDocument/didOpen`, `textDocument/didChange` (debounced 200 ms), `textDocument/didSave`, `textDocument/didClose`, `textDocument/publishDiagnostics`, `textDocument/codeAction` (one CodeAction per `Fix` from spec 008), and `workspace/executeCommand` for \"apply all fixes\". Diagnostics use the SARIF severity mapping from spec 006. Per-document AST cache so re-lint on character-level edits doesn't re-parse from scratch when the change is local. The daemon respects the project's `.jss-lint.toml` and watches it for changes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Author sees inline squiggles in their editor (Priority: P1)

A JSS author edits `manuscript.tex` in an LSP-aware editor. As they
type, the editor shows red/yellow squiggles under each violation.
Hovering shows the rule id, the violation message, and the JSS-
guide section (from spec 007). Saving the file refreshes the
squiggles within ~500 ms.

**Why this priority**: P1 because real-time editor integration is
the core value of an LSP. Without inline diagnostics, the LSP is
no improvement over running `jss-lint` in a terminal.

**Independent Test**: A test client connects to `jss-lint lsp`,
sends `initialize` + `textDocument/didOpen` for a fixture with one
known violation, and asserts that
`textDocument/publishDiagnostics` arrives with exactly one
`Diagnostic` matching the violation.

**Acceptance Scenarios**:

1. **Given** the server is running and a client opens
   `manuscript.tex` (one known violation), **When** the open
   notification arrives, **Then** the server publishes one
   `Diagnostic` with `range`, `severity` (per SARIF mapping),
   `code` (rule id), `message`, and `codeDescription.href`
   (`Rule.guide_url`).
2. **Given** the client hovers over the diagnostic line, **When**
   the editor displays the diagnostic tooltip, **Then** the
   tooltip contains the rule message and links to
   `Rule.guide_url`.
3. **Given** the client edits the file (typing into the buffer),
   **When** 200 ms pass without further edits, **Then** the
   server re-lints and publishes refreshed diagnostics.

---

### User Story 2 - Click-to-fix code actions (Priority: P1)

The author hovers over a squiggle for a rule that ships a `Fix`
(from spec 008). The editor's "Quick Fix" menu shows a code
action ("Wrap MASS in `\pkg{}`"). The author clicks it; the edit
applies; the squiggle disappears.

**Why this priority**: P1 because LSP code actions are how editor
users consume auto-fix. Without this story, spec 008's `Fix`
payload is invisible inside the editor.

**Independent Test**: A test client requests
`textDocument/codeAction` for the diagnostic range and asserts
that the response contains a `CodeAction` whose `edit` is the
LSP `WorkspaceEdit` representation of the violation's `Fix`.

**Acceptance Scenarios**:

1. **Given** a violation whose `Violation.fix is not None`,
   **When** the client requests `textDocument/codeAction` for
   the diagnostic's range, **Then** the response contains a
   `CodeAction` of kind `quickfix` with title `Fix.description`
   and an `edit` that maps to the `Fix` byte range.
2. **Given** a violation whose `Violation.fix is None`, **When**
   the client requests code actions, **Then** the response is
   an empty list (no actions).
3. **Given** the client applies the code action, **When** the
   server receives the resulting `textDocument/didChange`,
   **Then** it re-lints and publishes refreshed diagnostics; the
   fixed violation is gone.

---

### User Story 3 - Apply-all-fixes via workspace command (Priority: P2)

The author runs the editor's "Run command" panel and selects
`jss-lint: Apply all fixes`. The server applies every safe-
confidence `Fix` in the open document(s) and the editor updates
all buffers in one transaction.

**Why this priority**: P2 because the per-fix code action covers
most cases; bulk-apply is an accelerator for cleanup sessions.
Important enough to ship in this spec; not gating because
authors can use the CLI's `--fix` for the same effect.

**Independent Test**: A test client sends `workspace/
executeCommand` with `{command: "jss-lint.applyAllFixes"}` and
asserts that the server returns a `WorkspaceEdit` covering every
fixable violation across the open documents.

**Acceptance Scenarios**:

1. **Given** an open buffer with three fixable violations,
   **When** the client invokes the apply-all command, **Then**
   the server returns a `WorkspaceEdit` with three `TextEdit`
   entries.
2. **Given** an open buffer with no fixable violations, **When**
   the client invokes the apply-all command, **Then** the
   server returns an empty `WorkspaceEdit` (no edits) and a
   notification message confirming "no fixes to apply".

---

### User Story 4 - Watch and react to `.jss-lint.toml` changes (Priority: P2)

The author edits `.jss-lint.toml` (e.g., adds a rule to
`ignore_rules`). The server detects the change, re-loads the
config, re-lints all open documents, and publishes refreshed
diagnostics. The author does not have to restart their editor.

**Why this priority**: P2 because the LSP daemon is long-lived;
restarting it on every config edit would surprise authors.

**Independent Test**: A test client opens a file with one
violation, modifies a fixture `.jss-lint.toml` to suppress the
rule, and asserts that the next
`textDocument/publishDiagnostics` arrives with the diagnostic
removed.

**Acceptance Scenarios**:

1. **Given** the server is running with an empty `.jss-lint.toml`,
   **When** the file is edited to add the violating rule to
   `ignore_rules`, **Then** the server re-lints and publishes
   diagnostics with the now-suppressed rule absent.
2. **Given** the file is edited to a malformed TOML, **When**
   the server re-loads, **Then** it logs a parse error to its
   `window/logMessage` channel and continues using the previous
   valid config.

---

### User Story 5 - Performance — cached AST on incremental edits (Priority: P2)

The author types a single character into a 5,000-line manuscript.
The server re-lints in <50 ms because it reuses the cached AST
from before the edit, only re-parsing the affected region.

**Why this priority**: P2 because perceived responsiveness is
what makes the LSP feel like part of the editor. Slow re-parse
on every keystroke is the failure mode that causes authors to
disable the LSP.

**Independent Test**: A test client measures the round-trip time
for a single-character `textDocument/didChange` against a 5,000-
line fixture. The 95th-percentile latency is below 100 ms across
20 trials.

**Acceptance Scenarios**:

1. **Given** an open 5,000-line buffer with a populated AST cache,
   **When** the client sends a single-character
   `textDocument/didChange`, **Then** the next
   `textDocument/publishDiagnostics` arrives within 100 ms.
2. **Given** the client closes the file
   (`textDocument/didClose`), **When** the close notification
   arrives, **Then** the server evicts the AST cache for that
   file (verified by next-open round-trip latency, which now
   includes a cold parse).

---

### Edge Cases

- A `textDocument/didChange` arrives during the 200 ms debounce
  window: cancel the pending lint, restart the timer.
- A file path includes characters needing percent-encoding:
  `DocumentUri` round-trips correctly via `urllib.parse`.
- A non-`.tex` / `.Rnw` / `.Rmd` file is opened: the server logs
  `unsupported file: <ext>` and silently does nothing — does
  not raise.
- The client requests `textDocument/codeAction` for a range
  with multiple diagnostics: one `CodeAction` per diagnostic
  whose `Fix is not None`.
- The server's stdio is closed by the client without a
  `shutdown` request: the server exits cleanly within 1 second.
- A very large file (>1 MB): full re-parse on every change (no
  partial-reparse optimisation in this spec; see research §4).
  The server's debounce timer is the only mitigation.
- The client sends `workspace/executeCommand` with an unknown
  command id: the server returns LSP error
  `MethodNotFound`.
- Multi-root workspaces: only the first workspace folder is
  watched for `.jss-lint.toml` (per Clarifications §2).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new subcommand `jss-lint lsp` MUST be added that
  starts the LSP server. Default transport: stdio. Optional
  flag: `--socket PORT` for TCP transport (used by tests and by
  some editors).
- **FR-002**: The server MUST speak LSP 3.17 and respond to:
  `initialize`, `initialized`, `shutdown`, `exit`,
  `textDocument/didOpen`, `textDocument/didChange`,
  `textDocument/didSave`, `textDocument/didClose`,
  `textDocument/codeAction`, `workspace/executeCommand`.
- **FR-003**: For every supported file (`.tex`, `.Rnw`, `.Rmd`)
  the server MUST publish `textDocument/publishDiagnostics`
  on open, on save, and on every settled
  `textDocument/didChange`.
- **FR-004**: `textDocument/didChange` MUST be debounced 200 ms.
  An edit within the debounce window cancels the pending lint
  and restarts the timer; only one lint pass fires per
  settled-edit window.
- **FR-005**: Diagnostic severity MUST follow the SARIF severity
  mapping from spec 006: `Severity.ERROR` → LSP severity 1
  (Error), `Severity.WARNING` → 2 (Warning), `Severity.INFO` →
  3 (Information).
- **FR-006**: Each `Diagnostic` MUST carry: `range` (1-based
  line / column converted to LSP 0-based), `severity`, `code`
  (the rule id), `source` (`"jss-lint"`), `message`, and
  `codeDescription.href` (`Rule.guide_url` when non-`None`).
- **FR-007**: `textDocument/codeAction` MUST return one
  `CodeAction` per diagnostic whose `Violation.fix is not None`.
  The action is `kind = "quickfix"`, `title =
  Fix.description`, `edit = WorkspaceEdit(...)` derived from
  the `Fix` byte range and replacement.
- **FR-008**: `workspace/executeCommand` MUST register the
  command id `jss-lint.applyAllFixes`. Invocation returns a
  `WorkspaceEdit` covering every safe-confidence `Fix` across
  the currently-open buffers; review-confidence fixes are
  excluded from this command (the user can still apply them
  individually via per-fix code actions).
- **FR-009**: A per-document AST cache MUST be maintained.
  `textDocument/didOpen` populates the cache; `didClose` evicts
  it; `didChange` invalidates and re-populates. Spec-005 Rmd
  / Rnw documents MUST cache the same way as `.tex`.
- **FR-010**: The server MUST detect changes to the project's
  `.jss-lint.toml` (via the LSP `workspace/didChangeWatchedFiles`
  registration) and re-load the config. Re-load triggers a
  re-lint of every open document.
- **FR-011**: When the config file is malformed, the server
  MUST log a `window/logMessage` (severity Error) and continue
  with the previously-valid config. The server MUST NOT crash.
- **FR-012**: Multi-root workspaces: the server uses the FIRST
  workspace folder (sorted by URI) as the config root. Other
  folders inherit the same config. Multi-root with per-folder
  config is out of scope (Clarifications §2).
- **FR-013**: Very-large files (>1 MB): the server still
  re-parses fully on each settled edit. There is no partial-
  reparse optimisation in this spec; the debounce + cache
  strategy is sufficient for typical JSS manuscripts.
- **FR-014**: An unsupported file (extension not in the
  supported set) MUST be silently ignored: the server logs an
  info message and publishes zero diagnostics. No error
  response is sent.
- **FR-015**: The server MUST be installable as an optional
  extra: `pip install "jss-lint[lsp]"`. Users without the
  extra MAY invoke `jss-lint lsp` and receive a stderr error
  `LSP support not installed; install with pip install
  "jss-lint[lsp]"`.

### Key Entities

- **DocumentCache entry**: `(uri, parsed_document, version,
  config_hash)`. Keyed by `DocumentUri`. Invalidated on
  `didChange` or on config reload.
- **Diagnostic**: LSP 3.17 `Diagnostic` projected from a
  `Violation`.
- **CodeAction**: LSP 3.17 `CodeAction` projected from a
  `Violation` whose `fix is not None`.
- **WorkspaceEdit**: LSP 3.17 `WorkspaceEdit` aggregating one
  or more `TextEdit` entries derived from `Fix` byte ranges.
- **Server lifecycle**: `initialize` → ready (lint open
  documents) → idle (handle notifications) → `shutdown` →
  `exit`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a 5,000-line fixture, the 95th-percentile
  round-trip latency for a single-character
  `textDocument/didChange` is below 100 ms across 20 trials
  on the test machine.
- **SC-002**: Diagnostics published by the LSP server are
  byte-equivalent (after LSP-side coordinate conversion) to
  the SARIF results produced by `jss-lint --output sarif` on
  the same input.
- **SC-003**: The pre-spec-011 CLI behaviour is unchanged.
  The new subcommand is opt-in.
- **SC-004**: A malformed `.jss-lint.toml` does not crash the
  server. The next valid edit recovers full functionality.
- **SC-005**: `textDocument/codeAction` produces one
  `CodeAction` per `Violation.fix` AND zero
  `CodeAction`s when `Violation.fix is None`. Verified for
  every rule in the catalogue that ships a fix in spec 008.
- **SC-006**: The `[lsp]` extra adds at most one new
  third-party runtime dep (`pygls`); core users without the
  extra do not download the LSP libraries.

## Assumptions

- LSP 3.17 is the version every supported editor implements
  (VS Code, Neovim, Helix, Zed, Emacs `lsp-mode`). LSP 3.18
  may add features but is not required for spec 011.
- The LSP server runs as a child process of the editor; the
  editor manages startup and shutdown. No daemon mode in
  this spec.
- A single client connects at a time. The server does not
  support multiplexing across multiple editors. (Each editor
  spawns its own server child.)
- The server reuses the existing engine's `parse_document` /
  `run` functions; no new parsing or lint logic is added in
  this spec.
- The LSP cache is per-process — when the server restarts,
  the cache is empty.
- `pygls.test` (or equivalent) is the test driver; we do not
  hand-roll the LSP test client.
- The 200 ms debounce is empirical: a typing speed of ~5
  chars/sec yields one settled lint per word, which feels
  responsive without thrashing the parser.
