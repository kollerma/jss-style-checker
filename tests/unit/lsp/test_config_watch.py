"""Spec 011 — config_watch unit tests."""

from __future__ import annotations

from pathlib import Path

from texlint.api import Severity, ToolConfig
from texlint.lsp.config_watch import (
    ConfigState,
    merge_client_settings,
    reload,
)


class TestReload:
    def test_valid_config_loads(self, tmp_path: Path) -> None:
        cfg_path = tmp_path / ".jss-lint.toml"
        cfg_path.write_text(
            'journal = "jss"\n'
            'mode = "reviewer"\n'
            'output = "json"\n',
            encoding="utf-8",
        )
        state = ConfigState()
        logs: list[str] = []
        ok = reload(state, cfg_path, logs.append)
        assert ok is True
        assert state.path == cfg_path
        assert state.cfg.mode == "reviewer"
        assert state.cfg.output == "json"
        assert state.last_error is None
        assert logs == []

    def test_malformed_keeps_previous(self, tmp_path: Path) -> None:
        cfg_path = tmp_path / ".jss-lint.toml"
        cfg_path.write_text("this is = not = valid TOML  ! ! !", encoding="utf-8")
        state = ConfigState()
        prior_cfg = state.cfg
        logs: list[str] = []
        ok = reload(state, cfg_path, logs.append)
        assert ok is False
        assert state.cfg is prior_cfg  # unchanged
        assert state.last_error is not None
        assert len(logs) == 1

    def test_missing_file_keeps_previous(self, tmp_path: Path) -> None:
        state = ConfigState()
        logs: list[str] = []
        ok = reload(state, tmp_path / "no-such.toml", logs.append)
        assert ok is False
        # Default ToolConfig still in place.
        assert state.cfg is not None
        assert state.last_error is not None


class TestMergeClientSettings:
    """Client (VS Code) settings layer additively over .jss-lint.toml."""

    def test_empty_settings_returns_cfg_unchanged(self):
        cfg = ToolConfig()
        assert merge_client_settings(cfg, {}) is cfg

    def test_ignore_rules_union(self):
        cfg = ToolConfig(ignore_rules=frozenset({"JSS-A-001"}))
        out = merge_client_settings(cfg, {"ignoreRules": ["JSS-B-002"]})
        assert out.ignore_rules == frozenset({"JSS-A-001", "JSS-B-002"})

    def test_severity_overrides_client_wins_per_rule(self):
        cfg = ToolConfig(
            severity_overrides={
                "JSS-A-001": Severity.WARNING,
                "JSS-B-002": Severity.ERROR,
            }
        )
        out = merge_client_settings(
            cfg, {"severityOverrides": {"JSS-B-002": "info"}}
        )
        assert out.severity_overrides == {
            "JSS-A-001": Severity.WARNING,
            "JSS-B-002": Severity.INFO,
        }

    def test_code_width_replaces(self):
        out = merge_client_settings(ToolConfig(), {"codeWidth": 100})
        assert out.code_width == 100

    def test_invalid_code_width_ignored(self):
        out = merge_client_settings(ToolConfig(), {"codeWidth": -5})
        assert out.code_width == 80

    def test_run_on_not_a_config_field(self):
        # runOn gates lints on ConfigState, never ToolConfig.
        out = merge_client_settings(ToolConfig(), {"runOn": "save"})
        assert out == ToolConfig()

    def test_state_effective_layers_client(self):
        state = ConfigState()
        state.client_settings = {"ignoreRules": ["JSS-C-003"]}
        assert "JSS-C-003" in state.effective().ignore_rules
        assert state.cfg.ignore_rules == frozenset()
