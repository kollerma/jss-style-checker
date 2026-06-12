"""Integration tests for the spec-006 SARIF 2.1.0 output format."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint import __version__
from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestSarifShape:
    def test_top_level_keys(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert set(payload.keys()) == {"$schema", "runs", "version"}
        assert payload["version"] == "2.1.0"
        assert payload["$schema"] == "https://json.schemastore.org/sarif-2.1.0.json"

    def test_single_run(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                str(FIXTURES / "compliant" / "minimal.tex"),
            ],
        )
        payload = json.loads(result.output)
        assert len(payload["runs"]) == 1

    def test_tool_driver_metadata(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                str(FIXTURES / "compliant" / "minimal.tex"),
            ],
        )
        payload = json.loads(result.output)
        driver = payload["runs"][0]["tool"]["driver"]
        assert driver["name"] == "jss-lint"
        assert driver["version"] == __version__
        assert driver["informationUri"].startswith("https://")
        assert isinstance(driver["rules"], list)
        # Every catalogue rule appears + the synthetic parse rule.
        rule_ids = {r["id"] for r in driver["rules"]}
        assert "JSS-PARSE-000" in rule_ids
        assert "JSS-PRE-001" in rule_ids
        # Rule descriptors are sorted by id ascending.
        ids_in_order = [r["id"] for r in driver["rules"]]
        assert ids_in_order == sorted(ids_in_order)

    def test_rule_descriptor_shape(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                str(FIXTURES / "compliant" / "minimal.tex"),
            ],
        )
        payload = json.loads(result.output)
        for rule in payload["runs"][0]["tool"]["driver"]["rules"]:
            assert set(rule.keys()) >= {
                "id",
                "name",
                "shortDescription",
                "fullDescription",
                "defaultConfiguration",
                "properties",
            }
            assert rule["defaultConfiguration"]["level"] in {"error", "warning", "note"}
            tags = rule["properties"]["tags"]
            assert isinstance(tags, list)
            assert len(tags) == 1


class TestSarifResults:
    def test_clean_run_has_no_results(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        payload = json.loads(result.output)
        run = payload["runs"][0]
        assert run["results"] == []
        assert run["invocations"][0]["toolExecutionNotifications"] == []
        assert run["invocations"][0]["executionSuccessful"] is True

    def test_single_violation_result(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            ],
        )
        assert result.exit_code == 1
        payload = json.loads(result.output)
        run = payload["runs"][0]
        assert run["invocations"][0]["toolExecutionNotifications"] == []
        results = run["results"]
        assert len(results) >= 1
        cite_results = [r for r in results if r["ruleId"] == "JSS-CITE-002"]
        assert len(cite_results) == 1
        r = cite_results[0]
        assert r["level"] in {"error", "warning", "note"}
        assert "text" in r["message"]
        loc = r["locations"][0]["physicalLocation"]
        assert "uri" in loc["artifactLocation"]
        assert loc["region"]["startLine"] >= 1


class TestSarifParseError:
    def test_parse_error_emits_notification_not_result(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                str(FIXTURES / "violations" / "JSS-PARSE-000.bib"),
            ],
        )
        # Per spec FR-008 / contract C-7, parse failures still raise the
        # exit code to 2 even when emitted as a SARIF notification.
        assert result.exit_code == 2
        payload = json.loads(result.output)
        run = payload["runs"][0]
        # Parse failure is a notification, NOT a result.
        notifications = run["invocations"][0]["toolExecutionNotifications"]
        assert len(notifications) == 1
        n = notifications[0]
        assert n["descriptor"]["id"] == "JSS-PARSE-000"
        assert n["level"] == "error"
        assert "text" in n["message"]
        # No JSS-PARSE-000 in results.
        assert all(r["ruleId"] != "JSS-PARSE-000" for r in run["results"])
        # executionSuccessful stays true: parse failure is a finding,
        # not an internal crash.
        assert run["invocations"][0]["executionSuccessful"] is True


class TestSarifDeterminism:
    def test_two_runs_byte_identical(self, runner: CliRunner):
        args = [
            "--output",
            "sarif",
            str(FIXTURES / "compliant" / "minimal.tex"),
            str(FIXTURES / "compliant" / "minimal.bib"),
        ]
        r1 = runner.invoke(main, args)
        r2 = runner.invoke(main, args)
        assert r1.output == r2.output
        # Byte-deterministic stronger than string-equal: also assert same hash.
        assert hashlib.sha256(r1.output.encode()).hexdigest() == hashlib.sha256(
            r2.output.encode()
        ).hexdigest()


class TestSourceRoot:
    def test_default_source_root_is_cwd(self, runner: CliRunner, tmp_path: Path):
        # Copy a fixture into tmp_path/sub so relativisation against CWD
        # produces a non-trivial relative path.
        src = (FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex").read_bytes()
        sub = tmp_path / "sub"
        sub.mkdir()
        target = sub / "manuscript.tex"
        target.write_bytes(src)

        with runner.isolated_filesystem(temp_dir=tmp_path):
            cwd = Path.cwd()
            # cwd is somewhere inside tmp_path; reference target by relative path.
            rel = os.path.relpath(target, cwd)
            result = runner.invoke(main, ["--output", "sarif", rel])
            payload = json.loads(result.output)
            uris = [
                r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
                for r in payload["runs"][0]["results"]
            ]
            for uri in uris:
                assert "\\" not in uri  # POSIX-style
                # No drive letter, no leading "/" except when source-root
                # disagreement forces it (research §3 — should not happen here).
                assert not uri.startswith("/")

    def test_explicit_source_root(self, runner: CliRunner, tmp_path: Path):
        src = (FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex").read_bytes()
        sub = tmp_path / "sub"
        sub.mkdir()
        target = sub / "manuscript.tex"
        target.write_bytes(src)

        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                "--source-root",
                str(sub),
                str(target),
            ],
        )
        payload = json.loads(result.output)
        for r in payload["runs"][0]["results"]:
            uri = r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
            assert uri == "manuscript.tex"


# Top-level imports placed last to avoid disrupting class layout.
import os  # noqa: E402
