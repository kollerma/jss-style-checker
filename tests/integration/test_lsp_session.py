"""Spec 011 integration test — LSP server registration + handler smoke tests.

We don't spawn a pygls client/server pair (pygls 2.x doesn't ship a
synchronous in-process test driver in the way the spec assumed).
Instead we exercise the same handler functions the protocol layer
calls, which is what those handlers do anyway — pygls is a thin
JSON-RPC dispatcher above this layer. Every assertion below
exercises real handler code.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pygls")

from lsprotocol import types as lsp  # noqa: E402

from texlint.lsp.server import _uri_to_path, create_server  # noqa: E402

_FIXTURE_TEX = (
    "\\documentclass[article]{jss}\n"
    "\\title{T}\n"
    "\\author{A}\n"
    "\\Plainauthor{A}\n"
    "\\Abstract{D.}\n"
    "\\Keywords{k}\n"
    "\\Address{Z}\n"
    "\\begin{document}\nBody.\n\\end{document}\n"
)

_FIXTURE_WITH_VIOLATION = (
    "\\documentclass[article]{jss}\n"
    "\\title{T}\n"
    "\\author{A}\n"
    "\\Plainauthor{A}\n"
    "\\Abstract{D.}\n"
    "\\Keywords{k}\n"
    "\\Address{Z}\n"
    "\\begin{document}\n"
    "We use \\pkg{mgcv}.\n"
    "\\end{document}\n"
)


class TestServerRegistration:
    def test_creates_with_documented_features(self) -> None:
        server = create_server()
        names = set(server.protocol.fm.features.keys())
        assert "textDocument/didOpen" in names
        assert "textDocument/didChange" in names
        assert "textDocument/didSave" in names
        assert "textDocument/didClose" in names
        assert "textDocument/codeAction" in names
        assert "workspace/didChangeWatchedFiles" in names

    def test_apply_all_fixes_command_registered(self) -> None:
        server = create_server()
        assert "jss-lint.applyAllFixes" in server.protocol.fm.commands

    def test_server_metadata(self) -> None:
        server = create_server(name="x", version="42")
        assert server.name == "x"
        assert server.version == "42"


class TestUriToPath:
    def test_file_scheme(self) -> None:
        p = _uri_to_path("file:///tmp/foo.tex")
        assert p == Path("/tmp/foo.tex")

    def test_relative_uri_no_scheme(self) -> None:
        # A bare path is treated as the path itself.
        p = _uri_to_path("/tmp/foo.tex")
        assert p == Path("/tmp/foo.tex")

    def test_unsupported_scheme_raises(self) -> None:
        with pytest.raises(ValueError):
            _uri_to_path("untitled:bar.tex")

    def test_url_encoded_path(self) -> None:
        p = _uri_to_path("file:///tmp/foo%20bar.tex")
        assert p == Path("/tmp/foo bar.tex")


class TestDidOpen:
    """Exercise the registered didOpen handler on a real fixture."""

    def test_did_open_publishes_diagnostics(self, tmp_path: Path) -> None:
        server = create_server()
        manuscript = tmp_path / "m.tex"
        manuscript.write_text(_FIXTURE_TEX, encoding="utf-8")
        published: list[lsp.PublishDiagnosticsParams] = []

        def _capture(params: lsp.PublishDiagnosticsParams) -> None:
            published.append(params)

        server.text_document_publish_diagnostics = _capture  # type: ignore[assignment]

        # Look up the handler by feature name and call it directly.
        handler = server.protocol.fm.features["textDocument/didOpen"]
        params = lsp.DidOpenTextDocumentParams(
            text_document=lsp.TextDocumentItem(
                uri=manuscript.as_uri(),
                language_id="latex",
                version=1,
                text=_FIXTURE_TEX,
            )
        )
        handler(params)
        assert len(published) == 1
        assert published[0].uri == manuscript.as_uri()
        # The clean fixture might have a few violations from the
        # default catalogue; the contract here is just that we
        # publish *something* (could be empty).
        assert isinstance(published[0].diagnostics, list)


class TestDidOpenDoesNotTouchDisk:
    """The server lints the in-memory buffer; the file on disk must
    never be written (or even required to exist)."""

    def test_buffer_differs_from_disk_disk_untouched(self, tmp_path: Path) -> None:
        server = create_server()
        manuscript = tmp_path / "m.tex"
        disk_bytes = b"% disk content, deliberately not the buffer\n"
        manuscript.write_bytes(disk_bytes)
        stat_before = manuscript.stat()
        published: list[lsp.PublishDiagnosticsParams] = []
        server.text_document_publish_diagnostics = (  # type: ignore[assignment]
            lambda p: published.append(p)
        )

        handler = server.protocol.fm.features["textDocument/didOpen"]
        handler(
            lsp.DidOpenTextDocumentParams(
                text_document=lsp.TextDocumentItem(
                    uri=manuscript.as_uri(),
                    language_id="latex",
                    version=1,
                    text=_FIXTURE_TEX,  # buffer != disk
                )
            )
        )
        assert len(published) == 1
        assert manuscript.read_bytes() == disk_bytes
        assert manuscript.stat().st_mtime_ns == stat_before.st_mtime_ns

    def test_unsaved_buffer_without_disk_file(self, tmp_path: Path) -> None:
        server = create_server()
        manuscript = tmp_path / "never-saved.tex"  # does not exist
        published: list[lsp.PublishDiagnosticsParams] = []
        server.text_document_publish_diagnostics = (  # type: ignore[assignment]
            lambda p: published.append(p)
        )

        handler = server.protocol.fm.features["textDocument/didOpen"]
        handler(
            lsp.DidOpenTextDocumentParams(
                text_document=lsp.TextDocumentItem(
                    uri=manuscript.as_uri(),
                    language_id="latex",
                    version=1,
                    text=_FIXTURE_TEX,
                )
            )
        )
        assert len(published) == 1
        assert not manuscript.exists()


class TestDidClose:
    def test_did_close_publishes_empty(self, tmp_path: Path) -> None:
        server = create_server()
        published: list[lsp.PublishDiagnosticsParams] = []
        server.text_document_publish_diagnostics = lambda p: published.append(p)  # type: ignore[assignment]

        manuscript = tmp_path / "m.tex"
        uri = manuscript.as_uri()
        handler = server.protocol.fm.features["textDocument/didClose"]
        params = lsp.DidCloseTextDocumentParams(
            text_document=lsp.TextDocumentIdentifier(uri=uri)
        )
        handler(params)
        assert len(published) == 1
        assert published[0].diagnostics == []


class TestCodeAction:
    def test_code_action_empty_when_cache_miss(self) -> None:
        server = create_server()
        handler = server.protocol.fm.features["textDocument/codeAction"]
        params = lsp.CodeActionParams(
            text_document=lsp.TextDocumentIdentifier(uri="file:///nope.tex"),
            range=lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=0),
            ),
            context=lsp.CodeActionContext(diagnostics=[]),
        )
        actions = handler(params)
        assert actions == []


class TestApplyAllFixes:
    """The command must push the aggregated WorkspaceEdit via
    workspace/applyEdit (clients discard executeCommand results) and
    re-lint stale buffers before computing edits."""

    _SRC_WITH_FIX = (
        "\\documentclass[article]{jss}\n"
        "\\title{T}\n"
        "\\author{A}\n"
        "\\Plainauthor{A}\n"
        "\\Abstract{D.}\n"
        "\\Keywords{k}\n"
        "\\Address{Z}\n"
        "\\begin{document}\n"
        "We implement everything in R for speed.\n"
        "\\end{document}\n"
    )

    def _open(self, server, uri: str, text: str, version: int = 1) -> None:
        from pygls.workspace import Workspace

        # Handler-direct tests skip `initialize`; give the protocol a
        # real Workspace so workspace.get_text_document works.
        if server.protocol._workspace is None:
            server.protocol._workspace = Workspace(None)
        item = lsp.TextDocumentItem(
            uri=uri, language_id="latex", version=version, text=text
        )
        server.workspace.put_text_document(item)
        handler = server.protocol.fm.features["textDocument/didOpen"]
        handler(lsp.DidOpenTextDocumentParams(text_document=item))

    def test_sends_workspace_apply_edit(self, tmp_path: Path) -> None:
        server = create_server()
        server.text_document_publish_diagnostics = lambda p: None  # type: ignore[assignment]
        applied: list[lsp.ApplyWorkspaceEditParams] = []
        server.workspace_apply_edit = (  # type: ignore[assignment]
            lambda params: applied.append(params) or None
        )
        manuscript = tmp_path / "m.tex"
        uri = manuscript.as_uri()
        self._open(server, uri, self._SRC_WITH_FIX)

        command = server.protocol.fm.commands["jss-lint.applyAllFixes"]
        summary = command([])

        assert len(applied) == 1
        params = applied[0]
        assert params.label == "jss-lint: Apply all fixes"
        edits = params.edit.changes[uri]
        assert len(edits) >= 1
        assert any(e.new_text == "\\proglang{R}" for e in edits)
        assert summary == {"files": 1, "edits": len(edits)}

    def test_stale_cache_relinted_before_edit(self, tmp_path: Path) -> None:
        from texlint.lsp.cache import CachedDocument

        server = create_server()
        server.text_document_publish_diagnostics = lambda p: None  # type: ignore[assignment]
        applied: list[lsp.ApplyWorkspaceEditParams] = []
        server.workspace_apply_edit = (  # type: ignore[assignment]
            lambda params: applied.append(params) or None
        )
        manuscript = tmp_path / "m.tex"
        uri = manuscript.as_uri()
        self._open(server, uri, self._SRC_WITH_FIX)

        # Make the cache stale: the editor advanced the buffer (the R
        # sentence moved one line down) without a re-lint.
        new_text = self._SRC_WITH_FIX.replace(
            "\\begin{document}\n", "\\begin{document}\nA new first line.\n"
        )
        server.workspace.put_text_document(
            lsp.TextDocumentItem(
                uri=uri, language_id="latex", version=7, text=new_text
            )
        )
        # Cache still holds version-1 diagnostics with version-1 offsets.

        command = server.protocol.fm.commands["jss-lint.applyAllFixes"]
        command([])

        assert len(applied) == 1
        edits = applied[0].edit.changes[uri]
        wrap = next(e for e in edits if e.new_text == "\\proglang{R}")
        # The R now sits on line 9 (0-based) — one lower than at lint
        # time. A stale edit would target line 8.
        assert wrap.range.start.line == 9
        new_lines = new_text.splitlines()
        target = new_lines[wrap.range.start.line]
        assert target[wrap.range.start.character] == "R"

    def test_no_fixes_returns_none_and_sends_nothing(
        self, tmp_path: Path
    ) -> None:
        server = create_server()
        server.text_document_publish_diagnostics = lambda p: None  # type: ignore[assignment]
        applied: list[lsp.ApplyWorkspaceEditParams] = []
        server.workspace_apply_edit = (  # type: ignore[assignment]
            lambda params: applied.append(params) or None
        )
        manuscript = tmp_path / "clean.tex"
        self._open(server, manuscript.as_uri(), _FIXTURE_TEX)

        command = server.protocol.fm.commands["jss-lint.applyAllFixes"]
        assert command([]) is None
        assert applied == []
