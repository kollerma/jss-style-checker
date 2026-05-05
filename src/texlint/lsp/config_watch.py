"""Spec 011 — `.jss-lint.toml` watcher for the LSP server.

The server registers a glob watcher for ``.jss-lint.toml`` files
under every workspace folder. When the file changes, this module
re-loads the config and signals "every open document needs to be
re-linted". The actual re-lint dispatch happens in the server.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from texlint.api import ToolConfig
from texlint.config import load as load_config

if sys.version_info >= (3, 11):
    import tomllib  # type: ignore[unused-ignore]
else:  # pragma: no cover - covered only on 3.10
    import tomli as tomllib


@dataclass
class ConfigState:
    """Running cache of the active ``.jss-lint.toml``.

    ``path`` is the file we're watching (or ``None`` when no config
    has been picked up yet). ``cfg`` is the most-recent parsed
    config; on a malformed reload we keep the previous ``cfg`` and
    surface a log message via *log*.
    """

    path: Path | None = None
    cfg: ToolConfig = None  # type: ignore[assignment]
    last_error: str | None = None

    def __post_init__(self) -> None:
        if self.cfg is None:
            self.cfg = ToolConfig()


def reload(state: ConfigState, path: Path, log: Callable[[str], None]) -> bool:
    """Reload the config from *path*. Returns ``True`` when the new
    config replaces the old; ``False`` when the file is malformed
    (the previous config stays active)."""
    try:
        # `load_config` accepts a CWD; we want to read THIS file
        # specifically, so we delegate to its private read by
        # constructing a tomllib.loads directly first.
        text = path.read_text(encoding="utf-8")
        tomllib.loads(text)  # raises on malformed TOML
    except (OSError, tomllib.TOMLDecodeError) as exc:
        state.last_error = f"failed to read {path}: {exc}"
        log(state.last_error)
        return False

    try:
        new_cfg = load_config({}, path.parent)
    except Exception as exc:  # pragma: no cover - load_config is robust
        state.last_error = f"failed to load config at {path}: {exc}"
        log(state.last_error)
        return False

    state.path = path
    state.cfg = new_cfg
    state.last_error = None
    return True
