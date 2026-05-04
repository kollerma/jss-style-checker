# Research: Language Server (LSP)

**Phase**: 0
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. LSP framework: `pygls` vs. hand-rolled

**Decision**: Use `pygls>=1.3`, gated behind the `[lsp]` extra.

**Rationale**:
- `pygls` is the de-facto Python LSP framework, used by Microsoft
  in `pyright-langserver`'s reference Python ports.
- It handles JSON-RPC framing, lifecycle (`initialize` /
  `shutdown`), capability negotiation, and the request/notification
  dispatch that a hand-rolled implementation would otherwise have
  to reproduce (~1k LOC, plus the test scaffolding for each).
- Constitution §X allows the dep when the alternative is a
  substantial hand-rolled stack. The optional-extra gate keeps
  the core install size unchanged.

**Alternatives considered**:
- Hand-rolled JSON-RPC over stdio: rejected per rationale.
- `lsprotocol`-only (no server framework): rejected — would
  still need lifecycle handling.
- Forking `pygls` into the repo: rejected — supply-chain
  inflation for a library we don't need to fork.

---

## 2. Multi-root workspace handling

**Decision**: First workspace folder (sorted by URI) is the
config root. Other folders inherit the same config. Per-folder
`.jss-lint.toml` is out of scope for v1.

**Rationale**:
- Most editors open one workspace folder at a time when authoring
  a single manuscript.
- Multi-root with per-folder config introduces the question of
  which config wins for a file equally claimed by two folders;
  the answer requires a UX decision we don't have user data for.
- v1 ships the simple model; revisit if a real user has
  per-folder needs.

**Alternatives considered**:
- Refuse multi-root entirely: rejected — would block users with
  more than one folder open.
- Walk up from each open file to find the nearest
  `.jss-lint.toml`: rejected — deferred for v2.

---

## 3. AST cache key

**Decision**: `(DocumentUri, textDocument.version)`.

**Rationale**:
- LSP clients maintain `version` as a monotonic integer per
  document; it changes on every notification that mutates the
  buffer. The protocol guarantees this.
- mtime is unreliable when the editor has unsaved buffer state
  (the file on disk has not changed but the buffer has).
- Content hash is redundant given the version counter and adds
  per-edit cost.

**Alternatives considered**:
- mtime: rejected per rationale.
- Content hash (SHA-1): rejected per rationale.
- `(uri, content)`: rejected — requires hashing on every
  cache check.

---

## 4. Very-large-file strategy

**Decision**: Full reparse on every settled edit. The 200 ms
debounce + per-document cache strategy is sufficient for the
typical JSS manuscript size (~10–200 KB). No partial-reparse
optimisation in this spec.

**Rationale**:
- Partial reparse over pylatexenc would require a tree-diff
  engine; that is a much larger spec.
- The 1 MB threshold mentioned in spec FR-013 is an order of
  magnitude above any real JSS manuscript we have observed in
  the eval corpus.
- If a user reports unacceptable latency, the follow-up spec
  is straightforward: implement a partial-reparse pass and
  hide it behind a feature flag.

**Alternatives considered**:
- Skip files >1 MB: rejected — would silently disable the
  linter on the very documents users care about.
- Partial reparse via tree-diff: rejected — out of scope.
- Preallocate the parser pool: rejected — Constitution §X.

---

## 5. Hover prose surfacing

**Decision**: Each `Diagnostic` carries `codeDescription.href =
Rule.guide_url`. The full explanation prose from spec 009 is
NOT inlined into hover content. Users who want the prose run
`jss-lint explain <rule-id>` in a terminal.

**Rationale**:
- Inlining the full explanation would require also implementing
  `textDocument/hover` for diagnostic ranges, which is a
  separate LSP method with its own handler logic.
- The `codeDescription.href` field is the protocol-canonical
  surface for "click to learn more".
- Users with an internet connection can click the href to see
  the JSS guide directly; users without can run the explain
  CLI.

**Alternatives considered**:
- Implement `textDocument/hover` with the full explanation:
  rejected for v1 per rationale (simpler v1; revisit in a
  follow-up spec).
- Embed the explanation as a `Diagnostic.relatedInformation`
  entry: rejected — abuses the relatedInformation channel,
  which is meant for "see also this other location".

---

## 6. Debounce implementation

**Decision**: A single asyncio task per document URI, cancelled
and rescheduled on each `didChange`.

**Rationale**:
- `pygls` uses an asyncio loop; cancelling a pending task is
  the idiomatic debounce in this model.
- Per-document task isolates the debounce so edits in one file
  do not delay diagnostics in another.

**Alternatives considered**:
- Global single-flight queue: rejected — would serialise
  unrelated documents.
- Threaded timer: rejected — would not integrate cleanly with
  the asyncio loop.

---

## 7. Coordinate translation

**Decision**: Convert internal 1-based line / 1-based column to
LSP's 0-based line / 0-based UTF-16 column. The conversion is
done once per `Diagnostic`.

**Rationale**:
- LSP positions are 0-based; the linter is 1-based.
- LSP positions are nominally UTF-16 code units, but in
  practice every editor we target accepts UTF-8 byte offsets
  (they coincide for ASCII content). We document the
  approximation in the contract; if a user reports a
  multibyte-character offset bug, we tighten.

**Alternatives considered**:
- Convert to true UTF-16 offsets: pulls in an extra encoding
  step per character; deferred until a real user hits the
  issue.
- Adopt 0-based / UTF-16 internally: rejected — would
  cascade through the entire engine and the JSON / SARIF /
  HTML / terminal renderers.

---

## 8. CodeAction semantics

**Decision**: One `CodeAction` per fixable diagnostic, of kind
`quickfix`. The action's `edit` is a `WorkspaceEdit` with one
`TextEdit` derived from the `Fix.start` / `end` / `replacement`.

The `apply-all-fixes` workspace command returns a
`WorkspaceEdit` aggregating ALL safe-confidence `Fix`es across
the open documents (FR-008). Review-confidence fixes are
included only via per-fix code actions.

**Rationale**:
- LSP code actions are the canonical "click to fix" surface.
- Spec 008's `Fix.confidence` distinguishes safe from review;
  the apply-all path takes the conservative subset to match
  the CLI's `--fix-rule`-less default behaviour expectations.

**Alternatives considered**:
- Apply-all takes both confidences: rejected — would surprise
  users when a `review` fix is committed in bulk.
- Single CodeAction per file (one giant edit): rejected —
  would prevent per-fix undo in the editor.

---

## Summary

All eight decisions follow from spec Clarifications and
Constitution §I, §III, §X. No remaining `NEEDS CLARIFICATION`.
Ready for Phase 1.
