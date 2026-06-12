"""Load ``ToolConfig`` by merging built-in defaults, ``.jss-lint.toml``, and CLI flags.

Precedence, lowest to highest:
  1. ``ToolConfig()`` defaults
  2. keys present in ``.jss-lint.toml`` in the current working directory
  3. CLI overrides the user actually set

A CLI flag the user did not set (absent key in ``cli_overrides``) does not
override a file value. Unknown TOML keys are silently tolerated; if the
resulting config has ``verbose=True``, a one-line warning is emitted on stderr.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path
from typing import Any

from collections.abc import Mapping

from texlint.api import Severity, ToolConfig

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - covered on 3.10 only
    import tomli as tomllib

_CONFIG_FILENAME = ".jss-lint.toml"


def _normalise_ignore_rules(value: Any) -> frozenset[str]:
    if isinstance(value, frozenset):
        return value
    if isinstance(value, str):
        parts = [p.strip() for p in value.split(",") if p.strip()]
        return frozenset(parts)
    if isinstance(value, (list, tuple, set)):
        return frozenset(str(v).strip() for v in value if str(v).strip())
    return frozenset()


def _normalise_severity_overrides(value: Any) -> dict[str, Severity]:
    """Coerce a ``{rule_id: "error"|"warning"|"info"}`` mapping into
    ``{rule_id: Severity}``. Rule ids are upper-cased; entries with an
    invalid severity value are dropped (the rule keeps its catalogue
    severity rather than failing the whole config)."""
    if not isinstance(value, Mapping):
        return {}
    out: dict[str, Severity] = {}
    for rule_id, sev in value.items():
        try:
            out[str(rule_id).strip().upper()] = Severity(str(sev).lower())
        except ValueError:
            continue
    return out


def _read_toml(cwd: Path) -> dict[str, Any]:
    path = cwd / _CONFIG_FILENAME
    if not path.is_file():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load(cli_overrides: dict[str, Any], cwd: Path) -> ToolConfig:
    known_fields = {f.name for f in dataclasses.fields(ToolConfig)}

    merged: dict[str, Any] = {}
    file_data = _read_toml(cwd)
    unknown_keys = sorted(set(file_data) - known_fields)
    for key in known_fields:
        if key in file_data:
            merged[key] = file_data[key]

    for key, value in cli_overrides.items():
        if value is None:
            continue
        if key in known_fields:
            merged[key] = value

    if "ignore_rules" in merged:
        merged["ignore_rules"] = _normalise_ignore_rules(merged["ignore_rules"])

    if "severity_overrides" in merged:
        merged["severity_overrides"] = _normalise_severity_overrides(
            merged["severity_overrides"]
        )

    cfg = ToolConfig(**merged)

    if unknown_keys and cfg.verbose:
        print(
            f"warning: {_CONFIG_FILENAME} has unrecognised keys: {', '.join(unknown_keys)}",
            file=sys.stderr,
        )
    return cfg
