"""Spec 011 — config_watch unit tests."""

from __future__ import annotations

from pathlib import Path

from texlint.lsp.config_watch import ConfigState, reload


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
