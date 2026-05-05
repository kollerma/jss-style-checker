"""Spec 006 follow-up — byte-deterministic SARIF goldens.

Captures four canonical scenarios from spec 006 (clean run, single
warning, parse error, multi-file) and asserts the renderer's output
is byte-identical to the stored golden after masking volatile
fields.

Volatile fields (masked before comparison):

  * ``runs[0].tool.driver.version`` — bumps on every release;
    masked to ``"<masked>"``.
  * ``runs[0].tool.driver.rules`` — the full rule catalogue grows
    when new rules ship; we mask it to a single placeholder so
    catalogue additions don't churn every golden.

This keeps the goldens focused on the result/notification surface
that consumers (GitHub code-scanning, the diff command) actually
read.

Regenerate via:

    JSSLINT_REGEN_GOLDENS=1 pytest tests/integration/test_cli_sarif_goldens.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
GOLDENS_DIR = FIXTURES / "sarif"

_REGEN = os.environ.get("JSSLINT_REGEN_GOLDENS") == "1"


def _mask_volatile(payload: dict) -> dict:
    """Strip fields that change on every release / catalogue edit."""
    runs = payload.get("runs") or []
    for run in runs:
        driver = ((run.get("tool") or {}).get("driver")) or {}
        if "version" in driver:
            driver["version"] = "<masked>"
        if "rules" in driver:
            # Replace with a tiny placeholder. The structural
            # tests in test_cli_sarif.py already pin the full
            # rules array's shape; goldens here exist to pin
            # results / notifications stability.
            driver["rules"] = [{"_masked": True, "count": len(driver["rules"])}]
    return payload


def _normalised(stdout: str) -> str:
    return json.dumps(_mask_volatile(json.loads(stdout)), indent=2, sort_keys=True) + "\n"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.mark.parametrize(
    ("name", "argv"),
    [
        (
            "clean",
            [
                "--output",
                "sarif",
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        ),
        (
            "single_warning",
            [
                "--output",
                "sarif",
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            ],
        ),
        (
            "parse_error",
            [
                "--output",
                "sarif",
                str(FIXTURES / "violations" / "JSS-PARSE-000.tex"),
            ],
        ),
        (
            "multi_file",
            [
                "--output",
                "sarif",
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            ],
        ),
    ],
)
class TestSarifGoldens:
    def test_byte_equality(
        self,
        runner: CliRunner,
        name: str,
        argv: list[str],
    ) -> None:
        result = runner.invoke(main, argv)
        # All four scenarios use sub-2 exit codes (parse-error => 2).
        assert result.exit_code in {0, 1, 2}, result.output

        normalised = _normalised(result.output)
        golden_path = GOLDENS_DIR / f"golden_{name}.sarif"

        if _REGEN:
            GOLDENS_DIR.mkdir(parents=True, exist_ok=True)
            golden_path.write_text(normalised, encoding="utf-8")
            return

        assert golden_path.exists(), (
            f"Golden missing: {golden_path}. "
            f"Regenerate via JSSLINT_REGEN_GOLDENS=1 pytest"
        )
        expected = golden_path.read_text(encoding="utf-8")
        assert normalised == expected, (
            "SARIF output drifted from golden. "
            f"Regenerate via JSSLINT_REGEN_GOLDENS=1 pytest if intentional."
        )

    def test_double_invocation_is_byte_identical(
        self,
        runner: CliRunner,
        name: str,
        argv: list[str],
    ) -> None:
        """Determinism: two invocations of the same command produce
        the same bytes (Constitution §I)."""
        r1 = runner.invoke(main, argv)
        r2 = runner.invoke(main, argv)
        assert r1.output == r2.output
