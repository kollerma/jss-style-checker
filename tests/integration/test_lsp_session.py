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
