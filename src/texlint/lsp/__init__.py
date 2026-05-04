"""Spec 011 — Language Server Protocol surface for jss-lint.

The wire-protocol server (using pygls) is gated behind the optional
``[lsp]`` extra. This package's :mod:`conversions` module is
pure-Python and importable without the extra; it is the seam any
future LSP server (or other editor host) uses to project texlint's
internal types onto LSP wire shapes.
"""
