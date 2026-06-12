"""Contract tests validating SARIF 2.1.0 output against the official schema.

The renderer at ``src/texlint/output/sarif.py`` emits SARIF 2.1.0 documents.
The structural unit tests in ``test_cli_sarif.py`` cover invariants the
renderer must uphold, but they do not validate the wire format against the
authoritative JSON Schema. This module closes that gap by running the CLI
end-to-end for the four canonical scenarios (clean, single warning, parse
error, multi-file) and asserting each emitted document satisfies the
vendored SARIF 2.1.0 schema.

The schema is vendored under ``tests/fixtures/sarif-2.1.0-schema.json`` so
test runs are reproducible without network access. It is the SchemaStore
copy referenced by the renderer's ``$schema`` URI; that copy is declared
under JSON Schema Draft 7, so we use ``Draft7Validator``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from jsonschema import Draft7Validator

from texlint.cli import main

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures"
SCHEMA_PATH = FIXTURES / "sarif-2.1.0-schema.json"

# Load the schema once at module import — it is ~110 KB and parsing it for
# every parametrized case would dominate the test runtime.
_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

# Sanity-check the schema declares Draft 7. If the vendored copy is ever
# re-fetched and the upstream switches drafts, this assertion will surface
# the change immediately rather than letting the validator silently fall
# back to a different meta-schema.
assert _SCHEMA.get("$schema") == "http://json-schema.org/draft-07/schema#", (
    f"Vendored SARIF schema declares unexpected meta-schema: "
    f"{_SCHEMA.get('$schema')!r}"
)
Draft7Validator.check_schema(_SCHEMA)
_VALIDATOR = Draft7Validator(_SCHEMA)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# Each case is (test id, expected_exit_code, CLI args after `--output sarif`).
SCENARIOS = [
    pytest.param(
        0,
        [
            str(FIXTURES / "compliant" / "minimal.tex"),
            str(FIXTURES / "compliant" / "minimal.bib"),
        ],
        id="clean-run",
    ),
    pytest.param(
        1,
        [str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex")],
        id="single-warning",
    ),
    pytest.param(
        2,
        [str(FIXTURES / "violations" / "JSS-PARSE-000.bib")],
        id="parse-error",
    ),
    pytest.param(
        1,
        [
            str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            str(FIXTURES / "violations" / "citations" / "JSS-CITE-003-bad.tex"),
        ],
        id="multi-file",
    ),
]


@pytest.mark.parametrize("expected_exit, paths", SCENARIOS)
def test_sarif_output_matches_schema(
    runner: CliRunner, expected_exit: int, paths: list[str]
) -> None:
    """The CLI's SARIF output must validate against the vendored schema.

    ``validator.validate(doc)`` raises ``jsonschema.ValidationError`` on
    the first violation, which fails the test with the offending path
    and message in the traceback — that is the desired contract.
    """
    result = runner.invoke(main, ["--output", "sarif", *paths])
    assert result.exit_code == expected_exit, result.output

    document = json.loads(result.output)

    # Collect every error so a future regression surfaces all problems at
    # once rather than only the first. ``validate()`` would short-circuit.
    errors = sorted(_VALIDATOR.iter_errors(document), key=lambda e: list(e.absolute_path))
    if errors:
        formatted = "\n".join(
            f"  - {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in errors
        )
        pytest.fail(
            f"SARIF document failed schema validation ({len(errors)} error(s)):\n"
            f"{formatted}"
        )
