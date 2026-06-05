"""Spec 011 — LSP server for jss-lint.

Optional surface gated behind ``pip install "jss-lint[lsp]"``. The
server is a thin pygls subclass that wires the existing texlint
engine into the LSP protocol. Heavy lifting:

  * `texlint.lsp.conversions` projects Violation / Fix to LSP
    Diagnostic / CodeAction / WorkspaceEdit shapes.
  * `texlint.lsp.cache` holds per-document parsed views.
  * `texlint.lsp.config_watch` reloads `.jss-lint.toml` on change.

Methods supported (LSP 3.17 spec FR-002):

  * Lifecycle: initialize, initialized, shutdown, exit (lsprotocol
    handles them).
  * Document sync: textDocument/didOpen, didChange, didSave, didClose.
  * Diagnostics: textDocument/publishDiagnostics (server -> client).
  * Code actions: textDocument/codeAction.
  * Workspace: workspace/executeCommand (`jss-lint.applyAllFixes`),
    workspace/didChangeWatchedFiles.

The server is ``deterministic`` per Constitution §I: the
diagnostics it publishes for a given (file content, config) match
the SARIF / CLI output byte-equivalently after coordinate
translation.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from urllib.parse import unquote, urlparse

from lsprotocol import types as lsp
from pygls.lsp.server import LanguageServer

from texlint.api import Fix, ToolConfig
from texlint.core.engine import (
    InvalidJournalError,
    JournalNotFoundError,
    load_journal,
    parse_document,
)
from texlint.core.engine import (
    run as run_engine,
)
from texlint.journals.jss._catalogue_data import RULES as _CATALOGUE
from texlint.journals.jss._guide_index import load_guide_index
from texlint.lsp.cache import CachedDocument, DocumentCache
from texlint.lsp.config_watch import ConfigState
from texlint.lsp.config_watch import reload as reload_config
from texlint.lsp.conversions import (
    fix_to_text_edit,
    violation_to_diagnostic,
)

_DEBOUNCE_MS = 200

logger = logging.getLogger(__name__)


def _uri_to_path(uri: str) -> Path:
    """Convert ``file:///foo/bar.tex`` -> ``Path("/foo/bar.tex")``.

    Tolerates the small handful of URI shapes pygls clients send;
    raises ValueError on a non-``file:`` scheme so the server can
    log + skip rather than crash.
    """
    parsed = urlparse(uri)
    if parsed.scheme not in {"file", ""}:
        raise ValueError(f"unsupported URI scheme: {uri!r}")
    return Path(unquote(parsed.path))


def _guide_url_for(rule_id: str) -> str | None:
    meta = _CATALOGUE.get(rule_id)
    if not meta:
        return None
    url = meta.get("guide_url")
    if url:
        return str(url)
    section = meta.get("guide_section")
    if section:
        idx = load_guide_index()
        return idx.get(section)
    return None


def create_server(
    name: str = "jss-lint", version: str = "0.1.0"
) -> LanguageServer:
    """Build a fully-wired :class:`LanguageServer` instance.

    Factored as a constructor so unit tests can build a fresh
    server without touching module-level state.
    """
    server = LanguageServer(name=name, version=version)
    cache = DocumentCache()
    config_state = ConfigState()
    pending_lints: dict[str, asyncio.TimerHandle] = {}

    # ----- engine helpers ------------------------------------------------- #

    def _lint_uri(uri: str, *, version: int | None, source: str) -> None:
        """Synchronously lint *uri* and publish diagnostics."""
        try:
            path = _uri_to_path(uri)
        except ValueError as exc:
            logger.warning("skipping %s: %s", uri, exc)
            return
        if path.suffix.lower() not in {".tex", ".ltx", ".bib", ".rnw", ".rmd"}:
            logger.info("skipping unsupported file: %s", path)
            return

        # Write the editor's buffer to a temp file? In a stricter
        # implementation we'd parse the in-memory `source`. For
        # spec-011 v1, we delegate to the engine's path-based parser:
        # callers writing to the underlying file before calling this
        # is the typical editor flow. If `source` differs from disk
        # we still re-parse from disk for simplicity.
        path.write_text(source, encoding="utf-8")
        document = parse_document([path])
        cfg = config_state.cfg or ToolConfig()
        try:
            journal = load_journal(cfg.journal)
        except (JournalNotFoundError, InvalidJournalError) as exc:
            logger.error("journal load failed: %s", exc)
            return
        report = run_engine(cfg, document, journal)

        diagnostics: list[lsp.Diagnostic] = []
        for v in report.violations:
            d_dict = violation_to_diagnostic(
                v, guide_url=_guide_url_for(v.rule_id)
            )
            line = d_dict["range"]["start"]["line"]
            col = d_dict["range"]["start"]["character"]
            diagnostics.append(
                lsp.Diagnostic(
                    range=lsp.Range(
                        start=lsp.Position(line=line, character=col),
                        end=lsp.Position(line=line, character=col),
                    ),
                    message=d_dict["message"],
                    severity=lsp.DiagnosticSeverity(d_dict["severity"]),
                    code=d_dict["code"],
                    source=d_dict["source"],
                    code_description=(
                        lsp.CodeDescription(href=d_dict["codeDescription"]["href"])
                        if "codeDescription" in d_dict
                        else None
                    ),
                )
            )

        cache.put(
            CachedDocument(
                uri=uri,
                version=version or 0,
                parsed=document,
                diagnostics=tuple(report.violations),
            )
        )
        server.text_document_publish_diagnostics(
            lsp.PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics)
        )

    def _schedule_lint(uri: str, version: int | None, source: str) -> None:
        """Debounce: cancel any pending lint for *uri*, schedule a new
        one ``_DEBOUNCE_MS`` from now."""
        loop = asyncio.get_event_loop()
        old = pending_lints.pop(uri, None)
        if old is not None:
            old.cancel()
        pending_lints[uri] = loop.call_later(
            _DEBOUNCE_MS / 1000.0,
            lambda: _lint_uri(uri, version=version, source=source),
        )

    # ----- handlers ------------------------------------------------------- #

    @server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
    def _did_open(params: lsp.DidOpenTextDocumentParams) -> None:
        # Open documents lint immediately (no debounce).
        td = params.text_document
        _lint_uri(td.uri, version=td.version, source=td.text)

    @server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
    def _did_change(params: lsp.DidChangeTextDocumentParams) -> None:
        td = params.text_document
        # `pygls` keeps the in-memory document; pull current text.
        doc = server.workspace.get_text_document(td.uri)
        _schedule_lint(td.uri, td.version, doc.source)

    @server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
    def _did_save(params: lsp.DidSaveTextDocumentParams) -> None:
        td = params.text_document
        doc = server.workspace.get_text_document(td.uri)
        _lint_uri(td.uri, version=getattr(td, "version", None), source=doc.source)

    @server.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
    def _did_close(params: lsp.DidCloseTextDocumentParams) -> None:
        cache.evict(params.text_document.uri)
        # Clear any squiggles on close.
        server.text_document_publish_diagnostics(
            lsp.PublishDiagnosticsParams(uri=params.text_document.uri, diagnostics=[])
        )

    @server.feature(lsp.TEXT_DOCUMENT_CODE_ACTION)
    def _code_action(
        params: lsp.CodeActionParams,
    ) -> list[lsp.CodeAction]:
        entry = cache.get(params.text_document.uri)
        if entry is None:
            return []
        actions: list[lsp.CodeAction] = []
        for v in entry.diagnostics:
            if not isinstance(v.fix, Fix):
                continue
            # Only produce an action if its diagnostic intersects
            # the requested range.
            line = max(v.line - 1, 0)
            req = params.range
            if not (
                req.start.line <= line <= req.end.line
            ):
                continue
            try:
                source = server.workspace.get_text_document(
                    params.text_document.uri
                ).source
            except KeyError:  # pragma: no cover - defensive
                continue
            edit_dict = fix_to_text_edit(v.fix, source)
            text_edit = lsp.TextEdit(
                range=lsp.Range(
                    start=lsp.Position(
                        line=edit_dict["range"]["start"]["line"],
                        character=edit_dict["range"]["start"]["character"],
                    ),
                    end=lsp.Position(
                        line=edit_dict["range"]["end"]["line"],
                        character=edit_dict["range"]["end"]["character"],
                    ),
                ),
                new_text=edit_dict["newText"],
            )
            actions.append(
                lsp.CodeAction(
                    title=v.fix.description,
                    kind=lsp.CodeActionKind.QuickFix,
                    edit=lsp.WorkspaceEdit(
                        changes={params.text_document.uri: [text_edit]}
                    ),
                )
            )
        return actions

    @server.feature(lsp.WORKSPACE_DID_CHANGE_CONFIGURATION)
    def _did_change_configuration(
        params: lsp.DidChangeConfigurationParams,  # noqa: ARG001
    ) -> None:
        # VS Code (and other clients) push a notification whenever the
        # user edits settings. Config reload is wired through the file
        # watcher on `.jss-lint.toml` rather than client-pushed
        # settings, so we accept-and-ignore — without a registered
        # handler pygls logs a noisy warning for every settings save.
        return

    @server.feature(lsp.WORKSPACE_DID_CHANGE_WATCHED_FILES)
    def _config_changed(params: lsp.DidChangeWatchedFilesParams) -> None:
        for change in params.changes:
            try:
                path = _uri_to_path(change.uri)
            except ValueError:
                continue
            if path.name != ".jss-lint.toml":
                continue
            ok = reload_config(
                config_state, path, lambda m: server.window_show_message(
                    lsp.ShowMessageParams(type=lsp.MessageType.Error, message=m)
                ),
            )
            if not ok:
                continue
            # Re-lint every open document.
            for uri in tuple(cache.open_uris()):
                try:
                    doc = server.workspace.get_text_document(uri)
                except KeyError:
                    continue
                _lint_uri(uri, version=doc.version, source=doc.source)

    @server.command("jss-lint.applyAllFixes")
    def _apply_all_fixes(args: list) -> dict | None:  # noqa: ARG001
        """Workspace command: aggregate every safe-confidence Fix
        across the open documents into a single WorkspaceEdit and
        return it for the editor to apply."""
        changes: dict[str, list[lsp.TextEdit]] = {}
        for uri in cache.open_uris():
            entry = cache.get(uri)
            if entry is None:
                continue
            try:
                source = server.workspace.get_text_document(uri).source
            except KeyError:  # pragma: no cover
                continue
            edits: list[lsp.TextEdit] = []
            for v in entry.diagnostics:
                if not isinstance(v.fix, Fix):
                    continue
                if v.fix.confidence != "safe":
                    continue
                e = fix_to_text_edit(v.fix, source)
                edits.append(
                    lsp.TextEdit(
                        range=lsp.Range(
                            start=lsp.Position(
                                line=e["range"]["start"]["line"],
                                character=e["range"]["start"]["character"],
                            ),
                            end=lsp.Position(
                                line=e["range"]["end"]["line"],
                                character=e["range"]["end"]["character"],
                            ),
                        ),
                        new_text=e["newText"],
                    )
                )
            if edits:
                # Reverse-position order (spec 008): apply later
                # offsets first so earlier offsets stay valid.
                edits.sort(
                    key=lambda e: (e.range.start.line, e.range.start.character),
                    reverse=True,
                )
                changes[uri] = edits
        if not changes:
            return None
        # pygls returns the WorkspaceEdit dict for the client.
        we = lsp.WorkspaceEdit(changes=changes)
        # WorkspaceEdit serialises to a dict shape; pygls JSON-encodes.
        return we

    return server


def main() -> None:  # pragma: no cover - CLI entry
    """Console entry point for ``jss-lint lsp``. Spawns the server
    on stdio and blocks until the editor closes the connection."""
    logging.basicConfig(level=logging.WARNING)
    # pygls's json-rpc layer logs WARNING on every cancel notification
    # whose target request has already completed — a race that's
    # routine in interactive editing (the client cancels a stale code-
    # action probe just after the server already responded). Suppress
    # by bumping that logger to ERROR; we still see real errors.
    logging.getLogger("pygls.protocol.json_rpc").setLevel(logging.ERROR)
    server = create_server()
    server.start_io()


if __name__ == "__main__":  # pragma: no cover
    main()
