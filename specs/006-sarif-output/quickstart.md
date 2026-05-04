# Quickstart: Adding to or Modifying the SARIF Renderer

**Audience**: contributors editing `src/texlint/output/sarif.py` or
its test fixtures.

This is a how-to, not a reference. For the SARIF projection
contract see [data-model.md](data-model.md); for the schema-level
invariants see [contracts/sarif-output.md](contracts/sarif-output.md).

## Prerequisites

You have:
- Python ≥3.10 with the dev extras installed (`pip install -e
  ".[dev]"`); this brings in `pytest`, `pytest-cov`, and
  `jsonschema`.
- The repo at HEAD on the spec-006 branch (or post-merge `main`).

## Where things live

```text
src/texlint/output/sarif.py                    # the renderer
tests/unit/output/test_sarif.py                # the tests
tests/fixtures/sarif-2.1.0-schema.json         # vendored schema
tests/fixtures/sarif/golden_*.sarif            # 4 golden artefacts
specs/006-sarif-output/                         # spec + plan + research
specs/001-linter-foundation/contracts/cli.md   # cross-spec note
```

## Run the SARIF tests in isolation

```sh
pytest tests/unit/output/test_sarif.py -v
```

Every test in this file should pass on a clean checkout. If one
fails, the most likely culprits — in order — are:

1. **A field renamed in `texlint.api`** (e.g., `Violation.column`
   → `Violation.col`). Fix: update the projection in
   `output/sarif.py` and regenerate the goldens (see below).
2. **A new rule landed in `_catalogue_data.RULES`**. The
   `tool.driver.rules` array grew, so every golden is stale. Fix:
   regenerate the goldens.
3. **A schema-validation error**. The renderer is producing
   structurally-wrong SARIF. Read the validator's diagnostic; it
   names the offending field path.

## Try it manually

```sh
# Clean run
jss-lint --output sarif tests/fixtures/clean/minimal.tex \
  | python -m json.tool > /tmp/out.sarif

# With a custom source root
jss-lint --output sarif --source-root tests/fixtures/clean \
  tests/fixtures/clean/minimal.tex > /tmp/out.sarif
```

Validate against the vendored schema:

```sh
python -c '
import json, sys
from jsonschema import Draft202012Validator
schema = json.load(open("tests/fixtures/sarif-2.1.0-schema.json"))
doc = json.load(open("/tmp/out.sarif"))
Draft202012Validator(schema).validate(doc)
print("ok")
'
```

## Regenerate golden fixtures

When you intentionally change the output (e.g., adding a new field,
changing severity mapping), regenerate every golden:

```sh
# 1. Run the renderer for each fixture scenario
python -m texlint.output.sarif_regen tests/fixtures/sarif/

# 2. Inspect the diff
git diff tests/fixtures/sarif/

# 3. Run the tests to confirm goldens are now byte-equal
pytest tests/unit/output/test_sarif.py
```

`sarif_regen` is a small developer utility; it is not part of the
shipped CLI and not on `PATH`. If you do not see it, your branch is
behind the spec-006 implementation.

## Add a new golden scenario

1. Create the source fixture under `tests/fixtures/sarif/` — a
   `.tex` file that triggers the desired report shape.
2. Add a parametrize entry in `test_sarif.py` mapping the source
   fixture to a new `golden_<name>.sarif` path.
3. Run the regenerator. Inspect the new golden by hand before
   committing.
4. Add a comment in `data-model.md` §4 documenting the scenario.

## Schema fixture updates

The vendored schema is at
`tests/fixtures/sarif-2.1.0-schema.json`. Update it only when the
upstream OASIS schema is revised. The procedure:

1. Fetch the latest 2.1.0 schema from the
   `https://json.schemastore.org/sarif-2.1.0.json` endpoint.
2. Verify the `$id` and `$schema` declarations are unchanged
   (we are not bumping to 2.x or 3.x).
3. Replace the file in a single commit with a message explaining
   the upstream change.
4. Run the full SARIF test suite — if any golden now fails schema
   validation, the upstream schema tightened a constraint and a
   golden update is needed.

## Common pitfalls

- **Sorting**: `json.dumps(..., sort_keys=True)` sorts keys
  alphabetically *within each object*. SARIF arrays (e.g.,
  `results[]`, `rules[]`) are NOT sorted by `sort_keys`; we sort
  them deterministically before serialisation. If you add a new
  array, sort it explicitly in the renderer.
- **Path separators**: never use `str(path)`. Always
  `Path(...).as_posix()` or the `_relativise` helper.
- **Versions**: `tool.driver.version` reads from
  `texlint.__version__`. Do not hardcode it in fixtures — the
  golden files contain it, and it is updated whenever
  `__version__` bumps. The regenerator handles this.
- **`fixes[]`**: do NOT add this in spec 006; it is owned by
  spec 008. Adding it here will make spec 008 redo the golden
  fixtures.
- **`runs[].invocations[].endTimeUtc`**: do NOT emit it. Times
  break determinism (Constitution §I).

## Where to extend

- **Adding a SARIF field that depends on existing data**: edit
  `output/sarif.py` and regenerate goldens.
- **Adding a SARIF field that needs new public data**: extend
  `texlint.api` first (e.g., a new `Violation` field), then the
  renderer. Keep the spec-001 contract document in sync.
- **Adding a new output format**: do NOT extend
  `output/sarif.py`. Mirror the layout — add `output/<name>.py`
  with `render(report, cfg)` and a new branch in
  `cli.py::_dispatch_renderer`.
