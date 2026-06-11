"""Unit tests for ``texlint.config.load``."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ToolConfig
from texlint.config import load


class TestDefaults:
    def test_no_file_no_cli_returns_defaults(self, tmp_path: Path):
        cfg = load(cli_overrides={}, cwd=tmp_path)
        assert cfg == ToolConfig()

    def test_defaults_match_documented_values(self, tmp_path: Path):
        cfg = load(cli_overrides={}, cwd=tmp_path)
        assert cfg.journal == "jss"
        assert cfg.mode == "author"
        assert cfg.output == "terminal"
        assert cfg.ignore_rules == frozenset()
        assert cfg.verbose is False
        assert cfg.code_width == 80
        # Architecture-review follow-up: confidence floor and exit-code
        # policy default to the historical behaviour (run everything,
        # fail on any violation).
        assert cfg.min_confidence == "low"
        assert cfg.fail_on == "info"

    def test_file_sets_min_confidence_and_fail_on(self, tmp_path: Path):
        (tmp_path / ".jss-lint.toml").write_text(
            'min_confidence = "medium"\nfail_on = "error"\n',
            encoding="utf-8",
        )
        cfg = load(cli_overrides={}, cwd=tmp_path)
        assert cfg.min_confidence == "medium"
        assert cfg.fail_on == "error"


class TestTomlFile:
    def test_file_overlays_defaults(self, tmp_path: Path):
        (tmp_path / ".jss-lint.toml").write_text(
            'mode = "reviewer"\noutput = "json"\ncode_width = 100\n',
            encoding="utf-8",
        )
        cfg = load(cli_overrides={}, cwd=tmp_path)
        assert cfg.mode == "reviewer"
        assert cfg.output == "json"
        assert cfg.code_width == 100
        # Unchanged keys stay on defaults.
        assert cfg.journal == "jss"

    def test_file_ignore_rules_list_becomes_frozenset(self, tmp_path: Path):
        (tmp_path / ".jss-lint.toml").write_text(
            'ignore_rules = ["JSS-A-001", "JSS-B-002"]\n', encoding="utf-8"
        )
        cfg = load(cli_overrides={}, cwd=tmp_path)
        assert cfg.ignore_rules == frozenset({"JSS-A-001", "JSS-B-002"})

    def test_unknown_keys_tolerated_silently(self, tmp_path: Path, capsys):
        (tmp_path / ".jss-lint.toml").write_text(
            'future_key = "future_value"\n', encoding="utf-8"
        )
        cfg = load(cli_overrides={}, cwd=tmp_path)
        # Defaults preserved; no warning on stderr when not verbose.
        assert cfg.journal == "jss"
        err = capsys.readouterr().err
        assert "future_key" not in err

    def test_unknown_keys_warn_when_verbose(self, tmp_path: Path, capsys):
        (tmp_path / ".jss-lint.toml").write_text(
            'future_key = "future_value"\n', encoding="utf-8"
        )
        cfg = load(cli_overrides={"verbose": True}, cwd=tmp_path)
        assert cfg.verbose is True
        err = capsys.readouterr().err
        assert "future_key" in err


class TestCliOverrides:
    def test_cli_wins_over_file(self, tmp_path: Path):
        (tmp_path / ".jss-lint.toml").write_text('mode = "reviewer"\n', encoding="utf-8")
        cfg = load(cli_overrides={"mode": "author"}, cwd=tmp_path)
        assert cfg.mode == "author"

    def test_empty_cli_override_means_file_wins(self, tmp_path: Path):
        (tmp_path / ".jss-lint.toml").write_text('mode = "reviewer"\n', encoding="utf-8")
        cfg = load(cli_overrides={}, cwd=tmp_path)
        assert cfg.mode == "reviewer"

    def test_cli_ignore_rules_csv_becomes_frozenset(self, tmp_path: Path):
        cfg = load(
            cli_overrides={"ignore_rules": "JSS-A-001, JSS-B-002,JSS-C-003"},
            cwd=tmp_path,
        )
        assert cfg.ignore_rules == frozenset({"JSS-A-001", "JSS-B-002", "JSS-C-003"})

    def test_cli_ignore_rules_empty_clears_file_value(self, tmp_path: Path):
        (tmp_path / ".jss-lint.toml").write_text(
            'ignore_rules = ["JSS-A-001"]\n', encoding="utf-8"
        )
        cfg = load(cli_overrides={"ignore_rules": ""}, cwd=tmp_path)
        assert cfg.ignore_rules == frozenset()


class TestFrozen:
    def test_return_value_is_frozen_dataclass(self, tmp_path: Path):
        cfg = load(cli_overrides={}, cwd=tmp_path)
        import dataclasses

        import pytest

        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.journal = "other"  # type: ignore[misc]
