"""Spec 011 — `.jss-lint.toml` watcher for the LSP server.

The server registers a glob watcher for ``.jss-lint.toml`` files
under every workspace folder. When the file changes, this module
re-loads the config and signals "every open document needs to be
re-linted". The actual re-lint dispatch happens in the server.
"""

from __future__ import annotations

import dataclasses
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from texlint.api import ToolConfig
from texlint.config import (
    _normalise_ignore_rules,
    _normalise_severity_overrides,
)
from texlint.config import load as load_config

if sys.version_info >= (3, 11):
    import tomllib  # type: ignore[unused-ignore]
else:  # pragma: no cover - covered only on 3.10
    import tomli as tomllib


@dataclass
class ConfigState:
    """Running cache of the active ``.jss-lint.toml`` plus the
    client-pushed (VS Code settings) layer.

    ``path`` is the file we're watching (or ``None`` when no config
    has been picked up yet). ``cfg`` is the most-recent parsed
    config; on a malformed reload we keep the previous ``cfg`` and
    surface a log message via *log*. ``client_settings`` is the raw
    ``jssStyleChecker`` section from the latest
    ``workspace/didChangeConfiguration`` push; ``run_on`` controls
    whether ``didChange`` lints ("change", the default) or only
    ``didSave``/``didOpen`` do ("save").
    """

    path: Path | None = None
    cfg: ToolConfig = None  # type: ignore[assignment]
    last_error: str | None = None
    client_settings: dict[str, Any] = field(default_factory=dict)
    run_on: str = "change"

    def __post_init__(self) -> None:
        if self.cfg is None:
            self.cfg = ToolConfig()

    def effective(self) -> ToolConfig:
        """The config rules actually run with: ``.jss-lint.toml`` as
        the base, client settings layered on top."""
        return merge_client_settings(self.cfg, self.client_settings)


def merge_client_settings(
    cfg: ToolConfig, settings: Mapping[str, Any]
) -> ToolConfig:
    """Layer the client's ``jssStyleChecker`` settings over *cfg*.

    Precedence rules (additive, never wholesale — VS Code pushes its
    defaults for every key on every change, so "client replaces file"
    would silently erase ``.jss-lint.toml`` values):

    * ``ignoreRules`` **unions** into ``ignore_rules``;
    * ``severityOverrides`` **dict-updates** over file overrides
      (client wins per rule id);
    * ``codeWidth`` replaces ``code_width`` (the extension default 80
      equals the tool default, so an unset client is a no-op).

    ``runOn`` is deliberately not a ToolConfig concern — the server
    stores it on :class:`ConfigState` and gates ``didChange`` lints.
    """
    if not settings:
        return cfg
    changes: dict[str, Any] = {}
    if settings.get("ignoreRules"):
        extra = _normalise_ignore_rules(settings["ignoreRules"])
        if extra:
            changes["ignore_rules"] = cfg.ignore_rules | extra
    if settings.get("severityOverrides"):
        client_overrides = _normalise_severity_overrides(
            settings["severityOverrides"]
        )
        if client_overrides:
            changes["severity_overrides"] = {
                **cfg.severity_overrides,
                **client_overrides,
            }
    code_width = settings.get("codeWidth")
    if isinstance(code_width, (int, float)) and int(code_width) > 0:
        changes["code_width"] = int(code_width)
    if not changes:
        return cfg
    return dataclasses.replace(cfg, **changes)


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
